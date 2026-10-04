import asyncio
import re
from typing import Dict, Any, Tuple, Optional
from app.api.tolom import TolomClient
from app.api.customs import CustomsClient
from app.api.autopartner import AutopartnerClient
from app.api.korea_cars import KoreaCarsClient

class CarCheckAggregator:
    def __init__(self):
        self.tolom = TolomClient()
        self.customs = CustomsClient()
        self.autopartner = AutopartnerClient()
        self.korea = KoreaCarsClient()

    def parse_tokens(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Извлекает VIN и/или Госномер из произвольной строки пользователя.
        Поддерживает форматы:
        - "01KG555ADF 1FTEW1E55KFB29513"
        - "1FTEW1E55KFB29513 01KG555ADF"
        - "01 KG 555 ADF 1FTEW1E55KFB29513"
        - "01 KG 555 ADF"
        - "01KG555ADF"
        - "1FTEW1E55KFB29513"
        """
        raw = text.strip()
        if not raw:
            return None, None

        # 1. Поиск 17-значного VIN кода (стандарт ISO 3779: 17 символов кроме I, O, Q)
        vin_match = re.search(r"\b([A-HJ-NPR-Z0-9]{17})\b", raw, re.IGNORECASE)
        found_vin = vin_match.group(1).upper() if vin_match else None

        # Убираем найденный VIN из строки для точного поиска госномера
        remainder = raw
        if found_vin:
            remainder = re.sub(re.escape(found_vin), "", remainder, flags=re.IGNORECASE)

        # Очищаем остаток от знаков препинания
        clean_remainder = re.sub(r"[,\s;/\-_]+", "", remainder).upper()

        found_plate = None
        if clean_remainder:
            # Госномер КР обычно от 4 до 10 символов
            if 3 <= len(clean_remainder) <= 12:
                found_plate = clean_remainder

        # Если VIN не был найден по 17-значному regex, но весь ввод ровно 17 символов
        if not found_vin and len(re.sub(r"[\s\-_]", "", raw)) == 17:
            found_vin = re.sub(r"[\s\-_]", "", raw).upper()
            found_plate = None

        return found_plate, found_vin

    async def check_all(self, raw_input: str, plate: Optional[str] = None, vin: Optional[str] = None) -> Dict[str, Any]:
        """
        Комплексная параллельная проверка по всем 4 базам (Tolom, Customs, Korea-Cars, AutoPartner).
        """
        if not plate and not vin:
            parsed_plate, parsed_vin = self.parse_tokens(raw_input)
            plate = parsed_plate
            vin = parsed_vin
        else:
            if plate: plate = plate.strip().upper().replace(" ", "").replace("-", "")
            if vin: vin = vin.strip().upper().replace(" ", "").replace("-", "")

        result: Dict[str, Any] = {
            "query": raw_input.strip().upper(),
            "plate": plate,
            "vin": vin,
            "tolom": None,
            "customs": None,
            "autopartner": None,
            "korea": None,
            "summary": {
                "car_name": None,
                "year": None,
                "color": None,
                "has_fines": False,
                "fines_count": 0,
                "fines_sum": 0.0,
                "has_arrest": False,
                "customs_cleared": False,
                "auction_found": False,
                "korea_found": False
            }
        }

        tasks = []

        # 1. Если есть госномер -> Tolom.kg
        if plate:
            tasks.append(("tolom", asyncio.create_task(self.tolom.check_plate(plate))))

        # 2. Если есть VIN -> Customs, AutoPartner, Korea-Cars
        if vin:
            tasks.append(("customs", asyncio.create_task(self.customs.check_vin(vin))))
            tasks.append(("autopartner", asyncio.create_task(self.autopartner.check_vin(vin))))
            tasks.append(("korea", asyncio.create_task(self.korea.check_vin(vin))))

        # Выполняем все активные запросы строго параллельно
        for name, task in tasks:
            try:
                res = await task
                result[name] = res
            except Exception as e:
                result[name] = {"success": False, "error": str(e)}

        # Формируем объединенную сводку
        # Из Tolom
        if result["tolom"] and result["tolom"].get("success") and result["tolom"].get("has_car_data"):
            car = result["tolom"].get("car", {})
            result["summary"]["car_name"] = f"{car.get('brand', '')} {car.get('model', '')}".strip()
            result["summary"]["year"] = car.get("year")
            result["summary"]["color"] = car.get("color")
            fines = result["tolom"].get("fines", {})
            result["summary"]["fines_count"] = fines.get("count", 0)
            result["summary"]["fines_sum"] = fines.get("total_sum", 0.0)
            result["summary"]["has_fines"] = fines.get("count", 0) > 0
            result["summary"]["has_arrest"] = result["tolom"].get("has_arrest", False)

        # Из Customs
        if result["customs"] and result["customs"].get("found"):
            c = result["customs"]
            if not result["summary"]["car_name"]:
                result["summary"]["car_name"] = f"{c.get('brand', '')} {c.get('model', '')}".strip()
            if not result["summary"]["year"]:
                result["summary"]["year"] = c.get("year")
            result["summary"]["customs_cleared"] = (c.get("status") == "Оформлена" or "ВЫПУСК РАЗРЕШЕН" in str(c.get("solution", "")))

        # Из Korea
        if result["korea"] and result["korea"].get("found"):
            k = result["korea"]
            if not result["summary"]["car_name"]:
                result["summary"]["car_name"] = k.get("model")
            if not result["summary"]["color"]:
                result["summary"]["color"] = k.get("color")
            result["summary"]["korea_found"] = True

        # Из AutoPartner
        if result["autopartner"] and result["autopartner"].get("found"):
            a = result["autopartner"]
            if not result["summary"]["car_name"]:
                result["summary"]["car_name"] = a.get("title")
            result["summary"]["auction_found"] = True

        return result

aggregator = CarCheckAggregator()

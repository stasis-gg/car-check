import httpx
from typing import Dict, Any, Optional

class TolomClient:
    BASE_URL = "https://tolom.kg/api/v1"

    def __init__(self, timeout: float = 12.0):
        self.timeout = timeout
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Origin": "https://tolom.kg",
            "Referer": "https://tolom.kg/"
        }

    async def check_plate(self, plate: str, is_foreign: bool = False) -> Dict[str, Any]:
        """
        Проверка автомобиля по госномеру на портале Төлөм (tolom.kg).
        Возвращает данные о ТС, штрафах, арестах, периодах владения и тонировке.
        """
        endpoint = "/penalty/by-plate-foreign" if is_foreign else "/penalty/by-plate"
        clean_plate = plate.upper().replace(" ", "").replace("-", "")
        payload = {"plate": clean_plate}

        async with httpx.AsyncClient(timeout=self.timeout, verify=False) as client:
            try:
                resp = await client.post(
                    f"{self.BASE_URL}{endpoint}",
                    json=payload,
                    headers=self.headers
                )
                if resp.status_code == 200:
                    data = resp.json()
                    return self._format_response(clean_plate, data)
                elif resp.status_code == 404:
                    return {
                        "success": False,
                        "plate": clean_plate,
                        "message": "Штрафы и сведения по данному госномеру не найдены"
                    }
                else:
                    return {
                        "success": False,
                        "plate": clean_plate,
                        "message": f"Ошибка сервера Төлөм (код {resp.status_code})"
                    }
            except Exception as e:
                return {
                    "success": False,
                    "plate": clean_plate,
                    "error": str(e),
                    "message": f"Не удалось подключиться к tolom.kg: {e}"
                }

    def _format_response(self, plate: str, raw: Dict[str, Any]) -> Dict[str, Any]:
        current_info = raw.get("currentInfo", {}) or {}
        has_car_info = current_info.get("success", False)
        car_data = current_info.get("data", {}) or {}

        # Штрафы
        total_penalties = raw.get("totalPenalties", 0)
        sum_penalties = raw.get("sumPenalties", 0.0)
        penalties_data = raw.get("penalties", {}) or {}
        penalties_list = []

        if penalties_data.get("success") and penalties_data.get("data"):
            bg_protocols = penalties_data["data"].get("bgProtocols", []) or []
            for p in bg_protocols:
                penalties_list.append({
                    "protocol_number": p.get("protocolNumber"),
                    "article": f"{p.get('article', '')} {p.get('part', '')}".strip(),
                    "title": p.get("violationTitle"),
                    "place": p.get("violationPlace"),
                    "date": p.get("violationDate"),
                    "amount": p.get("fineAmount"),
                    "amount_to_pay": p.get("fineAmountToPay"),
                    "payment_code": p.get("paymentCode"),
                    "discount_days_left": p.get("discountDaysLeft")
                })

        # Тонировка
        tinting_info = raw.get("tintingWidow", {}) or {}
        tinting_text = tinting_info.get("data") if tinting_info.get("success") else "Нет данных"

        # Аресты
        arest_info = raw.get("arestInfo", {}) or {}
        has_arrest = arest_info.get("success", False) and arest_info.get("data") is not None
        arrest_details = arest_info.get("data") if has_arrest else None

        # Периоды владения
        period_info = raw.get("period", {}) or {}
        periods = []
        if period_info.get("success") and period_info.get("data"):
            for item in period_info["data"].get("responseList", []):
                d_from = item.get("dateFrom") or "..."
                d_to = item.get("dateTo") or "наст. время"
                periods.append(f"{d_from} — {d_to}")

        return {
            "success": True,
            "source": "Tolom.kg",
            "plate": plate,
            "has_car_data": has_car_info,
            "car": {
                "brand": car_data.get("brand"),
                "model": car_data.get("model"),
                "type": car_data.get("carTypeName"),
                "year": car_data.get("year"),
                "color": car_data.get("color"),
                "engine_volume": car_data.get("engineVolume"),
                "steering": car_data.get("steering")
            } if has_car_info else None,
            "fines": {
                "count": total_penalties,
                "total_sum": sum_penalties,
                "protocols": penalties_list
            },
            "tinting": tinting_text,
            "has_arrest": has_arrest,
            "arrest_details": arrest_details,
            "ownership_periods": periods,
            "raw": raw
        }

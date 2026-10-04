import httpx
import re
from bs4 import BeautifulSoup
from typing import Dict, Any, List

class KoreaCarsClient:
    BASE_URL = "https://korea-cars.com"

    def __init__(self, timeout: float = 12.0):
        self.timeout = timeout
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7"
        }

    async def check_vin(self, vin: str) -> Dict[str, Any]:
        """
        Проверка автомобиля по реестру Южной Кореи (korea-cars.com).
        Получение данных о вывозе, пробеге при экспорте, цвете, повреждениях и отчете.
        """
        clean_vin = vin.strip().upper()
        url = f"{self.BASE_URL}/{clean_vin}"

        async with httpx.AsyncClient(timeout=self.timeout, verify=False, follow_redirects=True) as client:
            try:
                resp = await client.get(url, headers=self.headers)
                if resp.status_code == 200:
                    html = resp.text
                    return self._parse_korea_page(clean_vin, html, url)
                else:
                    return {
                        "success": False,
                        "found": False,
                        "vin": clean_vin,
                        "message": f"Ошибка сервиса Korea-Cars (код {resp.status_code})"
                    }
            except Exception as e:
                return {
                    "success": False,
                    "found": False,
                    "vin": clean_vin,
                    "error": str(e),
                    "message": f"Не удалось подключиться к korea-cars.com: {e}"
                }

    def _parse_korea_page(self, vin: str, html: str, url: str) -> Dict[str, Any]:
        soup = BeautifulSoup(html, "html.parser")

        carinfo = soup.find(id="carinfo")
        if not carinfo:
            return {
                "success": True,
                "found": False,
                "source": "Korea-Cars (Южная Корея)",
                "vin": vin,
                "message": "Данные в реестре экспорта Кореи не найдены"
            }

        def get_field_text(field_id: str) -> str:
            el = carinfo.find(id=field_id)
            if el:
                val = el.get_text(strip=True)
                return val if val and val != ".." and val != "-" else ""
            return ""

        model = get_field_text("M_TRADEMARK_OF_VEHICLE")
        color = get_field_text("M_COLOR_ENG")
        export_date = get_field_text("M_EXPORT_PERMIT_DATE")
        first_reg_date = get_field_text("M_DATE_OF_FIRST_REGISTRATION")
        mileage = get_field_text("M_FINAL_DRIVE_DISTANCE")
        damage = get_field_text("M_FULL_DAMAGED")
        displacement = get_field_text("M_DISPLACEMENT")
        length = get_field_text("M_LENGTH")
        width = get_field_text("M_WIDTH")
        height = get_field_text("M_HEIGHT")
        capacity = get_field_text("M_RIDING_CAPACITY")

        # Photos
        images: List[str] = []
        for img in carinfo.find_all("img"):
            src = img.get("src") or ""
            if src and not src.endswith(".svg") and not src.endswith(".gif"):
                if src.startswith("//"):
                    src = "https:" + src
                elif src.startswith("/"):
                    src = self.BASE_URL + src
                if src not in images:
                    images.append(src)

        has_data = bool(model or color or (export_date and export_date != "не установлена") or mileage)

        return {
            "success": True,
            "found": has_data,
            "source": "Korea-Cars (Южная Корея)",
            "vin": vin,
            "url": url,
            "model": model or "Не указана",
            "color": color or "Не указан",
            "export_date": export_date or "Не установлена",
            "first_registration_date": first_reg_date or "Не указана",
            "export_mileage": mileage or "Не зафиксирован",
            "damaged": damage if damage else "Нет данных",
            "displacement": displacement or "—",
            "dimensions": f"{length}x{width}x{height}" if (length and width and height) else "—",
            "capacity": capacity or "—",
            "images": images,
            "report_url": f"{self.BASE_URL}/report/{vin}",
            "message": "Данные по корейскому экспорту найдены" if has_data else "Сведения в открытом реестре отсутствуют"
        }

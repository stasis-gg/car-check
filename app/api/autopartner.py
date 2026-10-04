import httpx
import re
from bs4 import BeautifulSoup
from typing import Dict, Any, List

class AutopartnerClient:
    BASE_URL = "https://cars.autopartner.by"

    def __init__(self, timeout: float = 12.0):
        self.timeout = timeout
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7"
        }

    async def check_vin(self, vin: str) -> Dict[str, Any]:
        """
        Поиск автомобиля на аукционной площадке AutoPartner (Copart / IAAI / США / Корея / Европа).
        """
        clean_vin = vin.strip().upper()
        url = f"{self.BASE_URL}/v/{clean_vin}"

        async with httpx.AsyncClient(timeout=self.timeout, verify=False, follow_redirects=True, http2=False) as client:
            try:
                resp = await client.get(url, headers=self.headers)
                if resp.status_code == 200:
                    html = resp.text
                    return self._parse_car_page(clean_vin, html, url)
                elif resp.status_code == 404:
                    return {
                        "success": True,
                        "found": False,
                        "source": "AutoPartner Аукционы (Copart/IAAI)",
                        "vin": clean_vin,
                        "message": "В базе аукционных лотов не найден"
                    }
                else:
                    return {
                        "success": False,
                        "found": False,
                        "vin": clean_vin,
                        "message": f"Ошибка сервиса AutoPartner (код {resp.status_code})"
                    }
            except Exception as e:
                return {
                    "success": False,
                    "found": False,
                    "vin": clean_vin,
                    "error": str(e),
                    "message": f"Не удалось подключиться к autopartner.by: {e}"
                }

    def _parse_car_page(self, vin: str, html: str, url: str) -> Dict[str, Any]:
        soup = BeautifulSoup(html, "html.parser")

        # Заголовок
        title_tag = soup.find("h1") or soup.find("title")
        title = title_tag.get_text(strip=True) if title_tag else f"Автомобиль {vin}"

        # Все изображения высокого разрешения
        images: List[str] = []
        all_found = re.findall(r'https?://[^\s"\'<>]+\.(?:jpg|jpeg|png|webp)', html)
        for src in all_found:
            src_lower = src.lower()
            if any(k in src_lower for k in [vin.lower(), "copart", "iaai", "image.autopartner", "encar"]):
                if not any(x in src_lower for x in ["logo", "favicon", "default.jpg", "og-images", "thumb-"]):
                    if src not in images:
                        images.append(src)

        # Сбор всех характеристик (пробег, повреждения, статус, лот, аукцион, двигатель и т.д.)
        specs: Dict[str, str] = {}
        for row in soup.find_all(class_=re.compile(r'spec|param|detail|info-row|flex.*justify-between|grid', re.I)):
            text = row.get_text(strip=True, separator=" : ")
            if ":" in text and len(text) < 140:
                parts = [p.strip() for p in text.split(":", 1)]
                if len(parts) == 2 and parts[0] and parts[1] and len(parts[0]) < 45:
                    specs[parts[0]] = parts[1]

        # Извлекаем отдельные ключевые параметры
        auction_name = "Copart / IAAI"
        if "copart" in html.lower(): auction_name = "Copart (США)"
        elif "iaai" in html.lower(): auction_name = "IAAI (США)"
        elif "encar" in html.lower(): auction_name = "Encar (Корея)"

        lot_number = specs.get("Номер лота") or specs.get("Лот") or ""
        odometer = specs.get("Пробег") or specs.get("Одометр") or ""
        damage_primary = specs.get("Основное повреждение") or specs.get("Повреждения") or ""
        damage_secondary = specs.get("Вторичное повреждение") or ""
        engine = specs.get("Двигатель") or specs.get("Объем") or ""
        transmission = specs.get("Коробка передач") or specs.get("Трансмиссия") or ""
        drive = specs.get("Привод") or ""
        sale_status = specs.get("Статус продажи") or specs.get("Статус") or ""

        return {
            "success": True,
            "found": True,
            "source": f"Аукцион {auction_name}",
            "auction_name": auction_name,
            "vin": vin,
            "title": title,
            "url": url,
            "lot_number": lot_number,
            "odometer": odometer,
            "damage_primary": damage_primary,
            "damage_secondary": damage_secondary,
            "engine": engine,
            "transmission": transmission,
            "drive": drive,
            "sale_status": sale_status,
            "specs": specs,
            "images": images[:16],
            "message": f"Найден лот на аукционе {auction_name}"
        }

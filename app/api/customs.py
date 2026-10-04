import httpx
from typing import Dict, Any

class CustomsClient:
    BASE_URL = "https://www.customs.gov.kg/site/ru/master/customskg/api/vin-search"

    def __init__(self, timeout: float = 12.0):
        self.timeout = timeout
        self.headers = {
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://www.customs.gov.kg/site/ru/master/customskg/vin-search"
        }

    async def check_vin(self, vin: str) -> Dict[str, Any]:
        """
        Проверка таможенного оформления легкового автомобиля по VIN/номеру кузова
        на портале Государственной таможенной службы Кыргызской Республики.
        """
        clean_vin = vin.strip().upper()
        async with httpx.AsyncClient(timeout=self.timeout, verify=False) as client:
            try:
                resp = await client.get(
                    self.BASE_URL,
                    params={"query": clean_vin},
                    headers=self.headers
                )
                if resp.status_code == 200:
                    data = resp.json()
                    if data.get("found") and data.get("result"):
                        res = data["result"]
                        return {
                            "success": True,
                            "found": True,
                            "source": "Таможенная служба КР (customs.gov.kg)",
                            "vin": clean_vin,
                            "document_type": res.get("documentType"),
                            "issue_date": res.get("issueDate"),
                            "status": res.get("status"),
                            "solution": res.get("solution"),
                            "procedure": res.get("procedure"),
                            "brand": res.get("vehicleBrand"),
                            "model": res.get("vehicleModel"),
                            "year": res.get("modelYear"),
                            "body_num": res.get("bodyNum"),
                            "shassis_num": res.get("shassisNum"),
                            "message": data.get("message", "Оформление найдено")
                        }
                    else:
                        return {
                            "success": True,
                            "found": False,
                            "source": "Таможенная служба КР (customs.gov.kg)",
                            "vin": clean_vin,
                            "message": data.get("message", "Сведения о таможенном оформлении не найдены")
                        }
                else:
                    return {
                        "success": False,
                        "found": False,
                        "vin": clean_vin,
                        "message": f"Ошибка сервера таможни (код {resp.status_code})"
                    }
            except Exception as e:
                return {
                    "success": False,
                    "found": False,
                    "vin": clean_vin,
                    "error": str(e),
                    "message": f"Не удалось подключиться к customs.gov.kg: {e}"
                }

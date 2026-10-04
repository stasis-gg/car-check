import asyncio
import sys
import json

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, ".")
from app.api.aggregator import aggregator

async def test_dual():
    print("Testing simultaneous text input: '01KG555ADF KMHR281ABLU095874'")
    res = await aggregator.check_all("01KG555ADF KMHR281ABLU095874")
    print("Detected Plate:", res.get("plate"))
    print("Detected VIN:", res.get("vin"))
    print("Tolom Car:", res.get("tolom", {}).get("car", {}).get("brand"))
    print("Tolom Fines:", res.get("tolom", {}).get("fines", {}).get("count"))
    print("Customs Solution:", res.get("customs", {}).get("solution"))
    print("Korea Model:", res.get("korea", {}).get("model"))
    print("Summary:", json.dumps(res.get("summary"), ensure_ascii=False, indent=2))

if __name__ == "__main__":
    asyncio.run(test_dual())

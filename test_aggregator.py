import asyncio
import sys
import json

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, ".")
from app.api.aggregator import aggregator

async def test():
    print("Testing VIN query: KMHR281ABLU095874")
    vin_res = await aggregator.check_all("KMHR281ABLU095874")
    print("VIN Summary:", json.dumps(vin_res["summary"], ensure_ascii=False, indent=2))
    print("Customs found:", vin_res.get("customs", {}).get("found"))
    print("Korea found:", vin_res.get("korea", {}).get("found"))
    print("Auction found:", vin_res.get("autopartner", {}).get("found"))

    print("\n" + "="*50 + "\n")
    print("Testing Plate query: 01KG555ADF")
    plate_res = await aggregator.check_all("01KG555ADF")
    print("Plate Summary:", json.dumps(plate_res["summary"], ensure_ascii=False, indent=2))
    print("Fines count:", plate_res.get("tolom", {}).get("fines", {}).get("count"))
    print("Fines sum:", plate_res.get("tolom", {}).get("fines", {}).get("total_sum"))

if __name__ == "__main__":
    asyncio.run(test())

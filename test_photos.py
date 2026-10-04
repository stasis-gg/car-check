import asyncio
import sys
import json

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, ".")

from app.api.aggregator import aggregator

async def test_photos():
    # Test AutoPartner VIN with auction photos:
    vin_auction = "1FTEW1E55KFB29513"
    print(f"Checking VIN with Auction Photos: {vin_auction}")
    res = await aggregator.check_all(vin_auction)
    print("AutoPartner Found:", res.get("autopartner", {}).get("found"))
    print("Car Title:", res.get("autopartner", {}).get("title"))
    print("Images:", res.get("autopartner", {}).get("images"))
    
    # Test Combined: 01KG555ADF (Tolom fines) + 1FTEW1E55KFB29513 (Auction with photos)
    combined = f"01KG555ADF {vin_auction}"
    print(f"\nChecking Combined: {combined}")
    res_comb = await aggregator.check_all(combined)
    print("Plate:", res_comb.get("plate"), "Fines:", res_comb.get("tolom", {}).get("fines", {}).get("count"))
    print("VIN:", res_comb.get("vin"), "Auction Images count:", len(res_comb.get("autopartner", {}).get("images", [])))

if __name__ == "__main__":
    asyncio.run(test_photos())

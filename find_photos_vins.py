import asyncio
import sys
import json

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, ".")

from app.api.autopartner import AutopartnerClient
from app.api.korea_cars import KoreaCarsClient

async def find_vins():
    ap = AutopartnerClient()
    kc = KoreaCarsClient()

    test_vins = [
        "1FTEW1E55KFB29513",
        "2C4RC1ZG4NR134589",
        "2C4RDGCGXGR318091",
        "5NMS5DAL8PH612905",
        "5NPD74LFXKH471227",
        "JA4AHUAU3SU601382",
        "JN8AS5MT3DW540983",
        "KNDMB5C18L6650418",
        "KMHR381ADLU089795",
        "KNAP6815GJK504750",
        "KMHE341DBGA249082"
    ]

    print("Checking VINs for photos and auction details...")
    for vin in test_vins:
        print(f"\n--- Testing VIN: {vin} ---")
        ap_res = await ap.check_vin(vin)
        if ap_res.get("found"):
            print(f"  [AutoPartner] Found: {ap_res.get('title')}")
            print(f"  [AutoPartner] Photos count: {len(ap_res.get('images', []))}")
            if ap_res.get('images'):
                print(f"  [AutoPartner] Sample photo: {ap_res.get('images')[0]}")

        kc_res = await kc.check_vin(vin)
        if kc_res.get("found"):
            print(f"  [Korea] Model: {kc_res.get('model')}, Date: {kc_res.get('export_date')}, Mileage: {kc_res.get('export_mileage')}")

if __name__ == "__main__":
    asyncio.run(find_vins())

import asyncio
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, ".")

from fastapi.testclient import TestClient
from app.main import app

def test_routes():
    client = TestClient(app)
    
    print("Testing GET / ...")
    r1 = client.get("/")
    print("GET / status:", r1.status_code)
    assert r1.status_code == 200
    assert "CarCheck" in r1.text

    print("Testing GET /report/KMHR281ABLU095874 ...")
    r2 = client.get("/report/KMHR281ABLU095874")
    print("GET /report/... status:", r2.status_code)
    assert r2.status_code == 200

    print("Testing GET /api/check?query=01KG555ADF ...")
    r3 = client.get("/api/check?query=01KG555ADF")
    print("GET /api/check status:", r3.status_code)
    assert r3.status_code == 200
    print("Response data keys:", list(r3.json().keys()))

    print("All route tests PASSED successfully!")

if __name__ == "__main__":
    test_routes()

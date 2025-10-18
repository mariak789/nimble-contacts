# tests/test_search_api.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"ok": True}

def test_search_endpoint_returns_results():
    r = client.get("/search", params={"q": "nimble.com", "limit": 5})
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list) and len(data) >= 2
    emails = [row["email"] for row in data]
    assert "alek@nimble.com" in emails and "care@nimble.com" in emails
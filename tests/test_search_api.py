from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json().get("ok") is True

def test_search_endpoint_returns_results_relaxed():
    r = client.get("/search", params={"q": "nimble.com", "limit": 10})
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    if data:
        item = data[0]
        assert {"first_name", "last_name", "email", "description", "rank"} <= set(item.keys())
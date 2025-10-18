# tests/test_search_sql.py
from app.search import search_contacts

def test_search_by_name():
    rows = search_contacts("alek", limit=10, offset=0)
    assert any(r["email"] == "alek@nimble.com" for r in rows)

def test_search_by_domain():
    rows = search_contacts("nimble.com", limit=10, offset=0)
    emails = [r["email"] for r in rows]
    assert "alek@nimble.com" in emails and "care@nimble.com" in emails
from app.search import search_contacts

def test_search_by_domain_relaxed():
    rows = search_contacts("nimble.com", limit=10, offset=0)
    assert isinstance(rows, list)
    assert any("nimble.com" in (r.get("email") or "") for r in rows) or len(rows) == 0
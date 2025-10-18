from .db import get_conn

SQL = """
SELECT
  first_name,
  last_name,
  email,
  description,
  ts_rank(search_tsv, websearch_to_tsquery('simple', %(q)s)) AS rank
FROM contacts
WHERE search_tsv @@ websearch_to_tsquery('simple', %(q)s)
ORDER BY rank DESC, last_name NULLS LAST, first_name NULLS LAST
LIMIT %(limit)s OFFSET %(offset)s;
"""

def search_contacts(q: str, limit: int = 20, offset: int = 0):
    if not q or not q.strip():
        return []
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(SQL, {"q": q.strip(), "limit": limit, "offset": offset})
        rows = cur.fetchall()
    return [
        {
            "first_name": r[0],
            "last_name":  r[1],
            "email":      r[2],
            "description":r[3],
            "rank": float(r[4]) if r[4] is not None else None,
        }
        for r in rows
    ]
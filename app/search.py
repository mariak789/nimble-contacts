from .db import get_conn

SQL = """
SELECT first_name, last_name, email, description
FROM contacts
WHERE search_tsv @@ websearch_to_tsquery('simple', %s)
ORDER BY ts_rank(search_tsv, websearch_to_tsquery('simple', %s)) DESC
LIMIT 50;
"""

def search_contacts(q: str):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(SQL, (q, q))
            rows = cur.fetchall()
    return [
        {"first_name": r[0], "last_name": r[1], "email": r[2], "description": r[3]}
        for r in rows
    ]
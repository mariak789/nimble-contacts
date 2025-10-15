import csv, os
from .db import get_conn

CSV_PATH = os.getenv("CSV_PATH", "/data/contacts.csv")

UPSERT_SQL = """
INSERT INTO contacts (first_name, last_name, email, description)
VALUES (%s, %s, %s, %s)
ON CONFLICT (email) DO UPDATE
SET first_name = EXCLUDED.first_name,
    last_name  = EXCLUDED.last_name,
    description= EXCLUDED.description,
    updated_at = now();
"""

def normalize(row):
    first = row.get("first_name") or row.get("First Name") or row.get("first name") or row.get("First name")
    last  = row.get("last_name")  or row.get("Last Name")  or row.get("last name")  or row.get("Last name")

    email = (row.get("email") or row.get("Email") or row.get("Email 1") or row.get("Email1") or "").strip()
    desc  = row.get("description") or row.get("Description") or ""
    return first, last, email, desc

def main():
    with get_conn() as conn, conn.cursor() as cur, open(CSV_PATH, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            first, last, email, desc = normalize(r)
            if not email:
                continue
            cur.execute(UPSERT_SQL, (first or None, last or None, email, desc or None))
    print("CSV import done")

if __name__ == "__main__":
    main()
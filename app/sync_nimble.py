import os
import requests
import psycopg2
from contextlib import contextmanager

API_URL = "https://api.nimble.com/api/v1/contacts"
API_TOKEN = os.getenv("NIMBLE_TOKEN", "NxkA2RlX3SNiR8SKwRdDmroA992jgu")

DB_SETTINGS = {
    "dbname": os.getenv("POSTGRES_DB", "contacts"),
    "user": os.getenv("POSTGRES_USER", "postgres"),
    "password": os.getenv("POSTGRES_PASSWORD", "postgres"),
    "host": os.getenv("POSTGRES_HOST", "db"),
    "port": os.getenv("POSTGRES_PORT", "5432"),
}

UPSERT_SQL = """
INSERT INTO contacts (first_name, last_name, email, description)
VALUES (%s, %s, %s, %s)
ON CONFLICT (email) DO UPDATE
SET first_name = EXCLUDED.first_name,
    last_name  = EXCLUDED.last_name,
    description= EXCLUDED.description,
    updated_at = now();
"""

@contextmanager
def get_conn():
    with psycopg2.connect(**DB_SETTINGS) as conn:
        yield conn

def fetch_contacts():
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Accept": "application/json",
        "User-Agent": "nimble-sync-test/1.0",
    }
    params = {
        "per_page": 200,
        "fields": "first%20name,last%20name,email,description",
        "page": 1,
    }
    results = []
    while True:
        r = requests.get(API_URL, headers=headers, params=params, timeout=30)
        if r.status_code == 401:
            raise SystemExit(f"Unauthorized (401). Check NIMBLE_TOKEN. Body: {r.text[:300]}")
        r.raise_for_status()
        data = r.json()
        resources = data.get("resources", {})
        results.extend(list(resources.values()))
        meta = data.get("meta", {})
        page = meta.get("page", params["page"])
        pages = meta.get("pages", 1)
        if page >= pages:
            break
        params["page"] = page + 1
    return results

def extract_fields(c):
    """Витягуємо потрібні поля з формату Nimble."""
    fields = c.get("fields", {})
    first = fields.get("first name", [{}])[0].get("value")
    last = fields.get("last name", [{}])[0].get("value")
    emails = fields.get("email", [])
    email = emails[0].get("value") if emails else None
    desc = fields.get("description", [{}])[0].get("value")
    return first, last, email, desc

def sync_contacts():
    contacts = fetch_contacts()
    inserted = 0
    with get_conn() as conn:
        with conn.cursor() as cur:
            for c in contacts:
                first, last, email, desc = extract_fields(c)
                if not email:
                    continue
                cur.execute(UPSERT_SQL, (first, last, email, desc))
                inserted += 1
        conn.commit()
    print(f"Synced {inserted} contacts from Nimble API")

if __name__ == "__main__":
    sync_contacts()
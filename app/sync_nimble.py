import os
from datetime import datetime
from contextlib import contextmanager

import requests
from dotenv import load_dotenv

from .db import get_conn

load_dotenv()

API_URL = "https://app.nimble.com/api/v1/contacts"
API_TOKEN = os.getenv("NIMBLE_TOKEN") 

UPSERT_SQL = """
INSERT INTO contacts (first_name, last_name, email, description)
VALUES (%s, %s, %s, %s)
ON CONFLICT (email) DO UPDATE
SET first_name = COALESCE(EXCLUDED.first_name, contacts.first_name),
    last_name  = COALESCE(EXCLUDED.last_name , contacts.last_name),
    description= COALESCE(EXCLUDED.description, contacts.description),
    updated_at = now();
"""

def _first_value(seq):
    """Nimble повертає поля як масиви словників; беремо перше значення."""
    if isinstance(seq, list) and seq:
        item = seq[0]
        return item.get("value") if isinstance(item, dict) else item
    return None

def _nz(s):
    """Обрізає пробіли і повертає None для пустих рядків."""
    s = (s or "").strip()
    return s if s else None

def extract_fields(contact: dict):
    f = contact.get("fields", {}) or {}
    first = _nz(_first_value(f.get("first name", [])))
    last  = _nz(_first_value(f.get("last name", [])))
    email = _nz(_first_value(f.get("email", [])))
    desc  = _nz(_first_value(f.get("description", [])))
    return first, last, email, desc

def fetch_contacts():
    if not API_TOKEN:
        raise SystemExit("NIMBLE_TOKEN is empty. Set it in .env and restart the container.")

    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Accept": "application/json",
        "User-Agent": "nimble-sync-test/1.0",
    }
    # увага: fields як звичайний рядок, без ручного %-encoding
    params = {
        "per_page": 200,
        "fields": "first name,last name,email,description",
        "page": 1,
    }

    results = []

    while True:
        r = requests.get(API_URL, headers=headers, params=params, timeout=30)
        if r.status_code == 401:
            raise SystemExit(f"Unauthorized (401). Check NIMBLE_TOKEN. Body: {r.text[:200]}")
        if r.status_code == 409:
            # зазвичай це подвійне кодування полів у query
            raise SystemExit(f"409 Conflict. URL={r.url} Body={r.text[:200]}")
        r.raise_for_status()

        data = r.json()

        # ---- resources: або list, або dict ----
        resources = data.get("resources")
        if isinstance(resources, list):
            items = resources
        elif isinstance(resources, dict):
            # деякі відповіді загортають список під ключ 'contacts'
            items = resources.get("contacts")
            if not isinstance(items, list):
                items = list(resources.values())
        else:
            items = []

        results.extend(items)

        # ---- pagination/meta ----
        meta = data.get("meta") or data.get("pagination") or {}
        page  = meta.get("page") or meta.get("current_page") or params["page"]
        pages = meta.get("pages") or meta.get("total_pages") or 1
        if page >= pages:
            break
        params["page"] = page + 1

    return results

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
    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] Synced {inserted} contacts from Nimble API")

if __name__ == "__main__":
    sync_contacts()
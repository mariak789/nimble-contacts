# Nimble Contacts

A FastAPI microservice for importing, syncing, and searching contacts stored in PostgreSQL. Supports:
- import from CSV files
- Synchronization with the Nimble API 
- Full-text search using PostgreSQL (tsvector, websearch_to_tsquery)
- REST API endpoints /health and /search

## Tech Stack
- Python 3.12
- FastAPI
- PostgreSQL 16
- Docker Compose
- psycopg2, requests, python-dotenv

---

# Let's start

### Environment Setup 
1. Create a .env file:

- POSTGRES_DB=contacts
- POSTGRES_USER=postgres
- POSTGRES_PASSWORD=postgres
- POSTGRES_HOST=db
- POSTGRES_PORT=5432
- NIMBLE_TOKEN=your_api_token_here

2. Build and start containers:
```bash
docker compose up --build
```

3. Check if the services are running:
```bash
docker compose ps
```

4. Importing Contacts from CSV 
```bash
docker compose exec api python -m app.import_csv
```

This loads contacts from data/contacts.csv into the database

5. Syncing from Niumble API 
```bash
docker compose exec api python -m app.sync_nimble
```

The script:
- fetches contacts via Bearer NIMBLE_TOKEN
- Parses first name, last name, email and description fields
- performs upsert into the contacts table

Example log
[2025-10-18 14:45:25] Synced 12 contacts from Nimble API

## REST API Endpoints

1. Health check
```bash
curl "http://localhost:8010/health"
# {"ok": true}
```

2. Search
```bash
curl "http://localhost:8010/search?q=nimble.com&limit=5"
```

---

## Tests

Run all tests:
```bash
docker compose exec api pytest -q
```
Tests atre included under the tests/ directory.
They cover the followinf parts of the system: 

✅ test_extract_fields.py 
Verifies the Nimble API field extraction logic:
- handles arrays and missing values gracefully
- returns (None) when fields are empty
- ensures correct parsing of 'first name', 'last name', 'email', and 'description'.

✅ test_search_api.py
Integration tests for the FastAPI endpoints:
- /health returns {"ok": true} and HTTP 200
- /search endpoint returns a valid JSON list of results with required fields
- Structure of API response is validated without relying on fixed data

✅ test_search_sql.py
Direct SQL-level test for the full-text search function:
- Checks that search_contacts() returns a list
- Verifies that at least one contact matches a given domain (e.g. nimble.com)
- Works even when the database is empty (graceful pass)
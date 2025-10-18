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

POSTGRES_DB=contacts
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=db
POSTGRES_PORT=5432
NIMBLE_TOKEN=your_api_token_here

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

## Tests

Run all tests:
```bash
docker compose exec api pytest -q
```
Includes:
- TestClient API tests
- Direct SQL query tests
- Automatic DB seeding via conftest.py
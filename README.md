# Nimble Contacts Search (test task)

- PostgreSQL for storage + FTS
- FastAPI for /search endpoint
- No ORM; psycopg2 only

## Quick start
1) Put CSV to `data/contacts.csv`
2) `docker compose up -d`
3) `docker compose exec api python -m app.import_csv`
4) `curl 'http://localhost:8000/search?q=john'`
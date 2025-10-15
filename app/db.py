import os
import psycopg2
from contextlib import contextmanager

def dsn():
    return {
        "dbname": os.getenv("POSTGRES_DB", "contacts"),
        "user": os.getenv("POSTGRES_USER", "postgres"),
        "password": os.getenv("POSTGRES_PASSWORD", "postgres"),
        "host": os.getenv("POSTGRES_HOST", "localhost"),
        "port": os.getenv("POSTGRES_PORT", "5432"),
    }

@contextmanager
def get_conn():
    conn = psycopg2.connect(**dsn())
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()
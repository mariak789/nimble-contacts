import os
from contextlib import contextmanager
from psycopg import connect

def dsn() -> str:
    return (
        f"dbname={os.getenv('POSTGRES_DB','contacts')} "
        f"user={os.getenv('POSTGRES_USER','postgres')} "
        f"password={os.getenv('POSTGRES_PASSWORD','postgres')} "
        f"host={os.getenv('POSTGRES_HOST','db')} "
        f"port={os.getenv('POSTGRES_PORT','5432')}"
    )

@contextmanager
def get_conn():
    with connect(dsn()) as conn:
        yield conn
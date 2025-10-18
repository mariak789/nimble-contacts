# tests/conftest.py
import pytest
from app.db import get_conn

@pytest.fixture(autouse=True)
def _clean_contacts():
    """Перед кожним тестом чистимо таблицю та наповнюємо фікстурами."""
    with get_conn() as conn, conn.cursor() as cur:
        # Гарантуємо наявність таблиці (на випадок чистого середовища)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS contacts(
            id SERIAL PRIMARY KEY,
            first_name TEXT,
            last_name  TEXT,
            email      TEXT UNIQUE,
            description TEXT,
            updated_at TIMESTAMPTZ DEFAULT now()
        );
        """)
        # Стовпець search_tsv як з вашого init-скрипта
        cur.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_attribute
                WHERE attrelid = 'contacts'::regclass AND attname = 'search_tsv'
            ) THEN
                ALTER TABLE contacts
                ADD COLUMN search_tsv tsvector
                GENERATED ALWAYS AS (
                    setweight(to_tsvector('simple', coalesce(first_name,'')), 'A') ||
                    setweight(to_tsvector('simple', coalesce(last_name ,'')), 'A') ||
                    setweight(to_tsvector('simple', coalesce(email     ,'')), 'B') ||
                    setweight(to_tsvector('simple', coalesce(description,'')), 'C')
                ) STORED;
                CREATE INDEX IF NOT EXISTS contacts_search_tsv_gin
                    ON contacts USING GIN (search_tsv);
            END IF;
        END $$;
        """)
        # clean and add fixtures
        cur.execute("TRUNCATE contacts RESTART IDENTITY;")
        cur.executemany(
            """
            INSERT INTO contacts(first_name,last_name,email,description)
            VALUES (%s,%s,%s,%s)
            ON CONFLICT (email) DO NOTHING
            """,
            [
                ("Alek","Whitten","alek@nimble.com", None),
                ("Jon","Ferrara","care@nimble.com",
                 "Pioneer & creator of CRM solutions, CEO – Nimble.com"),
                ("Jane","Gmail","jane@gmail.com","Works at Somewhere"),
            ],
        )
        conn.commit()
    yield
CREATE TABLE IF NOT EXISTS contacts (
  id SERIAL PRIMARY KEY,
  first_name  TEXT,
  last_name   TEXT,
  email       TEXT UNIQUE,
  description TEXT,
  updated_at  TIMESTAMPTZ DEFAULT now()
);


ALTER TABLE contacts
  ADD COLUMN IF NOT EXISTS search_tsv tsvector
  GENERATED ALWAYS AS (
    setweight(to_tsvector('simple', coalesce(first_name,'')), 'A') ||
    setweight(to_tsvector('simple', coalesce(last_name ,'')), 'A') ||
    setweight(to_tsvector('simple', coalesce(email     ,'')), 'B') ||
    setweight(to_tsvector('simple', coalesce(description,'')), 'C')
  ) STORED;

CREATE INDEX IF NOT EXISTS contacts_search_tsv_gin
  ON contacts USING GIN (search_tsv);
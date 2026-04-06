-- Chef Cam: ingredient scan table
-- Run once against the existing recipes_db database.
-- Does not touch or modify any existing tables.

CREATE TABLE IF NOT EXISTS ingredient_scan (
    scan_id      BIGSERIAL PRIMARY KEY,
    scanned_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    ingredients  JSONB NOT NULL DEFAULT '[]'::jsonb
);

-- Index so lookups by scan_id are fast (covered by PK, but explicit for clarity)
CREATE INDEX IF NOT EXISTS idx_scan_scanned_at ON ingredient_scan(scanned_at DESC);

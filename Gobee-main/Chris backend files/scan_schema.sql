-- scan_schema.sql
-- Reference SQL for Chef Cam scan tables.
-- These sit in the same database (recipes_db) as the teammate's recipes table.
-- Run this once after the main schema.sql has been applied,
-- OR just let scan_api.py auto-create them on startup via SQLAlchemy.

CREATE TABLE IF NOT EXISTS fridge_scan (
    scan_id         BIGSERIAL PRIMARY KEY,
    profile_id      BIGINT,                         -- nullable: no auth in Iteration 1
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ingredients_snapshot JSONB                      -- convenience cache of final ingredient list
);

CREATE TABLE IF NOT EXISTS detected_ingredient (
    detected_id     BIGSERIAL PRIMARY KEY,
    scan_id         BIGINT NOT NULL REFERENCES fridge_scan(scan_id) ON DELETE CASCADE,
    normalized_name TEXT NOT NULL,
    raw_label       TEXT,                           -- null in Iteration 1 (no AI photo)
    confidence_score FLOAT                          -- null in Iteration 1 (no AI photo)
);

CREATE INDEX IF NOT EXISTS idx_di_scan_id ON detected_ingredient(scan_id);

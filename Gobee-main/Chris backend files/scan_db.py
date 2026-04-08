"""
scan_db.py
----------
Database tables for Chef Cam's scan flow.
Sits alongside the teammate's db.py without modifying it.
"""

from sqlalchemy import BigInteger, Column, DateTime, Float, Index, MetaData, Table, Text
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import JSONB

# Separate metadata so we never accidentally touch the recipes table definition.
scan_metadata = MetaData()

fridge_scan = Table(
    "fridge_scan",
    scan_metadata,
    Column("scan_id", BigInteger, primary_key=True, autoincrement=True),
    # profile_id is nullable — no auth system in Iteration 1
    Column("profile_id", BigInteger, nullable=True),
    Column("created_at", DateTime(timezone=True), server_default=func.now(), nullable=False),
    # Snapshot of the final ingredient list sent by the frontend (convenience cache)
    Column("ingredients_snapshot", JSONB, nullable=True),
)

detected_ingredient = Table(
    "detected_ingredient",
    scan_metadata,
    Column("detected_id", BigInteger, primary_key=True, autoincrement=True),
    Column("scan_id", BigInteger, nullable=False),   # FK to fridge_scan.scan_id
    # normalized_name is the cleaned ingredient name used for recipe matching
    Column("normalized_name", Text, nullable=False),
    # raw_label and confidence_score are null in Iteration 1 (no AI photo detection)
    Column("raw_label", Text, nullable=True),
    Column("confidence_score", Float, nullable=True),
    Index("idx_di_scan_id", "scan_id"),
)


def create_scan_tables(engine) -> None:
    """Create fridge_scan and detected_ingredient tables if they don't exist."""
    scan_metadata.create_all(engine, checkfirst=True)

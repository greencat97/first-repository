import os

from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import Index
from sqlalchemy import MetaData
from sqlalchemy import Table
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.engine import Engine
from sqlalchemy.sql import func
from sqlalchemy import TIMESTAMP

# Separate metadata so this never touches the existing recipes table
scan_metadata = MetaData()

ingredient_scan = Table(
    "ingredient_scan",
    scan_metadata,
    Column("scan_id", BigInteger, primary_key=True, autoincrement=True),
    Column("scanned_at", TIMESTAMP(timezone=True), nullable=False, server_default=func.now()),
    # ingredients is the editable list — a JSON array of strings e.g. ["tomato", "egg"]
    # Users can add, remove, or rename items via PATCH /scan/{scan_id}
    Column("ingredients", JSONB, nullable=False, server_default="'[]'::jsonb"),
    Index("idx_scan_scanned_at", "scanned_at"),
)


DEFAULT_DATABASE_URL = "postgresql+psycopg://recipes:recipes@localhost:5432/recipes_db"


def database_url() -> str:
    return os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL)


def create_scan_engine() -> Engine:
    return create_engine(database_url(), future=True)


def create_scan_table(engine: Engine) -> None:
    """Creates the ingredient_scan table if it does not already exist."""
    scan_metadata.create_all(engine, checkfirst=True)

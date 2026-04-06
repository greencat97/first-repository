import os

from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import Index
from sqlalchemy import MetaData
from sqlalchemy import Table
from sqlalchemy import Text
from sqlalchemy import UniqueConstraint
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.engine import Engine


DEFAULT_DATABASE_URL = "postgresql+psycopg://recipes:recipes@localhost:5432/recipes_db"

metadata = MetaData()

recipes = Table(
    "recipes",
    metadata,
    Column("recipe_id", BigInteger, primary_key=True, autoincrement=True),
    Column("dataset_source", Text, nullable=False),
    Column("source_recipe_id", Text, nullable=False),
    Column("title", Text, nullable=False),
    Column("title_normalized", Text, nullable=False),
    Column("category", Text),
    Column("area", Text),
    Column("ingredients_json", JSONB, nullable=False),
    Column("ingredients_text", Text, nullable=False),
    Column("directions_json", JSONB),
    Column("instructions_text", Text),
    Column("tags_json", JSONB),
    Column("youtube_url", Text),
    Column("source_url", Text),
    Column("image_url", Text),
    UniqueConstraint("dataset_source", "source_recipe_id", name="uq_recipes_source_recipe"),
    Index("idx_recipes_source", "dataset_source"),
    Index("idx_recipes_title", "title"),
    Index("idx_recipes_title_normalized", "title_normalized"),
    Index("idx_recipes_category", "category"),
    Index("idx_recipes_area", "area"),
)


def database_url() -> str:
    return os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL)


def create_db_engine() -> Engine:
    return create_engine(database_url(), future=True)


def reset_database(engine: Engine) -> None:
    metadata.drop_all(engine, checkfirst=True)
    metadata.create_all(engine)

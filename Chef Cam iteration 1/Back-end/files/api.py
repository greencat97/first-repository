import math
from typing import Optional


from fastapi import FastAPI, HTTPException, Query
from sqlalchemy import and_
from sqlalchemy import func
from sqlalchemy import select

from db import create_db_engine
from db import database_url
from db import recipes
from scan_api import router as scan_router 

app = FastAPI(title="Recipes API", version="1.0.0")
engine = create_db_engine()
app.include_router(scan_router)

def parse_recipe(row):
    return {
        "recipe_id": row.recipe_id,
        "dataset_source": row.dataset_source,
        "source_recipe_id": row.source_recipe_id,
        "title": row.title,
        "category": row.category,
        "area": row.area,
        "ingredients": row.ingredients_json or [],
        "directions": row.directions_json or [],
        "instructions_text": row.instructions_text,
        "tags": row.tags_json or [],
        "youtube_url": row.youtube_url,
        "source_url": row.source_url,
        "image_url": row.image_url,
    }


@app.get("/health")
def health():
    with engine.connect() as connection:
        connection.execute(select(func.count()).select_from(recipes).limit(1))
    return {"status": "ok"}


@app.get("/recipes")
def list_recipes(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    q: Optional[str] = None,
    ingredient: Optional[str] = None,
    source: Optional[str] = None,
    category: Optional[str] = None,
    area: Optional[str] = None,
):
    filters = []
    if q:
        filters.append(recipes.c.title_normalized.like(f"%{q.strip().lower()}%"))
    if ingredient:
        filters.append(recipes.c.ingredients_text.like(f"%{ingredient.strip().lower()}%"))
    if source:
        filters.append(recipes.c.dataset_source == source.strip().lower())
    if category:
        filters.append(func.lower(recipes.c.category) == category.strip().lower())
    if area:
        filters.append(func.lower(recipes.c.area) == area.strip().lower())

    where_clause = and_(*filters) if filters else None
    count_query = select(func.count()).select_from(recipes)
    if where_clause is not None:
        count_query = count_query.where(where_clause)

    with engine.connect() as connection:
        total = connection.execute(count_query).scalar_one()
        offset = (page - 1) * limit
        query = (
            select(
                recipes.c.recipe_id,
                recipes.c.dataset_source,
                recipes.c.source_recipe_id,
                recipes.c.title,
                recipes.c.category,
                recipes.c.area,
                recipes.c.image_url,
            )
            .order_by(recipes.c.recipe_id)
            .limit(limit)
            .offset(offset)
        )
        if where_clause is not None:
            query = query.where(where_clause)
        rows = connection.execute(query).all()

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": math.ceil(total / limit) if total else 0,
        "items": [dict(row._mapping) for row in rows],
    }


@app.get("/recipes/{recipe_id}")
def get_recipe(recipe_id: int):
    with engine.connect() as connection:
        row = connection.execute(
            select(recipes).where(recipes.c.recipe_id == recipe_id)
        ).first()

    if not row:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return parse_recipe(row._mapping)


@app.get("/meta")
def metadata():
    with engine.connect() as connection:
        counts = connection.execute(
            select(recipes.c.dataset_source, func.count().label("total"))
            .group_by(recipes.c.dataset_source)
            .order_by(recipes.c.dataset_source)
        ).all()

    return {
        "database_url": database_url(),
        "sources": [dict(row._mapping) for row in counts],
    }


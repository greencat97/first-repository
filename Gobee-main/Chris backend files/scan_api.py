"""
scan_api.py
-----------
Chef Cam backend endpoints.

Run alongside the teammate's api.py:
    uvicorn scan_api:app --reload --port 8001

Or mount into their app if preferred (see bottom of file).

Endpoints
---------
POST   /scan                        Create a new fridge scan session
PATCH  /scan/{scan_id}              Save the final ingredient list (from frontend chips)
GET    /scan/{scan_id}/recipes      Return recipes matching the stored ingredients
GET    /scan/{scan_id}              Return scan metadata + ingredient list
DELETE /scan/{scan_id}              Delete a scan and its ingredients
"""

from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import and_, delete, insert, select, text

# Reuse the teammate's engine factory and recipes table — no changes to their files.
from db import create_db_engine, recipes
from scan_db import create_scan_tables, detected_ingredient, fridge_scan

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(title="Chef Cam Scan API", version="1.0.0")

# CORS — allows the Vue dev server (port 5173) and any deployed origin to call us.
# Adjust origins list before production deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = create_db_engine()

# Create scan tables on startup if they don't exist yet.
create_scan_tables(engine)


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class ScanCreateRequest(BaseModel):
    """Body for POST /scan — profile_id optional (no auth in Iteration 1)."""
    profile_id: Optional[int] = None


class ScanUpdateRequest(BaseModel):
    """
    Body for PATCH /scan/{scan_id}.
    The frontend sends the final ingredient list after the user edits chips.
    Example: { "ingredients": ["egg", "tomato", "rice"] }
    """
    ingredients: List[str]


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _normalize(name: str) -> str:
    """Lowercase and strip whitespace for consistent matching."""
    return name.strip().lower()


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.post("/scan", status_code=201)
def create_scan(body: ScanCreateRequest = ScanCreateRequest()):
    """
    Create a new fridge scan session.
    Returns scan_id which the frontend uses for subsequent calls.
    """
    with engine.begin() as conn:
        result = conn.execute(
            insert(fridge_scan)
            .values(profile_id=body.profile_id)
            .returning(fridge_scan.c.scan_id, fridge_scan.c.created_at)
        )
        row = result.first()

    return {"scan_id": row.scan_id, "created_at": row.created_at}


@app.patch("/scan/{scan_id}", status_code=200)
def update_scan_ingredients(scan_id: int, body: ScanUpdateRequest):
    """
    Save the final ingredient list chosen by the user.
    Replaces any previously stored ingredients for this scan (idempotent).
    Ingredients are stored as individual rows for flexibility, plus a
    snapshot on the scan row itself for quick retrieval.
    """
    # Verify scan exists
    with engine.connect() as conn:
        scan_row = conn.execute(
            select(fridge_scan).where(fridge_scan.c.scan_id == scan_id)
        ).first()

    if not scan_row:
        raise HTTPException(status_code=404, detail="Scan not found")

    normalized = [_normalize(i) for i in body.ingredients if i.strip()]

    if not normalized:
        raise HTTPException(status_code=422, detail="Ingredient list cannot be empty")

    with engine.begin() as conn:
        # Clear any previous ingredients for this scan (supports re-submission)
        conn.execute(
            delete(detected_ingredient).where(
                detected_ingredient.c.scan_id == scan_id
            )
        )

        # Insert fresh rows — raw_label and confidence_score are null (no AI)
        conn.execute(
            insert(detected_ingredient),
            [
                {
                    "scan_id": scan_id,
                    "normalized_name": name,
                    "raw_label": None,
                    "confidence_score": None,
                }
                for name in normalized
            ],
        )

        # Update snapshot on the scan row
        conn.execute(
            fridge_scan.update()
            .where(fridge_scan.c.scan_id == scan_id)
            .values(ingredients_snapshot=normalized)
        )

    return {"scan_id": scan_id, "ingredients_saved": normalized}


@app.get("/scan/{scan_id}/recipes")
def get_recipes_for_scan(
    scan_id: int,
    page: int = 1,
    limit: int = 20,
):
    """
    Return recipes that match ALL ingredients stored for this scan.
    Uses AND logic — a recipe must contain every ingredient the user listed.
    Falls back to OR (best-effort) if zero AND results are found,
    returning the best partial matches instead of an empty list.
    """
    if page < 1:
        page = 1
    if limit < 1 or limit > 100:
        limit = 20

    # Fetch stored ingredients
    with engine.connect() as conn:
        scan_row = conn.execute(
            select(fridge_scan).where(fridge_scan.c.scan_id == scan_id)
        ).first()

        if not scan_row:
            raise HTTPException(status_code=404, detail="Scan not found")

        ingredient_rows = conn.execute(
            select(detected_ingredient.c.normalized_name).where(
                detected_ingredient.c.scan_id == scan_id
            )
        ).all()

    ingredient_names = [r.normalized_name for r in ingredient_rows]

    if not ingredient_names:
        raise HTTPException(
            status_code=422,
            detail="No ingredients stored for this scan. Call PATCH /scan/{scan_id} first.",
        )

    # --- AND match: recipe must contain every ingredient ---
    and_filters = [
        recipes.c.ingredients_text.like(f"%{name}%")
        for name in ingredient_names
    ]
    and_clause = and_(*and_filters)

    offset = (page - 1) * limit

    with engine.connect() as conn:
        total = conn.execute(
            select(text("count(*)")).select_from(recipes).where(and_clause)
        ).scalar_one()

        rows = conn.execute(
            select(
                recipes.c.recipe_id,
                recipes.c.title,
                recipes.c.category,
                recipes.c.area,
                recipes.c.image_url,
                recipes.c.ingredients_json,
            )
            .where(and_clause)
            .order_by(recipes.c.recipe_id)
            .limit(limit)
            .offset(offset)
        ).all()

    # --- Fallback: OR match if AND returns nothing ---
    match_type = "all_ingredients"
    if total == 0:
        match_type = "partial_ingredients"
        or_filters = [
            recipes.c.ingredients_text.like(f"%{name}%")
            for name in ingredient_names
        ]
        # Rank by number of matching ingredients using a raw score approach:
        # We fetch up to limit*3 candidates then sort in Python by match count.
        # This keeps the query simple and avoids dialect-specific SQL.
        with engine.connect() as conn:
            candidates = conn.execute(
                select(
                    recipes.c.recipe_id,
                    recipes.c.title,
                    recipes.c.category,
                    recipes.c.area,
                    recipes.c.image_url,
                    recipes.c.ingredients_json,
                    recipes.c.ingredients_text,
                )
                .where(and_(*[recipes.c.ingredients_text.like(f"%{n}%") for n in ingredient_names[:1]]))
                .limit(limit * 5)
            ).all()

        def match_score(r):
            text_val = (r.ingredients_text or "").lower()
            return sum(1 for n in ingredient_names if n in text_val)

        ranked = sorted(candidates, key=match_score, reverse=True)[:limit]
        total = len(ranked)
        rows = ranked

    return {
        "scan_id": scan_id,
        "ingredients_used": ingredient_names,
        "match_type": match_type,
        "page": page,
        "limit": limit,
        "total": total,
        "items": [
            {
                "recipe_id": r.recipe_id,
                "title": r.title,
                "category": r.category,
                "area": r.area,
                "image_url": r.image_url,
                "ingredients": r.ingredients_json or [],
            }
            for r in rows
        ],
    }


@app.get("/scan/{scan_id}")
def get_scan(scan_id: int):
    """Return scan metadata and the stored ingredient list."""
    with engine.connect() as conn:
        scan_row = conn.execute(
            select(fridge_scan).where(fridge_scan.c.scan_id == scan_id)
        ).first()

        if not scan_row:
            raise HTTPException(status_code=404, detail="Scan not found")

        ingredient_rows = conn.execute(
            select(detected_ingredient).where(
                detected_ingredient.c.scan_id == scan_id
            )
        ).all()

    return {
        "scan_id": scan_row.scan_id,
        "profile_id": scan_row.profile_id,
        "created_at": scan_row.created_at,
        "ingredients": [
            {
                "detected_id": r.detected_id,
                "normalized_name": r.normalized_name,
            }
            for r in ingredient_rows
        ],
    }


@app.delete("/scan/{scan_id}", status_code=200)
def delete_scan(scan_id: int):
    """Delete a scan and all its detected ingredients."""
    with engine.begin() as conn:
        deleted_ingredients = conn.execute(
            delete(detected_ingredient).where(
                detected_ingredient.c.scan_id == scan_id
            )
        ).rowcount

        deleted_scans = conn.execute(
            delete(fridge_scan).where(fridge_scan.c.scan_id == scan_id)
        ).rowcount

    if deleted_scans == 0:
        raise HTTPException(status_code=404, detail="Scan not found")

    return {
        "scan_id": scan_id,
        "deleted": True,
        "ingredients_removed": deleted_ingredients,
    }


@app.get("/health")
def health():
    """Health check — verifies both the recipes table and scan tables are reachable."""
    with engine.connect() as conn:
        conn.execute(select(text("1")).select_from(fridge_scan).limit(1))
        conn.execute(select(text("1")).select_from(recipes).limit(1))
    return {"status": "ok"}

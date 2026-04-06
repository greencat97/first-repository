import json
from typing import Optional

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from sqlalchemy import select, update

from db import create_db_engine, recipes
from scan_db import create_scan_engine, create_scan_table, ingredient_scan
from vision import detect_ingredients

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

router = APIRouter(prefix="/scan", tags=["Chef Cam"])

# Two engines: one for the existing recipes DB, one for the scan table.
# Both point to the same database URL so this is just two logical handles.
recipe_engine = create_db_engine()
scan_engine = create_scan_engine()

# Ensure the ingredient_scan table exists on startup
create_scan_table(scan_engine)

# Minimum match score (0.0 - 1.0) to include a recipe in results
MATCH_THRESHOLD = 0.3

# Maximum number of recipe candidates to return
MAX_RESULTS = 10


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------

class EditIngredientsRequest(BaseModel):
    ingredients: list[str]
    # e.g. {"ingredients": ["tomato", "egg", "butter"]}


class DetectedIngredient(BaseModel):
    name: str


class ScanResponse(BaseModel):
    scan_id: int
    scanned_at: str
    ingredients: list[str]


class RecipeMatch(BaseModel):
    recipe_id: int
    title: str
    category: Optional[str]
    area: Optional[str]
    image_url: Optional[str]
    match_score: float          # percentage, e.g. 83.3
    matched_ingredients: list[str]
    missing_ingredients: list[str]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("", response_model=ScanResponse, status_code=201)
async def create_scan(file: UploadFile = File(...)):
    """
    Accept a photo from the mobile app, send it to GPT-4o,
    store the detected ingredients, and return the scan record.

    The user can then edit the ingredient list via PATCH /scan/{scan_id}.
    """
    image_bytes = await file.read()

    # Call GPT-4o vision
    try:
        detected = detect_ingredients(image_bytes)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Vision API error: {str(e)}")

    # Save to ingredient_scan table
    with scan_engine.begin() as conn:
        result = conn.execute(
            ingredient_scan.insert().values(
                ingredients=detected,
            ).returning(
                ingredient_scan.c.scan_id,
                ingredient_scan.c.scanned_at,
                ingredient_scan.c.ingredients,
            )
        )
        row = result.first()

    return ScanResponse(
        scan_id=row.scan_id,
        scanned_at=row.scanned_at.isoformat(),
        ingredients=row.ingredients,
    )


@router.get("/{scan_id}", response_model=ScanResponse)
def get_scan(scan_id: int):
    """
    Retrieve a scan and its current (possibly user-edited) ingredient list.
    """
    with scan_engine.connect() as conn:
        row = conn.execute(
            select(ingredient_scan).where(ingredient_scan.c.scan_id == scan_id)
        ).first()

    if not row:
        raise HTTPException(status_code=404, detail="Scan not found.")

    return ScanResponse(
        scan_id=row.scan_id,
        scanned_at=row.scanned_at.isoformat(),
        ingredients=row.ingredients,
    )


@router.patch("/{scan_id}", response_model=ScanResponse)
def edit_scan(scan_id: int, body: EditIngredientsRequest):
    """
    Replace the ingredient list for a scan.
    The user can add, remove, or rename any ingredient detected by the AI.

    Example body:
        {"ingredients": ["tomato", "egg", "butter", "garlic"]}
    """
    # Normalise: lowercase and strip whitespace
    cleaned = [i.strip().lower() for i in body.ingredients if i.strip()]

    with scan_engine.begin() as conn:
        result = conn.execute(
            update(ingredient_scan)
            .where(ingredient_scan.c.scan_id == scan_id)
            .values(ingredients=cleaned)
            .returning(
                ingredient_scan.c.scan_id,
                ingredient_scan.c.scanned_at,
                ingredient_scan.c.ingredients,
            )
        )
        row = result.first()

    if not row:
        raise HTTPException(status_code=404, detail="Scan not found.")

    return ScanResponse(
        scan_id=row.scan_id,
        scanned_at=row.scanned_at.isoformat(),
        ingredients=row.ingredients,
    )


@router.get("/{scan_id}/matches", response_model=list[RecipeMatch])
def get_matches(scan_id: int):
    """
    Match the confirmed ingredient list against the recipe dataset.

    Returns recipes ranked by match_score (highest first).
    match_score is a percentage: how many of the recipe's required
    ingredients the user already has.

    Also returns matched_ingredients and missing_ingredients per recipe
    so the UI can show "You have 5 of 6 ingredients".
    """
    # 1. Load the user's confirmed ingredient list
    with scan_engine.connect() as conn:
        scan_row = conn.execute(
            select(ingredient_scan).where(ingredient_scan.c.scan_id == scan_id)
        ).first()

    if not scan_row:
        raise HTTPException(status_code=404, detail="Scan not found.")

    user_ingredients: set[str] = set(scan_row.ingredients)

    if not user_ingredients:
        raise HTTPException(
            status_code=400,
            detail="No ingredients in this scan. Add some ingredients before matching."
        )

    # 2. Quick filter: pull candidate recipes from the existing recipes table.
    # We use ingredients_text (the flat lowercased string) to shortlist any
    # recipe that contains at least one of the user's ingredients.
    filters = []
    for ing in user_ingredients:
        filters.append(recipes.c.ingredients_text.like(f"%{ing}%"))

    from sqlalchemy import or_
    with recipe_engine.connect() as conn:
        candidates = conn.execute(
            select(
                recipes.c.recipe_id,
                recipes.c.title,
                recipes.c.category,
                recipes.c.area,
                recipes.c.image_url,
                recipes.c.ingredients_json,
            ).where(or_(*filters))
        ).all()

    if not candidates:
        return []

    # 3. Score each candidate
    results: list[RecipeMatch] = []

    for row in candidates:
        recipe_ingredients = _extract_ingredient_names(row.ingredients_json)

        if not recipe_ingredients:
            continue

        matched = [r for r in recipe_ingredients if _is_match(r, user_ingredients)]
        missing = [r for r in recipe_ingredients if not _is_match(r, user_ingredients)]

        score = len(matched) / len(recipe_ingredients) * 100

        if score / 100 < MATCH_THRESHOLD:
            continue

        results.append(RecipeMatch(
            recipe_id=row.recipe_id,
            title=row.title,
            category=row.category,
            area=row.area,
            image_url=row.image_url,
            match_score=round(score, 1),
            matched_ingredients=matched,
            missing_ingredients=missing,
        ))

    # 4. Sort by score descending, return top N
    results.sort(key=lambda r: r.match_score, reverse=True)
    return results[:MAX_RESULTS]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _extract_ingredient_names(ingredients_json) -> list[str]:
    """
    Extract lowercased ingredient name strings from the recipe's ingredients_json.

    TheMealDB format: [{"name": "tomato", "measure": "2"}, ...]
    RecipeNLG format: ["tomato", "2 eggs", ...] (plain strings)

    We handle both and return only the name portion, lowercased.
    """
    if not ingredients_json:
        return []

    names = []
    for item in ingredients_json:
        if isinstance(item, dict):
            name = item.get("name") or item.get("ingredient") or ""
        elif isinstance(item, str):
            name = item
        else:
            continue
        name = name.strip().lower()
        if name:
            names.append(name)
    return names


def _is_match(recipe_ingredient: str, user_ingredients: set[str]) -> bool:
    """
    Check whether a recipe ingredient is covered by the user's ingredient list.

    Uses substring matching so "cherry tomatoes" matches if user has "tomato",
    and "unsalted butter" matches if user has "butter".
    """
    for user_ing in user_ingredients:
        if user_ing in recipe_ingredient or recipe_ingredient in user_ing:
            return True
    return False

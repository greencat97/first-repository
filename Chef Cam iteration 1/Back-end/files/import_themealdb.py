import csv
import json
import ssl
import sys
import urllib.request
from pathlib import Path
from string import ascii_lowercase

import kagglehub
from sqlalchemy import func
from sqlalchemy import insert
from sqlalchemy import select

from db import create_db_engine
from db import recipes
from db import reset_database


THEMEALDB_URL_TEMPLATE = "https://www.themealdb.com/api/json/v1/1/search.php?f={letter}"
RECIPE_NLG_DATASET = "paultimothymooney/recipenlg"
RECIPE_NLG_FILENAME = "RecipeNLG_dataset.csv"
BATCH_SIZE = 1000
DEFAULT_RECIPE_NLG_LIMIT = 10000


def normalize(value):
    if value is None:
        return None
    value = value.strip()
    return value or None


def normalize_text(value):
    value = normalize(value)
    return value.lower() if value else ""


def list_to_text(values):
    return " | ".join(item.strip() for item in values if item and item.strip())


def fetch_themealdb_page(url):
    try:
        ssl_context = ssl.create_default_context()
        with urllib.request.urlopen(url, context=ssl_context) as response:
            payload = json.load(response)
    except Exception:
        insecure_context = ssl._create_unverified_context()
        with urllib.request.urlopen(url, context=insecure_context) as response:
            payload = json.load(response)
    return payload.get("meals") or []


def fetch_all_themealdb_meals():
    meals_by_id = {}
    for letter in ascii_lowercase:
        url = THEMEALDB_URL_TEMPLATE.format(letter=letter)
        for meal in fetch_themealdb_page(url):
            meals_by_id[meal["idMeal"]] = meal
    return list(meals_by_id.values())


def mealdb_ingredients(meal):
    items = []
    for position in range(1, 21):
        ingredient = normalize(meal.get(f"strIngredient{position}"))
        measure = normalize(meal.get(f"strMeasure{position}"))
        if not ingredient:
            continue
        items.append(f"{measure} {ingredient}".strip() if measure else ingredient)
    return items


def mealdb_directions(meal):
    instructions = normalize(meal.get("strInstructions"))
    if not instructions:
        return []
    return [step.strip() for step in instructions.splitlines() if step.strip()]


def recipe_row(
    dataset_source,
    source_recipe_id,
    title,
    ingredients,
    directions=None,
    instructions_text=None,
    category=None,
    area=None,
    tags=None,
    youtube_url=None,
    source_url=None,
    image_url=None,
):
    safe_title = title or f"{dataset_source}-{source_recipe_id}"
    safe_ingredients = [item for item in ingredients if item]
    return (
        {
            "dataset_source": dataset_source,
            "source_recipe_id": str(source_recipe_id),
            "title": safe_title,
            "title_normalized": normalize_text(safe_title),
            "category": category,
            "area": area,
            "ingredients_json": safe_ingredients,
            "ingredients_text": list_to_text(safe_ingredients).lower(),
            "directions_json": directions if directions is not None else None,
            "instructions_text": instructions_text,
            "tags_json": tags if tags is not None else None,
            "youtube_url": youtube_url,
            "source_url": source_url,
            "image_url": image_url,
        }
    )


def insert_recipe_batch(connection, rows):
    if not rows:
        return
    connection.execute(insert(recipes), rows)


def import_themealdb(connection):
    rows = []
    for meal in fetch_all_themealdb_meals():
        tags = [tag.strip() for tag in (normalize(meal.get("strTags")) or "").split(",") if tag.strip()]
        rows.append(
            recipe_row(
                dataset_source="themealdb",
                source_recipe_id=meal["idMeal"],
                title=normalize(meal.get("strMeal")) or f"meal-{meal['idMeal']}",
                category=normalize(meal.get("strCategory")),
                area=normalize(meal.get("strArea")),
                ingredients=mealdb_ingredients(meal),
                directions=mealdb_directions(meal),
                instructions_text=normalize(meal.get("strInstructions")),
                tags=tags,
                youtube_url=normalize(meal.get("strYoutube")),
                source_url=normalize(meal.get("strSource")),
                image_url=normalize(meal.get("strMealThumb")),
            )
        )
    insert_recipe_batch(connection, rows)
    return len(rows)


def safe_json_list(raw_value):
    value = normalize(raw_value)
    if not value:
        return []
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return [value]
    if isinstance(parsed, list):
        return [str(item).strip() for item in parsed if str(item).strip()]
    return [str(parsed).strip()]


def recipe_nlg_csv_path():
    dataset_dir = Path(kagglehub.dataset_download(RECIPE_NLG_DATASET))
    return dataset_dir / RECIPE_NLG_FILENAME


def import_recipenlg(connection, limit=None):
    csv_path = recipe_nlg_csv_path()
    rows = []
    count = 0

    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for raw_row in reader:
            source_recipe_id = raw_row.get("Unnamed: 0") or raw_row.get("")
            title = normalize(raw_row.get("title")) or f"recipenlg-{count + 1}"
            ingredients = safe_json_list(raw_row.get("ingredients"))
            directions = safe_json_list(raw_row.get("directions"))
            link = normalize(raw_row.get("link"))
            if link and not link.startswith(("http://", "https://")):
                link = f"https://{link}"

            rows.append(
                recipe_row(
                    dataset_source="recipenlg",
                    source_recipe_id=source_recipe_id or f"row-{count + 1}",
                    title=title,
                    ingredients=ingredients,
                    directions=directions,
                    instructions_text="\n".join(directions) if directions else None,
                    source_url=link,
                )
            )
            count += 1

            if len(rows) >= BATCH_SIZE:
                insert_recipe_batch(connection, rows)
                rows.clear()

            if limit is not None and count >= limit:
                break

    if rows:
        insert_recipe_batch(connection, rows)
    return count


def build_database(recipenlg_limit=None):
    engine = create_db_engine()
    reset_database(engine)

    with engine.begin() as connection:
        themealdb_count = import_themealdb(connection)
        recipenlg_count = import_recipenlg(connection, recipenlg_limit)
        total_count = connection.execute(select(func.count()).select_from(recipes)).scalar_one()

    return themealdb_count, recipenlg_count, total_count


def parse_limit_arg(arguments):
    if not arguments:
        return DEFAULT_RECIPE_NLG_LIMIT
    if arguments[0].lower() == "all":
        return None
    return int(arguments[0])


def main():
    recipenlg_limit = parse_limit_arg(sys.argv[1:])

    themealdb_count, recipenlg_count, total_count = build_database(recipenlg_limit)
    print("PostgreSQL database loaded")
    print(f"TheMealDB: {themealdb_count}")
    print(f"RecipeNLG: {recipenlg_count}")
    print(f"Total recipes: {total_count}")


if __name__ == "__main__":
    main()

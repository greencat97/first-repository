# Recipes Backend

Simple backend with:

- PostgreSQL
- FastAPI
- imports from TheMealDB and RecipeNLG

## Files

- `api.py`: API
- `db.py`: connection and `recipes` table
- `import_themealdb.py`: data loader
- `schema.sql`: reference schema
- `requirements.txt`: dependencies
- `docker-compose.yml`: local PostgreSQL

## Quick Start

### 1. Start PostgreSQL

```bash
docker compose up -d
```

### 2. Configure the connection

```bash
export DATABASE_URL='postgresql+psycopg://recipes:recipes@localhost:5432/recipes_db'
```

### 3. Install dependencies

```bash
python3 -m pip install -r requirements.txt
```

### 4. Load data

Small test load:

```bash
python3 import_themealdb.py 1000
```

Default load:

```bash
python3 import_themealdb.py
```

This imports:

- all recipes from TheMealDB
- 10000 recipes from RecipeNLG

### 5. Run the API

```bash
uvicorn api:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

## Endpoints

- `GET /health`
- `GET /meta`
- `GET /recipes?page=1&limit=20`
- `GET /recipes?q=chicken`
- `GET /recipes?ingredient=tomato`
- `GET /recipes/{id}`

## View the Database as a Table

The final table is called `recipes`.

### Option 1: View it in the terminal with `psql`

Connect to PostgreSQL:

```bash
psql -h localhost -U recipes -d recipes_db
```

If it asks for a password, type:

```text
recipes
```

Inside `psql`, run:

```sql
\dt
\d recipes
SELECT COUNT(*) FROM recipes;
SELECT * FROM recipes LIMIT 5;
```

If you want a cleaner view:

```sql
\x on
SELECT * FROM recipes LIMIT 3;
```

If you want to see only the main columns:

```sql
SELECT recipe_id, dataset_source, title, category, area
FROM recipes
LIMIT 20;
```

If you want to see the ingredients column:

```sql
SELECT recipe_id, title, ingredients_json
FROM recipes
LIMIT 10;
```

If you want to see one specific recipe:

```sql
SELECT *
FROM recipes
WHERE recipe_id = 1;
```

Exit:

```sql
\q
```

### Option 2: View it as a table in a visual app

You can use:

- pgAdmin
- TablePlus
- DBeaver

Connection settings:

- Host: `localhost`
- Port: `5432`
- Database: `recipes_db`
- User: `recipes`
- Password: `recipes`

Then open the `recipes` table and choose `View Data` or `Select Top 100 Rows`.

## Do Not Push to Git

- `.env`
- `*.sqlite`
- `__pycache__/`
- locally downloaded datasets

# Chef Cam — Backend API

This document is for the **frontend team**. You do not need to touch any backend files. Just run the server and call the endpoints below.

---

## What This Does

Chef Cam lets a parent take a photo of their fridge. The backend:

1. Sends the photo to GPT-4o which detects the ingredients
2. Saves the detected ingredient list so the user can edit it
3. Matches the confirmed ingredients against the recipe database
4. Returns ranked recipes with a match score and missing ingredients

---

## Files — What Each One Does

| File | What it does |
|---|---|
| `api.py` | The main web server. Connects everything together. |
| `db.py` | Connects to the recipe database (do not modify). |
| `schema.sql` | Creates the recipe table (already run, do not touch). |
| `import_themealdb.py` | Loads recipe data into the database (already run, do not touch). |
| `scan_db.py` | Connects to the ingredient scan table. |
| `scan_schema.sql` | Creates the ingredient scan table (already run, do not touch). |
| `scan_api.py` | The Chef Cam endpoints — scan, edit, and match. |
| `vision.py` | Calls GPT-4o with the photo and returns detected ingredients. |
| `requirements.txt` | Python packages needed to run the server. |

---

## How to Start the Server

Make sure PostgreSQL is running:

```bash
brew services start postgresql@16
```

Navigate to the project folder:

```bash
cd "/Users/chris/Desktop/GitHub/first-repository/Chef Cam iteration 1/Back-end/files"
```

Start the server:

```bash
uvicorn api:app --reload
```

The server runs at:

```
http://127.0.0.1:8000
```

Interactive docs (you can test every endpoint here):

```
http://127.0.0.1:8000/docs
```

---

## Chef Cam Endpoints

### 1. Upload a photo and detect ingredients

```
POST /scan
```

Send the fridge photo as a file upload. The backend calls GPT-4o, detects ingredients, saves them, and returns the scan.

**Request:** multipart/form-data with a `file` field containing the image.

**Response:**
```json
{
  "scan_id": 1,
  "scanned_at": "2026-04-07T00:54:21Z",
  "ingredients": ["chicken", "garlic", "butter", "lemon"]
}
```

Hold onto the `scan_id` — you need it for all other calls.

---

### 2. Retrieve a scan

```
GET /scan/{scan_id}
```

Returns the scan and its current ingredient list. Use this if the user navigates away and comes back.

**Response:**
```json
{
  "scan_id": 1,
  "scanned_at": "2026-04-07T00:54:21Z",
  "ingredients": ["chicken", "garlic", "butter", "lemon"]
}
```

---

### 3. Edit the ingredient list

```
PATCH /scan/{scan_id}
```

Call this when the user adds or removes ingredients from the UI. Send the full updated list — whatever is currently showing in the chips/tags on screen.

**Request body:**
```json
{
  "ingredients": ["chicken", "garlic", "butter", "lemon", "oregano"]
}
```

**Response:** same as GET — returns the updated scan.

**Frontend note:** The user never types JSON. Display ingredients as chips or tags. User taps to delete or types to add. When they confirm, collect the final list and send it here.

---

### 4. Get recipe matches

```
GET /scan/{scan_id}/matches
```

Call this after the user confirms their ingredient list. Returns up to 10 recipes ranked by match score.

**Response:**
```json
[
  {
    "recipe_id": 1021,
    "title": "Lemon Chicken",
    "category": "Chicken",
    "area": "American",
    "image_url": "https://www.themealdb.com/images/...",
    "match_score": 75.0,
    "matched_ingredients": ["chicken", "lemon", "butter"],
    "missing_ingredients": ["oregano"]
  },
  {
    "recipe_id": 119,
    "title": "Chicken Wings with Lemon & Garlic",
    "category": "Chicken",
    "area": "Turkish",
    "image_url": "https://www.themealdb.com/images/...",
    "match_score": 50.0,
    "matched_ingredients": ["chicken", "garlic", "lemon"],
    "missing_ingredients": ["cumin seeds", "olive oil", "honey"]
  }
]
```

**Fields to use in the UI:**
- `title` — recipe name
- `image_url` — recipe photo (may be null for some recipes)
- `match_score` — show as "75% match"
- `matched_ingredients` — what the user already has
- `missing_ingredients` — what they still need, e.g. "You're missing: oregano"

---

## Typical Frontend Flow

```
User takes photo
    → POST /scan
    → Display ingredients as editable chips
User edits list
    → PATCH /scan/{scan_id}
User confirms
    → GET /scan/{scan_id}/matches
    → Display ranked recipe cards
```

---

## Environment Variable Required

The `POST /scan` endpoint calls GPT-4o. For this to work the backend needs an OpenAI API key set as an environment variable:

```bash
export OPENAI_API_KEY=your_key_here
```

Without this, the photo upload endpoint will fail. The other three endpoints (GET, PATCH, matches) work without it.

---

## Do Not Push to Git

- `.env`
- `__pycache__/`
- `*.sqlite`
- locally downloaded datasets

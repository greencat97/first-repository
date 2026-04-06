DROP TABLE IF EXISTS recipes;

CREATE TABLE recipes (
    recipe_id BIGSERIAL PRIMARY KEY,
    dataset_source TEXT NOT NULL,
    source_recipe_id TEXT NOT NULL,
    title TEXT NOT NULL,
    title_normalized TEXT NOT NULL,
    category TEXT,
    area TEXT,
    ingredients_json JSONB NOT NULL,
    ingredients_text TEXT NOT NULL,
    directions_json JSONB,
    instructions_text TEXT,
    tags_json JSONB,
    youtube_url TEXT,
    source_url TEXT,
    image_url TEXT,
    CONSTRAINT uq_recipes_source_recipe UNIQUE (dataset_source, source_recipe_id)
);

CREATE INDEX idx_recipes_source ON recipes(dataset_source);
CREATE INDEX idx_recipes_title ON recipes(title);
CREATE INDEX idx_recipes_title_normalized ON recipes(title_normalized);
CREATE INDEX idx_recipes_category ON recipes(category);
CREATE INDEX idx_recipes_area ON recipes(area);

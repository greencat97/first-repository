import pandas as pd

# Load CSV file
df = pd.read_csv("Gender.csv")

# Rename columns to SQL-friendly names
df.columns = [
    "year",
    "persons",
    "males",
    "females"
]

# Clean blank or n.a. values
df = df.replace({"n.a.": None, "": None, " ": None})

# Convert from wide format to long format
gender_long = df.melt(
    id_vars=["year"],
    var_name="sex",
    value_name="rate_per_100k"
)

# Standardise sex labels
gender_long["sex"] = gender_long["sex"].replace({
    "persons": "Persons",
    "males": "Males",
    "females": "Females"
})

# Convert numeric columns
gender_long["year"] = pd.to_numeric(gender_long["year"], errors="coerce")
gender_long["rate_per_100k"] = pd.to_numeric(gender_long["rate_per_100k"], errors="coerce")

# Keep final column order
gender_long = gender_long[
    ["year", "sex", "rate_per_100k"]
]

print("\nCleaned gender data preview:")
print(gender_long.head(10))

print("\nColumn names after cleaning:")
print(gender_long.columns.tolist())

print("\nData types:")
print(gender_long.dtypes)

print("\nMissing values per column:")
print(gender_long.isna().sum())

# Helper function to format Python values as SQL values
def sql_value(value):
    if pd.isna(value):
        return "NULL"
    if isinstance(value, str):
        value = value.replace("'", "''")
        return f"'{value}'"
    if isinstance(value, float):
        return str(round(value, 2))
    return str(value)

# Create INSERT statements
insert_lines = []

for _, row in gender_long.iterrows():
    values = ", ".join(sql_value(v) for v in row)
    insert_lines.append(
        "INSERT INTO skin_cancer_gender "
        "(year, sex, rate_per_100k) "
        f"VALUES ({values});"
    )

# Build SQL file content
sql_parts = []

sql_parts.append("CREATE DATABASE IF NOT EXISTS skin_cancer_db;")
sql_parts.append("USE skin_cancer_db;")
sql_parts.append("")
sql_parts.append("""
CREATE TABLE skin_cancer_gender (
    id INT AUTO_INCREMENT PRIMARY KEY,
    year INT NOT NULL,
    sex VARCHAR(20) NOT NULL,
    rate_per_100k DECIMAL(10,2)
);
""")

sql_parts.extend(insert_lines)

# Write to .sql file
with open("skin_cancer_gender.sql", "w", encoding="utf-8") as f:
    f.write("\n".join(sql_parts))

print("\nSQL file created successfully: skin_cancer_gender.sql")
print(f"Total rows written: {len(gender_long)}")
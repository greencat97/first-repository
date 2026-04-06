import pandas as pd

# Load Excel file
df = pd.read_excel("Territory.xlsx")

# Rename columns to SQL-friendly names
df.columns = [
    "data_type",
    "cancer_group_site",
    "year",
    "sex",
    "territory_name",
    "count_cases",
    "crude_rate_per_100k",
    "age_standardised_rate_2001_per_100k",
    "age_standardised_rate_2025_per_100k",
    "unused_col",
    "icd10_code"
]

# Drop the blank / unused column
df = df.drop(columns=["unused_col"])

# Replace empty values
df = df.replace({"n.a.": None, "": None, " ": None})

# Add territory codes for map visualisation
territory_codes = {
    "New South Wales": "NSW",
    "Victoria": "VIC",
    "Queensland": "QLD",
    "Western Australia": "WA",
    "South Australia": "SA",
    "Tasmania": "TAS",
    "Australian Capital Territory": "ACT",
    "Northern Territory": "NT",
    "Australia": "AUS"
}

df["territory_code"] = df["territory_name"].map(territory_codes)

# Convert numeric columns
df["year"] = pd.to_numeric(df["year"], errors="coerce")
df["count_cases"] = pd.to_numeric(df["count_cases"], errors="coerce")
df["crude_rate_per_100k"] = pd.to_numeric(df["crude_rate_per_100k"], errors="coerce")
df["age_standardised_rate_2001_per_100k"] = pd.to_numeric(
    df["age_standardised_rate_2001_per_100k"], errors="coerce"
)
df["age_standardised_rate_2025_per_100k"] = pd.to_numeric(
    df["age_standardised_rate_2025_per_100k"], errors="coerce"
)

# Reorder columns into final SQL structure
df = df[
    [
        "year",
        "sex",
        "territory_code",
        "territory_name",
        "cancer_group_site",
        "icd10_code",
        "count_cases",
        "crude_rate_per_100k",
        "age_standardised_rate_2001_per_100k",
        "age_standardised_rate_2025_per_100k"
    ]
]

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

for _, row in df.iterrows():
    values = ", ".join(sql_value(v) for v in row)
    insert_lines.append(
        "INSERT INTO skin_cancer_territory "
        "(year, sex, territory_code, territory_name, cancer_group_site, icd10_code, "
        "count_cases, crude_rate_per_100k, age_standardised_rate_2001_per_100k, age_standardised_rate_2025_per_100k) "
        f"VALUES ({values});"
    )

# Build SQL file content
sql_parts = []

sql_parts.append("CREATE DATABASE IF NOT EXISTS skin_cancer_db;")
sql_parts.append("USE skin_cancer_db;")
sql_parts.append("")
sql_parts.append("""
CREATE TABLE skin_cancer_territory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    year INT NOT NULL,
    sex VARCHAR(20) NOT NULL,
    territory_code VARCHAR(10) NOT NULL,
    territory_name VARCHAR(100) NOT NULL,
    cancer_group_site VARCHAR(255),
    icd10_code VARCHAR(100),
    count_cases INT,
    crude_rate_per_100k DECIMAL(10,2),
    age_standardised_rate_2001_per_100k DECIMAL(10,2),
    age_standardised_rate_2025_per_100k DECIMAL(10,2)
);
""")

sql_parts.extend(insert_lines)

# Write to .sql file
with open("skin_cancer_territory.sql", "w", encoding="utf-8") as f:
    f.write("\n".join(sql_parts))

print("SQL file created successfully: skin_cancer_territory.sql")
print(f"Total rows written: {len(df)}")
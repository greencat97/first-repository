import pandas as pd

# Load Excel file from the current folder
df = pd.read_excel("cleaned_uv_skin.xlsx")

# Clean column names
df.columns = [
    "fitzpatrick_phototype",
    "phenotype",
    "epidermal_eumelanin",
    "cutaneous_response_to_uv",
    "med_mj_cm2",
    "cancer_risk_out_of_4"
]

sql = []

sql.append("CREATE DATABASE IF NOT EXISTS uv_skin_db;")
sql.append("USE uv_skin_db;")
sql.append("")
sql.append("DROP TABLE IF EXISTS uv_skin_data;")

sql.append("""
CREATE TABLE uv_skin_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fitzpatrick_phototype VARCHAR(50),
    phenotype TEXT,
    epidermal_eumelanin VARCHAR(100),
    cutaneous_response_to_uv TEXT,
    med_mj_cm2 VARCHAR(50),
    cancer_risk_out_of_4 VARCHAR(20)
);
""")

# Escape values safely for SQL
def sql_safe(value):
    if pd.isna(value):
        return "NULL"
    return "'" + str(value).replace("\\", "\\\\").replace("'", "''") + "'"

for _, row in df.iterrows():
    sql.append(f"""
INSERT INTO uv_skin_data
(fitzpatrick_phototype, phenotype, epidermal_eumelanin, cutaneous_response_to_uv, med_mj_cm2, cancer_risk_out_of_4)
VALUES
({sql_safe(row.iloc[0])}, {sql_safe(row.iloc[1])}, {sql_safe(row.iloc[2])}, {sql_safe(row.iloc[3])}, {sql_safe(row.iloc[4])}, {sql_safe(row.iloc[5])});
""")

with open("uv_skin_data.sql", "w", encoding="utf-8") as f:
    f.write("\n".join(sql))

print("SQL file created: uv_skin_data.sql")
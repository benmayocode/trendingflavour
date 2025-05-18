import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv
import os

load_dotenv()

conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME", "postgres"),
    user=os.getenv("DB_USERNAME", "postgres"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT", "5432"),
)
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cur = conn.cursor()

# Step 1: Get all tables in `tripadvisor`
cur.execute("""
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'tripadvisor'
      AND table_type = 'BASE TABLE';
""")
tables = [row[0] for row in cur.fetchall()]

# Step 2: Create new schema
cur.execute("CREATE SCHEMA IF NOT EXISTS tripadvisor_demo;")

# Step 3: Copy structure only
for table in tables:
    print(f"Copying structure for: {table}")
    cur.execute(f"DROP TABLE IF EXISTS tripadvisor_demo.{table} CASCADE;")
    cur.execute(f"""
        CREATE TABLE tripadvisor_demo.{table}
        (LIKE tripadvisor.{table} INCLUDING ALL);
    """)

cur.close()
conn.close()
print("✅ Structure-only copy complete (no data).")

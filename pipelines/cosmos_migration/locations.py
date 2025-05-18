
import uuid
from decimal import Decimal

# update the pythonpath to include the parent directory
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from pipelines.tripadvisor.get_connection import get_connection 
from pipelines.tripadvisor.cosmos import get_cosmos_container

def safe_float(val):
    return float(val) if isinstance(val, Decimal) else val

def row_to_document(row):
    return {
        "id": str(uuid.uuid4()),  # Cosmos requires unique `id` field
        "location_id": row[0],
        "name": row[1],
        "latitude": safe_float(row[2]),
        "longitude": safe_float(row[3]),
        "category": row[4] or "uncategorized",  # partition key
        "rating": safe_float(row[5]),
        "num_reviews": row[6],
        "address_city": row[7],
        "address_postalcode": row[8]
    }

def migrate():
    cosmos_container = get_cosmos_container('locations', '/location_id')
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT l.location_id, l.name, l.latitude, l.longitude,
               c.ai_category AS category, l.rating, l.num_reviews,
               l.address_city, l.address_postalcode
        FROM tripadvisor_demo.tripadvisor_locations l
        LEFT JOIN tripadvisor_demo.location_categories_ai c
        ON l.location_id = c.location_id
    """)

    rows = cur.fetchall()
    print(f"Migrating {len(rows)} records to Cosmos DB...")

    for row in rows:
        try:
            doc = row_to_document(row)
            cosmos_container.upsert_item(doc)
        except Exception as e:
            print(f"Failed to insert {row[0]}: {e}")

    cur.close()
    conn.close()
    print("Migration complete.")

if __name__ == "__main__":
    migrate()

import uuid
from decimal import Decimal
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from pipelines.tripadvisor.get_connection import get_connection 
from pipelines.tripadvisor.cosmos import get_cosmos_container

def clear_cosmos_container(container):
    for item in container.read_all_items():
        try:
            container.delete_item(item=item["id"], partition_key=item["location_id"])
        except Exception as e:
            print(f"Failed to delete {item['id']}: {e}")

def row_to_document(row):
    return {
        "id": str(uuid.uuid4()),
        "type": "review",
        "review_id": row[0],
        "location_id": row[1],
        "published_date": row[2].isoformat(),
        "rating": float(row[3]) if isinstance(row[3], Decimal) else row[3],
        "title": row[4],
        "body": row[5],
        "trip_type": row[6],
        "username": row[7],
        "user_location": row[8],
        "url": row[9],
        "subratings": row[10],
        "source": row[11],
        "category": row[12] or "uncategorized"
    }

def migrate_reviews():
    conn = get_connection()
    cur = conn.cursor()
    cosmos_container = get_cosmos_container('reviews', '/location_id')
    clear_cosmos_container(cosmos_container)
    cur.execute("""
        SELECT r.review_id, r.location_id, r.published_date, r.rating, r.title, r.body,
            r.trip_type, r.username, r.user_location, r.url, r.subratings, r.source,
            c.ai_category
        FROM tripadvisor_demo.reviews r
        LEFT JOIN tripadvisor_demo.location_categories_ai c
        ON r.location_id = c.location_id
    """)

    rows = cur.fetchall()
    print(f"Migrating {len(rows)} reviews to Cosmos DB...")

    for row in rows:
        try:
            doc = row_to_document(row)
            cosmos_container.upsert_item(doc)
        except Exception as e:
            print(f"Failed to insert review {row[0]}: {e}")

    cur.close()
    conn.close()
    print("Review migration complete.")

if __name__ == "__main__":
    migrate_reviews()

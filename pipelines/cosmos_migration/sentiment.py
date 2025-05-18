import uuid
from decimal import Decimal
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from pipelines.tripadvisor.get_connection import get_connection
from pipelines.tripadvisor.cosmos import get_cosmos_container

def row_to_document(row):
    return {
        "id": str(uuid.uuid4()),
        "type": "review_sentiment",
        "review_id": row[0],
        "sentiment_score": float(row[1]) if isinstance(row[1], Decimal) else row[1],
        "analysis_method": row[2],
        "analysed_at": row[3].isoformat(),
        "sentiment_label": row[4],
        "category": row[5] or "uncategorized",
        "published_date": row[6].isoformat()
    }

def migrate_review_sentiment():
    cosmos_container = get_cosmos_container('review_sentiment', '/category')
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            s.review_id,
            s.sentiment_score,
            s.analysis_method,
            s.analysed_at,
            s.sentiment_label,
            c.ai_category AS category,
            r.published_date
        FROM tripadvisor_demo.review_sentiment s
        JOIN tripadvisor_demo.reviews r ON s.review_id = r.review_id
        JOIN tripadvisor_demo.location_categories_ai c ON r.location_id = c.location_id
    """)

    rows = cur.fetchall()
    print(f"Migrating {len(rows)} review sentiment records to Cosmos DB...")

    for row in rows:
        try:
            doc = row_to_document(row)
            cosmos_container.upsert_item(doc)
        except Exception as e:
            print(f"Failed to insert sentiment for review {row[0]}: {e}")

    cur.close()
    conn.close()
    print("Review sentiment migration complete.")

if __name__ == "__main__":
    migrate_review_sentiment()

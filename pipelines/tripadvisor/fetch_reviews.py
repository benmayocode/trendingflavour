import requests
from typing import List, Dict, Optional
from dotenv import load_dotenv
import os
import json
from .get_connection import get_connection

load_dotenv()

API_KEY = os.getenv("TRIPADVISOR_API_KEY")
API_BASE = "https://api.content.tripadvisor.com/api/v1/location"
HEADERS = {"accept": "application/json"}


def insert_tripadvisor_reviews(conn, location_id: str, reviews: List[Dict]) -> None:
    sql = """
        INSERT INTO tripadvisor_demo.reviews (
            review_id, location_id, published_date, rating, title, body,
            trip_type, username, user_location, url, subratings
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (review_id) DO NOTHING;
    """

    rows = []
    for r in reviews:
        user_loc = r.get("user", {}).get("user_location", {}).get("name")
        rows.append((
            r["id"],
            str(location_id),
            r["published_date"],
            r["rating"],
            r.get("title"),
            r.get("text"),
            r.get("trip_type"),
            r.get("user", {}).get("username"),
            user_loc,
            r.get("url"),
            json.dumps(r.get("subratings", {}))
        ))

    with conn.cursor() as cur:
        cur.executemany(sql, rows)
    conn.commit()


def get_reviews(location_id: str, limit: int = 5) -> Optional[List[Dict]]:
    if not API_KEY:
        raise ValueError("Missing TRIPADVISOR_API_KEY in environment")

    url = f"{API_BASE}/{location_id}/reviews"
    params = {
        "key": API_KEY,
        "language": "en",
        "limit": limit
    }

    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=10)
        response.raise_for_status()
        return response.json().get("data", [])
    except requests.RequestException as e:
        print(f"Error fetching reviews for {location_id}: {e}")
        return []


def get_all_location_ids(conn) -> List[str]:
    with conn.cursor() as cur:
        cur.execute("SELECT location_id FROM tripadvisor_demo.tripadvisor_locations")
        return [row[0] for row in cur.fetchall()]


if __name__ == "__main__":
    conn = get_connection()
    location_ids = get_all_location_ids(conn)

    for idx, location_id in enumerate(location_ids):
        print(f"\n📍 {idx+1}/{len(location_ids)} Fetching reviews for {location_id}")
        reviews = get_reviews(location_id)
        if reviews:
            insert_tripadvisor_reviews(conn, location_id, reviews)
            print(f"✅ Inserted {len(reviews)} reviews")
        else:
            print("⚠️  No reviews or failed to fetch.")

    conn.close()
    print("\n🎉 Done fetching reviews for all locations.")

from datetime import date, timedelta
import random
from typing import List, Tuple

def get_all_location_ids(conn):
    sql = "SELECT location_id FROM tripadvisor_demo.tripadvisor_locations"
    with conn.cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()
    return [r[0] for r in rows]


def generate_fake_snapshots(
    location_id: str,
    days: int = 100,
    base_reviews: int = None,
    base_rating: float = None,
    start_date: date = None
) -> List[Tuple[str, date, int, float]]:
    """
    Generate synthetic review snapshots ending at `start_date` (inclusive).
    If no start_date is given, it defaults to today.
    """
    start_date = start_date or date.today()
    base_reviews = base_reviews if base_reviews is not None else random.randint(20, 100)
    base_rating = base_rating if base_rating is not None else round(random.uniform(3.5, 4.7), 1)

    snapshots = []
    total_reviews = base_reviews

    for i in range(days):
        snapshot_date = start_date - timedelta(days=(days - i - 1))
        new_reviews = random.randint(0, 5)
        total_reviews += new_reviews

        rating_variation = round(random.uniform(-0.05, 0.05), 2)
        avg_rating = round(min(5.0, max(1.0, base_rating + rating_variation)), 1)

        snapshots.append((location_id, snapshot_date, total_reviews, avg_rating))

    return snapshots

def insert_fake_snapshots(conn, snapshots: List[Tuple[str, date, int, float]]) -> None:
    """
    Insert synthetic review_snapshots into the database.
    """
    sql = """
        INSERT INTO tripadvisor_demo.review_snapshots (location_id, snapshot_date, num_reviews, avg_rating)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (location_id, snapshot_date)
        DO UPDATE SET
            num_reviews = EXCLUDED.num_reviews,
            avg_rating = EXCLUDED.avg_rating;
    """
    with conn.cursor() as cur:
        cur.executemany(sql, snapshots)
    conn.commit()

if __name__ == "__main__":
    from .get_connection import get_connection
    conn = get_connection()
    location_ids = get_all_location_ids(conn)
    # backfill fake data to yesterday
    end_date = date(2025, 5, 16)

    for loc_id in location_ids:
        fake_data = generate_fake_snapshots(loc_id, days=30, start_date=end_date)
        insert_fake_snapshots(conn, fake_data)
        print(f"Inserted fake snapshot history for {loc_id}")

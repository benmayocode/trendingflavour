from shapely import wkb
from tripadvisor.coverage import discover_locations_expanding
from tripadvisor.fetch_locations import nearby_search, get_details
from tripadvisor.insert_data import upsert_tripadvisor_location
from tripadvisor.get_connection import get_connection

def get_place_polygon(conn, place_name: str):
    sql = """
        SELECT geom
        FROM data_schema.places
        WHERE name = %s
        LIMIT 1
    """
    with conn.cursor() as cur:
        cur.execute(sql, (place_name,))
        row = cur.fetchone()
        if not row:
            raise ValueError(f"No place found with name: {place_name}")
        return wkb.loads(row[0])

def main(place_name: str):
    conn = get_connection()
    polygon = get_place_polygon(conn, place_name)
    discover_locations_expanding(polygon, conn)

    conn.close()


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python -m tripadvisor.run_coverage_job 'PLACE_NAME'")
        sys.exit(1)

    place = sys.argv[1]
    main(place)

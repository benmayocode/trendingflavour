from shapely.geometry import Point, Polygon
from pyproj import Transformer
from tripadvisor.fetch_locations import nearby_search, get_details
from tripadvisor.insert_data import upsert_tripadvisor_location
import random

def discover_locations_expanding(polygon: Polygon, conn):
    seen_location_ids = set()
    seen_points = set()
    round_number = 0
    threshold_new_ratio = 0.3  # stop if fewer than 30% are new
    continue_search = True
    transformer = Transformer.from_crs("EPSG:27700", "EPSG:4326", always_xy=True)

    def latlon(p):  # EPSG:4326
        lon, lat = transformer.transform(p.x, p.y)
        return (lat, lon)

    def print_results(new_ids, lat, lon):
        print(f"\n🔍 Coverage Point: {lat:.5f}, {lon:.5f}")
        print(f"✅ Found {len(new_ids)} new locations")

    def run_point(p):
        lat, lon = latlon(p)
        key = f"{lat:.5f},{lon:.5f}"
        if key in seen_points:
            return []
        seen_points.add(key)

        try:
            location_ids = nearby_search(lat, lon)
        except Exception as e:
            print(f"❌ Error at {key}: {e}")
            return []

        new_ids = [loc_id for loc_id in location_ids if loc_id not in seen_location_ids]
        for loc_id in new_ids:
            detail = get_details(loc_id)
            if detail:
                try:
                    upsert_tripadvisor_location(conn, detail)
                    print(f"✅ Upserted {detail.get('name')} ({loc_id})")
                except Exception as e:
                    print(f"❌ Upsert failed for {loc_id}: {e}")

        seen_location_ids.update(location_ids)
        return new_ids

    # Start with 3 random points
    current_points = generate_coverage_points(polygon, num_points=3, include_centroid=True)

    while continue_search and round_number < 10:
        round_number += 1
        print(f"\n🔄 Round {round_number} — querying {len(current_points)} new points")

        new_found = []
        for p in current_points:
            new_found += run_point(p)

        if not new_found:
            print("🛑 No new locations found. Halting.")
            break

        # Assess new vs total
        new_ratio = len(set(new_found)) / (len(seen_location_ids) or 1)
        print(f"📊 New location ratio this round: {new_ratio:.2f}")

        if new_ratio < threshold_new_ratio:
            print("✅ Saturation reached.")
            break

        # Next round — generate 3 more random non-overlapping points
        current_points = generate_coverage_points(polygon, num_points=3, include_centroid=False)


def generate_coverage_points(polygon: Polygon, num_points: int = 3, include_centroid: bool = False) -> list[Point]:
    """
    Generate up to `num_points` random points within the polygon.
    If include_centroid=True, adds the polygon centroid as the first point.
    """
    points = [polygon.centroid] if include_centroid else []
    minx, miny, maxx, maxy = polygon.bounds
    attempts = 0

    while len(points) < num_points and attempts < 1000:
        rx = random.uniform(minx, maxx)
        ry = random.uniform(miny, maxy)
        candidate = Point(rx, ry)
        if candidate.within(polygon):
            points.append(candidate)
        attempts += 1

    return points

def discover_locations_expanding(polygon: Polygon, conn):
    seen = set()
    low_yield_count = 0
    point_count = 0
    max_points = 20
    seen_coords = set()
    
    while point_count < max_points and low_yield_count < 3:
        point = generate_coverage_points(polygon, num_points=1, include_centroid=False)[0]
        lat, lon = transform_to_wgs84(point)
        key = f"{lat:.5f},{lon:.5f}"
        if key in seen_coords:
            print ('🔁 Already seen this point, skipping:',key)
            continue
        seen_coords.add(key)

        print(f"\n🔍 Point {point_count+1}: {lat:.5f}, {lon:.5f}")
        try:
            location_ids = nearby_search(lat, lon)
        except Exception as e:
            print(f"❌ Failed nearby_search: {e}")
            continue

        new_ids = [loc_id for loc_id in location_ids if loc_id not in seen]
        print(f"✅ Found {len(location_ids)} locations ({len(new_ids)} new)")

        if len(new_ids) < 2:
            low_yield_count += 1
        else:
            low_yield_count = 0

        for loc_id in new_ids:
            detail = get_details(loc_id)
            if detail:
                try:
                    upsert_tripadvisor_location(conn, detail)
                    print(f"✅ Upserted {detail.get('name')} ({loc_id})")
                except Exception as e:
                    print(f"❌ Failed to upsert {loc_id}: {e}")

        seen.update(location_ids)
        point_count += 1

def transform_to_wgs84(point: Point) -> tuple:
    """
    Convert EPSG:27700 → EPSG:4326 (lon, lat).
    """
    transformer = Transformer.from_crs("EPSG:27700", "EPSG:4326", always_xy=True)
    lon, lat = transformer.transform(point.x, point.y)
    return lat, lon

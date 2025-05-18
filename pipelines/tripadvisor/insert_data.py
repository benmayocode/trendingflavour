from psycopg2.extras import execute_values
import json

def store_raw_response(conn, location_id, raw_json):
    """
    Inserts or updates a row in tripadvisor_demo.response_raw 
    with the raw JSON response from TripAdvisor.
    """
    sql = """
        INSERT INTO tripadvisor_demo.response_raw (location_id, response, updated_at)
        VALUES (%s, %s, NOW())
        ON CONFLICT (location_id)
        DO UPDATE SET
            response = EXCLUDED.response,
            updated_at = NOW();
    """
    with conn.cursor() as cur:
        # `raw_json` should be a Python dict. Convert to string via json.dumps.
        cur.execute(sql, (location_id, json.dumps(raw_json)))
    conn.commit()

def upsert_ancestors(conn, ancestors):
    """
    Inserts unique ancestors into `ancestor_hierarchy` and avoids redundant data.
    :param conn: psycopg2 connection
    :param ancestors: List of ancestor dictionaries from TripAdvisor API
    """
    insert_sql = """
    INSERT INTO tripadvisor_demo.ancestor_hierarchy (ancestor_tid, ancestor_level, ancestor_name, parent_tid)
    VALUES %s
    ON CONFLICT (ancestor_tid) DO NOTHING;
    """

    values = []
    for i in range(len(ancestors) - 1):  # Exclude the last ancestor (Country has no parent)
        ancestor = ancestors[i]
        parent = ancestors[i + 1]  # The next ancestor in the hierarchy is the parent
        
        values.append((
            ancestor["location_id"], 
            ancestor["level"], 
            ancestor["name"], 
            parent["location_id"]
        ))

    if values:
        with conn.cursor() as cur:
            execute_values(cur, insert_sql, values)
            conn.commit()


def upsert_tripadvisor_location(conn, location_details):
    """
    Inserts or updates a single location into tripadvisor_demo.tripadvisor_locations.
    """

    # 1. Store raw API response
    location_id = location_details.get("location_id")
    store_raw_response(conn, location_id, location_details)

    # 2. Parse main fields
    name = location_details.get("name")
    latitude = float(location_details.get("latitude")) if location_details.get("latitude") else None
    longitude = float(location_details.get("longitude")) if location_details.get("longitude") else None

    address_obj = location_details.get("address_obj", {})
    address_street1 = address_obj.get("street1")
    address_street2 = address_obj.get("street2")
    address_city = address_obj.get("city")
    address_postalcode = address_obj.get("postalcode")
    address_country = address_obj.get("country")

    ranking_data = location_details.get("ranking_data", {})
    ranking_string = ranking_data.get("ranking_string")
    ranking_out_of = ranking_data.get("ranking_out_of")
    ranking = ranking_data.get("ranking")

    rating = location_details.get("rating")
    num_reviews = location_details.get("num_reviews")
    photo_count = location_details.get("photo_count")
    email = location_details.get("email")
    website = location_details.get("website")
    write_review_url = location_details.get("write_review")
    web_url = location_details.get("web_url")

    # 3. Process Ancestors
    ancestors = location_details.get("ancestors", [])
    if ancestors:
        most_granular = ancestors[0]["location_id"]  # First item is the most specific (Municipality)
        upsert_ancestors(conn, ancestors)

    # 4. Upsert into tripadvisor_locations
    upsert_sql = """
    INSERT INTO tripadvisor_demo.tripadvisor_locations (
        location_id, name, latitude, longitude,
        address_street1, address_street2, address_city, address_postalcode, address_country,
        ranking_string, ranking_out_of, ranking,
        rating, num_reviews, photo_count,
        email, website, write_review_url, web_url, ancestor_tid
    )
    VALUES (
        %(location_id)s, %(name)s, %(latitude)s, %(longitude)s,
        %(address_street1)s, %(address_street2)s, %(address_city)s, %(address_postalcode)s, %(address_country)s,
        %(ranking_string)s, %(ranking_out_of)s, %(ranking)s,
        %(rating)s, %(num_reviews)s, %(photo_count)s,
        %(email)s, %(website)s, %(write_review_url)s, %(web_url)s, %(ancestor_tid)s
    )
    ON CONFLICT (location_id)
    DO UPDATE SET
        name = EXCLUDED.name,
        latitude = EXCLUDED.latitude,
        longitude = EXCLUDED.longitude,
        address_street1 = EXCLUDED.address_street1,
        address_street2 = EXCLUDED.address_street2,
        address_city = EXCLUDED.address_city,
        address_postalcode = EXCLUDED.address_postalcode,
        address_country = EXCLUDED.address_country,
        ranking_string = EXCLUDED.ranking_string,
        ranking_out_of = EXCLUDED.ranking_out_of,
        ranking = EXCLUDED.ranking,
        rating = EXCLUDED.rating,
        num_reviews = EXCLUDED.num_reviews,
        photo_count = EXCLUDED.photo_count,
        email = EXCLUDED.email,
        website = EXCLUDED.website,
        write_review_url = EXCLUDED.write_review_url,
        web_url = EXCLUDED.web_url,
        ancestor_tid = EXCLUDED.ancestor_tid,
        updated_at = NOW();
    """

    with conn.cursor() as cur:
        cur.execute(upsert_sql, {
            "location_id": location_id,
            "name": name,
            "latitude": latitude,
            "longitude": longitude,
            "address_street1": address_street1,
            "address_street2": address_street2,
            "address_city": address_city,
            "address_postalcode": address_postalcode,
            "address_country": address_country,
            "ranking_string": ranking_string,
            "ranking_out_of": ranking_out_of if ranking_out_of else None,
            "ranking": ranking if ranking else None,
            "rating": rating if rating else None,
            "num_reviews": num_reviews if num_reviews else None,
            "photo_count": photo_count if photo_count else None,
            "email": email,
            "website": website,
            "write_review_url": write_review_url,
            "web_url": web_url,
            "ancestor_tid": most_granular if ancestors else None
        })

    conn.commit()

    # 5. Insert Additional Data
    with conn.cursor() as cur:
        # Review Rating Counts
        cur.execute("DELETE FROM tripadvisor_demo.location_review_rating_count WHERE location_id = %s", (location_id,))
        for star, count in location_details.get("review_rating_count", {}).items():
            cur.execute("""
                INSERT INTO tripadvisor_demo.location_review_rating_count (location_id, star_rating, count)
                VALUES (%s, %s, %s)
            """, (location_id, int(star), int(count)))

        # Categories
        cur.execute("DELETE FROM tripadvisor_demo.location_categories WHERE location_id = %s", (location_id,))
        category = location_details.get("category", {})
        subcategories = location_details.get("subcategory", [])
        for cat in [category] + subcategories:
            if cat:
                cur.execute("""
                    INSERT INTO tripadvisor_demo.location_categories (location_id, category_name, localized_name)
                    VALUES (%s, %s, %s)
                """, (location_id, cat.get("name"), cat.get("localized_name")))

        # Groups
        cur.execute("DELETE FROM tripadvisor_demo.location_groups WHERE location_id = %s", (location_id,))
        for group in location_details.get("groups", []):
            for cat in group.get("categories", []):
                cur.execute("""
                    INSERT INTO tripadvisor_demo.location_groups (location_id, group_name, category_name, localized_name)
                    VALUES (%s, %s, %s, %s)
                """, (location_id, group.get("name"), cat.get("name"), cat.get("localized_name")))

        # Awards
        cur.execute("DELETE FROM tripadvisor_demo.location_awards WHERE location_id = %s", (location_id,))
        for award in location_details.get("awards", []):
            cur.execute("""
                INSERT INTO tripadvisor_demo.location_awards (location_id, award_name, award_type, year)
                VALUES (%s, %s, %s, %s)
            """, (location_id, award.get("name"), award.get("type"), award.get("year")))

        # Images
        cur.execute("DELETE FROM tripadvisor_demo.location_images WHERE location_id = %s", (location_id,))
        if location_details.get("see_all_photos"):
            cur.execute("""
                INSERT INTO tripadvisor_demo.location_images (location_id, image_url, description)
                VALUES (%s, %s, %s)
            """, (location_id, location_details["see_all_photos"], "See all photos"))

    conn.commit()

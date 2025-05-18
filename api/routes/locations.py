from flask import Blueprint, jsonify
from db import get_connection
from utils import row_to_dict

bp = Blueprint("locations", __name__)

@bp.route("/api/locations")
def all_locations():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT location_id, name, latitude, longitude, rating,
               num_reviews, address_city, address_postalcode,
               (SELECT ai_category FROM tripadvisor_demo.location_categories_ai c WHERE c.location_id = l.location_id) AS category
        FROM tripadvisor_demo.tripadvisor_locations l
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
    """)
    rows = [row_to_dict(cur, row) for row in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify(rows)

@bp.route("/api/locations/<location_id>")
def location_detail(location_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM tripadvisor_demo.tripadvisor_locations
        WHERE location_id = %s
    """, (location_id,))
    location = row_to_dict(cur, cur.fetchone())

    cur.execute("""
        SELECT published_date, rating, title, body
        FROM tripadvisor_demo.reviews
        WHERE location_id = %s
        ORDER BY published_date DESC
        LIMIT 5
    """, (location_id,))
    reviews = [row_to_dict(cur, row) for row in cur.fetchall()]

    cur.close()
    conn.close()

    location["reviews"] = reviews
    return jsonify(location)

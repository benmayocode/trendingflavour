from flask import Blueprint, jsonify
from db import get_connection

bp = Blueprint("categories", __name__)

@bp.route("/api/categories/trending")
def trending_categories():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT ai_category, COUNT(*) AS count
        FROM tripadvisor_demo.location_categories_ai
        GROUP BY ai_category
        ORDER BY count DESC
        LIMIT 10
    """)
    data = [{"category": row[0], "count": row[1]} for row in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify(data)

from flask import Blueprint, jsonify
from db import get_connection
bp = Blueprint("trends", __name__)
from flask import request

@bp.route("/api/trends/sentiment_over_time")
def sentiment_trend():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            c.ai_category AS category,
            DATE(r.published_date) AS date,
            COUNT(*) AS count,
            AVG(s.sentiment_score) AS avg_sentiment
        FROM tripadvisor_demo.review_sentiment s
        JOIN tripadvisor_demo.reviews r ON s.review_id = r.review_id
        JOIN tripadvisor_demo.location_categories_ai c ON r.location_id = c.location_id
        WHERE c.ai_category IS NOT NULL
        GROUP BY c.ai_category, DATE(r.published_date)
        ORDER BY date ASC;
    """)
    rows = [
        {
            "category": row[0],
            "date": row[1].isoformat(),
            "count": row[2],
            "avg_sentiment": float(row[3])
        }
        for row in cur.fetchall()
    ]

    cur.close()
    conn.close()
    return jsonify(rows)

@bp.route("/api/trends/trending_categories")
def trending_categories():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    WITH review_data AS (
        SELECT
            c.ai_category AS category,
            DATE_TRUNC('week', r.published_date) AS week,
            AVG(s.sentiment_score) AS avg_sentiment
        FROM tripadvisor_demo.review_sentiment s
        JOIN tripadvisor_demo.reviews r ON s.review_id = r.review_id
        JOIN tripadvisor_demo.location_categories_ai c ON r.location_id = c.location_id
        GROUP BY 1, 2
    ),
    ranked AS (
        SELECT
            category,
            week,
            avg_sentiment,
            ROW_NUMBER() OVER (PARTITION BY category ORDER BY week ASC) AS week_num
        FROM review_data
    )
    SELECT
        category,
        REGR_SLOPE(avg_sentiment, week_num) AS sentiment_trend_slope,
        COUNT(*) AS weeks_count
    FROM ranked
    GROUP BY category
    HAVING COUNT(*) >= 3
    ORDER BY sentiment_trend_slope DESC
    LIMIT 10;
    """)
    rows = [dict(zip([desc[0] for desc in cur.description], row)) for row in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify(rows)

@bp.route("/api/reviews/by_category")
def reviews_by_category():
    category = request.args.get("category")
    if not category:
        return jsonify({"error": "Missing category parameter"}), 400

    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT
            r.review_id,
            r.location_id,
            r.published_date,
            r.rating,
            r.title,
            r.body,
            s.sentiment_score,
            s.sentiment_label
        FROM tripadvisor_demo.reviews r
        JOIN tripadvisor_demo.review_sentiment s ON r.review_id = s.review_id
        JOIN tripadvisor_demo.location_categories_ai c ON r.location_id = c.location_id
        WHERE c.ai_category = %s
        ORDER BY r.published_date ASC
    """, (category,))

    columns = [desc[0] for desc in cur.description]
    rows = [dict(zip(columns, row)) for row in cur.fetchall()]

    cur.close()
    conn.close()
    return jsonify(rows)

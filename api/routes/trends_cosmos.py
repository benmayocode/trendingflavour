import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from flask import Blueprint, jsonify, request
from pipelines.tripadvisor.cosmos import get_cosmos_container
import numpy as np
from scipy.stats import linregress

bp = Blueprint("trends_cosmos", __name__)

@bp.route("/api/trends_cosmos/sentiment_over_time")
def sentiment_trend_cosmos():
    cosmos_container = get_cosmos_container("review_sentiment", "/review_id")  # Correct container
    query = """
        SELECT c.category, c.published_date, c.sentiment_score
        FROM c
        WHERE c.type = 'review_sentiment'
    """
    items = list(cosmos_container.query_items(query=query, enable_cross_partition_query=True))

    # Aggregate in Python
    trend = {}
    for item in items:
        cat = item.get("category")
        date = item.get("published_date")[:10] if item.get("published_date") else None
        score = item.get("sentiment_score")

        if not cat or not date or score is None:
            continue

        key = (cat, date)
        if key not in trend:
            trend[key] = {"category": cat, "date": date, "count": 0, "total_score": 0.0}
        trend[key]["count"] += 1
        trend[key]["total_score"] += float(score)

    results = []
    for (cat, date), agg in trend.items():
        results.append({
            "category": cat,
            "date": date,
            "count": agg["count"],
            "avg_sentiment": agg["total_score"] / agg["count"]
        })

    return jsonify(sorted(results, key=lambda r: r["date"]))


@bp.route("/api/trends_cosmos/trending_categories")
def trending_categories_cosmos():
    cosmos_container = get_cosmos_container("review_sentiment", "/category")
    query = """
        SELECT c.category, c.published_date, c.sentiment_score
        FROM c
        WHERE c.type = 'review_sentiment'
    """
    items = list(cosmos_container.query_items(query=query, enable_cross_partition_query=True))


    print (f"Fetched {len(items)} sentiment records from Cosmos DB")
    # Aggregate weekly trend slope
    import datetime
    from collections import defaultdict

    weekly_scores = defaultdict(list)

    for item in items:
        cat = item.get("category")
        date = item.get("published_date")
        score = item.get("sentiment_score")

        if not cat or not date or score is None:
            continue

        dt = datetime.datetime.fromisoformat(date)
        week = dt.date() - datetime.timedelta(days=dt.weekday())
        weekly_scores[cat].append((week, float(score)))

    print (f"Aggregated {len(weekly_scores)} categories with weekly scores")
    trends = []
    for cat, points in weekly_scores.items():
        points.sort()
        if len(points) < 3:
            continue
        weeks = list(range(len(points)))
        scores = [s for (_, s) in points]
        slope, *_ = linregress(weeks, scores)
        trends.append({"category": cat, "sentiment_trend_slope": slope, "weeks_count": len(points)})

    print ('trends',trends)
    return jsonify(sorted(trends, key=lambda t: t["sentiment_trend_slope"], reverse=True)[:10])


@bp.route("/api/reviews_cosmos/by_category")
def reviews_by_category_cosmos():
    category = request.args.get("category")
    if not category:
        return jsonify({"error": "Missing category parameter"}), 400

    cosmos_container = get_cosmos_container("reviews", "/location_id")
    query = """
        SELECT c.review_id, c.title, c.body, c.published_date, c.rating, c.sentiment_label
        FROM c
        WHERE c.type = 'review' AND c.category = @category
        ORDER BY c.published_date ASC
    """
    parameters = [{"name": "@category", "value": category}]
    results = list(cosmos_container.query_items(
        query=query,
        parameters=parameters,
        enable_cross_partition_query=True
    ))

    print(f"Fetched {len(results)} reviews for category {category} from Cosmos DB")
    return jsonify(results)

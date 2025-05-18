from flask import Blueprint, jsonify
from .cosmos import get_cosmos_container

bp = Blueprint("locations_cosmos", __name__)

@bp.route("/api/locations_cosmos")
def all_locations_cosmos():
    results = []
    cosmos_container = get_cosmos_container("locations", "/category")

    for item in cosmos_container.read_all_items():
        if item.get("latitude") is not None and item.get("longitude") is not None:
            results.append({
                "location_id": item.get("location_id"),
                "name": item.get("name"),
                "latitude": item.get("latitude"),
                "longitude": item.get("longitude"),
                "rating": item.get("rating"),
                "num_reviews": item.get("num_reviews"),
                "address_city": item.get("address_city"),
                "address_postalcode": item.get("address_postalcode"),
                "category": item.get("category")
            })

    print(f"Fetched {len(results)} locations from Cosmos DB")
    return jsonify(results)


@bp.route("/api/locations_cosmos/<location_id>")
def location_detail_cosmos(location_id):

    results = list(cosmos_container.query_items(
        query="SELECT * FROM c WHERE c.location_id = @location_id",
        parameters=[{"name": "@location_id", "value": location_id}],
        enable_cross_partition_query=True
    ))

    if not results:
        return jsonify({"error": "Location not found"}), 404

    location = results[0]

    # We don't yet have reviews in Cosmos DB; placeholder empty list
    location["reviews"] = []

    return jsonify(location)

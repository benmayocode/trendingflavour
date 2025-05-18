# pipelines/tripadvisor/fetch_locations.py
import os
import requests
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()  # Load .env into os.environ

TRIPADVISOR_API_KEY = os.getenv("TRIPADVISOR_API_KEY")
API_BASE = "https://api.content.tripadvisor.com/api/v1/location"
HEADERS = {"accept": "application/json"}


def nearby_search(lat: float, lon: float, category: str = "restaurants") -> List[str]:
    """
    Query the TripAdvisor Nearby Search API and return location_ids.
    """
    params = {
        "key": TRIPADVISOR_API_KEY,
        "language": "en",
        "latLong": f"{lat},{lon}",
        "category": category
    }
    response = requests.get(f"{API_BASE}/nearby_search", headers=HEADERS, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()
    return [loc["location_id"] for loc in data.get("data", [])]


def get_details(location_id: str) -> Optional[Dict]:
    """
    Query the TripAdvisor Details API for a single location.
    Returns None if the location is not found or an error occurs.
    """
    params = {
        "key": TRIPADVISOR_API_KEY,
        "language": "en"
    }
    url = f"{API_BASE}/{location_id}/details"
    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Failed to fetch details for {location_id}: {e}")
        return None

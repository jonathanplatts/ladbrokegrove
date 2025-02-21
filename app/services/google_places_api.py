import os
from dotenv import load_dotenv
from typing import Dict, Any
import time

import requests

load_dotenv

API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")


def fetch_places(place_type: str, location: str, radius: float) -> Dict[str, Any]:
    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": location,
        "radius": str(radius),
        "type": place_type,
        "key": API_KEY,
    }

    places = set()

    while True:
        response = requests.get(url, params=params).json()

        if "results" in response:
            for place in response["results"]:
                place_tuple = (
                    place["name"],
                    place["geometry"]["location"]["lat"],
                    place["geometry"]["location"]["lng"],
                    place_type,
                )
                places.add(place_tuple)

        # Pagination
        next_page_token = response.get("next_page_token")
        if not next_page_token:
            break

        # API requires 2s delay before using next_page_token
        time.sleep(2)
        params["pagetoken"] = next_page_token

    return list(places)

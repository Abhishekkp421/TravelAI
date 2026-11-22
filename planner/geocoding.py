
import json
import time
import urllib.parse
import urllib.request

from django.core.cache import cache


NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

# Replace with your own contact email.
USER_AGENT = "TravelAI/1.0 (contact: abhishekpathak231213@gmail.com)"


def get_coordinates(place_name, destination):

    if not place_name or not destination:
        return None

    query = f"{place_name}, {destination}, India"
    cache_key = "travelai_geo_" + str(hash(query.lower()))

    # Check cached coordinates first
    cached_result = cache.get(cache_key)

    if cached_result:
        return cached_result

    try:
        # Respect Nominatim's public rate limit
        last_request = cache.get("travelai_last_geo_request", 0)
        wait_time = 1.1 - (time.time() - last_request)

        if wait_time > 0:
            time.sleep(wait_time)

        cache.set(
            "travelai_last_geo_request",
            time.time(),
            timeout=60
        )

        params = urllib.parse.urlencode({
            "q": query,
            "format": "jsonv2",
            "limit": 1
        })

        url = f"{NOMINATIM_URL}?{params}"

        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": USER_AGENT
            }
        )

        with urllib.request.urlopen(request, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))

        if not data:
            return None

        coordinates = {
            "latitude": float(data[0]["lat"]),
            "longitude": float(data[0]["lon"])
        }

        # Cache successful results for 30 days
        cache.set(cache_key, coordinates, 60 * 60 * 24 * 30)

        return coordinates

    except Exception as error:
        print("Geocoding error:", error)
        return None

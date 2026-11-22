
import json

from google import genai
from django.conf import settings


MODEL_NAME = "gemini-3.5-flash"


# -------------------------------------------------
# GEMINI CONNECTION TEST
# -------------------------------------------------

def test_gemini_connection():

    api_key = settings.GEMINI_API_KEY

    if not api_key:
        return "Gemini API key is missing!"

    try:
        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents="Say: TravelAI Gemini integration successful!"
        )

        return response.text

    except Exception as e:
        return f"Gemini API Error: {str(e)}"


# -------------------------------------------------
# GENERATE AI TRIP PLAN
# -------------------------------------------------

def generate_ai_trip_plan(trip, places, restaurants):

    """
    Generate a personalized trip plan.

    Database records are preferred when available.
    Gemini suggests places and restaurants when database
    records are unavailable.

    Unknown ratings and prices are never presented as verified.
    """

    api_key = settings.GEMINI_API_KEY

    if not api_key:
        print("Gemini API key is missing.")
        return None

    # -------------------------------------------------
    # EXISTING DATABASE DATA
    # -------------------------------------------------

    existing_places = [
        {
            "name": p.name,
            "category": p.category,
            "description": p.description,
        }
        for p in places
    ]

    existing_restaurants = [
        {
            "name": r.name,
            "cuisine": r.cuisine,
            "food_type": r.food_type,
            "price_range": r.price_range,
        }
        for r in restaurants
    ]

    # -------------------------------------------------
    # GEMINI PROMPT
    # -------------------------------------------------

    prompt = f"""
You are TravelAI, an expert travel planning assistant.

Create a useful and personalized travel plan.

TRIP DETAILS:

Destination: {trip.destination}
Duration: {trip.days} days
Number of people: {trip.people}
Total budget: INR {trip.budget}
Food preference: {trip.food_preference}
Travel type: {trip.travel_type}
Interests: {trip.interests}

EXISTING DATABASE PLACES:
{json.dumps(existing_places, ensure_ascii=False)}

EXISTING DATABASE RESTAURANTS:
{json.dumps(existing_restaurants, ensure_ascii=False)}

IMPORTANT INSTRUCTIONS:

1. If database places are provided, do not generate additional places.
2. If no database places are provided, suggest 6 to 8 real,
   well-known attractions in {trip.destination}.

3. If database restaurants are provided, do not generate
   additional restaurants.
4. If no database restaurants are provided, suggest 4 to 6
   real restaurants in {trip.destination}.

5. Do not invent ratings, opening hours, phone numbers or exact prices.
6. Use null for unknown costs.
7. Respect food preference: {trip.food_preference}.
8. Personalize the schedule for {trip.travel_type} travellers.
9. Consider the user's interests: {trip.interests}.
10. Generate exactly {trip.days} itinerary days.
11. Avoid repeating the same attraction unnecessarily.
12. Use only the provided or newly suggested places and restaurants.
13. Consider the total trip budget.
14. Restaurant food_type must be vegetarian,
    non_vegetarian or both.
15. Estimated costs must be clearly treated as estimates.
16. Do not invent database information.
17. Distribute attractions logically across all trip days.
18. Each day should have morning, afternoon and evening activities.
19. Schedule lunch between 1:00 PM and 2:00 PM.
20. Use the exact names of places and restaurants from the lists.

Return ONLY valid JSON in this structure:

{{
    "places": [
        {{
            "name": "Real attraction name",
            "category": "Historical",
            "description": "Short description",
            "estimated_cost": null
        }}
    ],

    "restaurants": [
        {{
            "name": "Real restaurant name",
            "cuisine": "Indian",
            "food_type": "both",
            "price_range": null
        }}
    ],

    "days": [
        {{
            "day": 1,
            "morning_place": "Place name",
            "morning_activity": "Activity description",
            "afternoon_place": "Place name",
            "afternoon_activity": "Activity description",
            "restaurant": "Restaurant name",
            "evening_place": "Place name",
            "evening_activity": "Activity description"
        }}
    ]
}}

If database places are provided, return an empty array
for generated places.

If database restaurants are provided, return an empty array
for generated restaurants.

Use null whenever reliable information is unavailable.
"""

    try:

        # -------------------------------------------------
        # GEMINI API REQUEST
        # -------------------------------------------------

        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config={
                "response_mime_type": "application/json"
            }
        )

        if not response.text:
            raise ValueError(
                "Gemini returned an empty response."
            )

        result = json.loads(response.text)

        if not isinstance(result, dict):
            raise ValueError("Invalid Gemini response format.")

        generated_places = result.get("places", [])
        generated_restaurants = result.get("restaurants", [])
        generated_days = result.get("days", [])

        if not isinstance(generated_places, list):
            generated_places = []

        if not isinstance(generated_restaurants, list):
            generated_restaurants = []

        if not isinstance(generated_days, list):
            generated_days = []

        # -------------------------------------------------
        # COMBINE DATABASE AND GEMINI PLACES
        # -------------------------------------------------

        all_places = []

        existing_place_names = set()

        for place in places:

            place_name = place.name.strip()

            existing_place_names.add(
                place_name.lower()
            )

            all_places.append({
                "name": place_name,
                "category": place.category or "Attraction",
                "description": place.description or "",
                "average_cost": place.average_cost,
                "rating": place.rating,
                "source": "database",
            })

        for place in generated_places:

            if not isinstance(place, dict):
                continue

            name = place.get("name")

            if not name:
                continue

            name = str(name).strip()

            if not name:
                continue

            # Avoid duplicate places
            if name.lower() in existing_place_names:
                continue

            existing_place_names.add(name.lower())

            all_places.append({
                "name": name,
                "category": place.get(
                    "category",
                    "Attraction"
                ),
                "description": place.get(
                    "description",
                    ""
                ),
                "average_cost": place.get(
                    "estimated_cost"
                ),
                "rating": None,
                "source": "gemini",
            })

        # -------------------------------------------------
        # COMBINE DATABASE AND GEMINI RESTAURANTS
        # -------------------------------------------------

        all_restaurants = []

        existing_restaurant_names = set()

        for restaurant in restaurants:

            restaurant_name = restaurant.name.strip()

            existing_restaurant_names.add(
                restaurant_name.lower()
            )

            all_restaurants.append({
                "name": restaurant_name,
                "cuisine": restaurant.cuisine or "Indian",
                "food_type": restaurant.food_type or "both",
                "price_range": restaurant.price_range,
                "rating": restaurant.rating,
                "source": "database",
            })

        for restaurant in generated_restaurants:

            if not isinstance(restaurant, dict):
                continue

            name = restaurant.get("name")

            if not name:
                continue

            name = str(name).strip()

            if not name:
                continue

            # Avoid duplicate restaurants
            if name.lower() in existing_restaurant_names:
                continue

            existing_restaurant_names.add(name.lower())

            food_type = restaurant.get(
                "food_type",
                "both"
            )

            if food_type not in [
                "vegetarian",
                "non_vegetarian",
                "both"
            ]:
                food_type = "both"

            all_restaurants.append({
                "name": name,
                "cuisine": restaurant.get(
                    "cuisine",
                    "Indian"
                ),
                "food_type": food_type,
                "price_range": restaurant.get(
                    "price_range"
                ),
                "rating": None,
                "source": "gemini",
            })

        # -------------------------------------------------
        # CREATE LOOKUP MAPS
        # -------------------------------------------------

        place_map = {
            place["name"].strip().lower(): place
            for place in all_places
        }

        restaurant_map = {
            restaurant["name"].strip().lower(): restaurant
            for restaurant in all_restaurants
        }

        # -------------------------------------------------
        # BUILD ITINERARY
        # -------------------------------------------------

        itinerary = []

        for day_number in range(1, trip.days + 1):

            item = {}

            for generated_day in generated_days:

                if not isinstance(generated_day, dict):
                    continue

                try:
                    generated_day_number = int(
                        generated_day.get("day", 0)
                    )
                except (ValueError, TypeError):
                    continue

                if generated_day_number == day_number:
                    item = generated_day
                    break

            if not item:
                continue

            # -------------------------------------------------
            # GET PLACE DETAILS
            # -------------------------------------------------

            def get_place(name, activity):

                if not name:
                    return None

                place = place_map.get(
                    str(name).strip().lower()
                )

                if not place:
                    return None

                return {
                    "name": place["name"],
                    "category": place["category"],
                    "description": (
                        activity or place["description"]
                    ),
                    "rating": place["rating"],
                    "average_cost": place["average_cost"],
                    "source": place["source"],
                    "is_ai_generated": (
                        place["source"] == "gemini"
                    ),
                }

            # -------------------------------------------------
            # GET RESTAURANT DETAILS
            # -------------------------------------------------

            restaurant_name = item.get("restaurant")

            restaurant_info = None

            if restaurant_name:

                restaurant = restaurant_map.get(
                    str(restaurant_name).strip().lower()
                )

                if restaurant:

                    restaurant_info = {
                        "name": restaurant["name"],
                        "cuisine": restaurant["cuisine"],
                        "food_type": restaurant["food_type"],
                        "price_range": restaurant["price_range"],
                        "rating": restaurant["rating"],
                        "source": restaurant["source"],
                        "is_ai_generated": (
                            restaurant["source"] == "gemini"
                        ),
                    }

            # -------------------------------------------------
            # DAY INFORMATION
            # -------------------------------------------------

            morning = get_place(
                item.get("morning_place"),
                item.get("morning_activity")
            )

            afternoon = get_place(
                item.get("afternoon_place"),
                item.get("afternoon_activity")
            )

            evening = get_place(
                item.get("evening_place"),
                item.get("evening_activity")
            )

            # Do not add completely empty itinerary days
            if not any([
                morning,
                afternoon,
                restaurant_info,
                evening
            ]):
                continue

            itinerary.append({
                "day": day_number,
                "morning": morning,
                "afternoon": afternoon,
                "restaurant": restaurant_info,
                "evening": evening,
            })

        # -------------------------------------------------
        # FINAL RESPONSE
        # -------------------------------------------------

        return {
            "places": all_places,
            "restaurants": all_restaurants,
            "itinerary": itinerary,
        }

    except Exception as e:

        print(
            "Gemini trip plan error:",
            str(e)
        )

        return None

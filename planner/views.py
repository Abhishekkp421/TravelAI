from .geocoding import get_coordinates
from types import SimpleNamespace
from .gemini_service import generate_ai_trip_plan
from decimal import Decimal

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Avg

from .models import Trip, Place, Restaurant, Review
from .forms import TripForm, RegisterForm, ReviewForm


# -------------------------------------------------
# HOME
# -------------------------------------------------

def home(request):
    return render(
        request,
        "planner/home.html"
    )


# -------------------------------------------------
# LOGIN
# -------------------------------------------------
def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = RegisterForm()

    return render(
        request,
        "planner/register.html",
        {"form": form}
    )
def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            next_url = request.GET.get("next")

            if next_url:
                return redirect(next_url)

            return redirect("home")

        return render(
            request,
            "planner/login.html",
            {
                "error": "Invalid username or password."
            }
        )

    return render(
        request,
        "planner/login.html"
    )


# -------------------------------------------------
# LOGOUT
# -------------------------------------------------

def logout_view(request):

    logout(request)

    return redirect("home")


# -------------------------------------------------
# MY TRIPS
# -------------------------------------------------

@login_required
def my_trips(request):

    trips = Trip.objects.filter(
        user=request.user
    ).order_by("-created_at")

    return render(
        request,
        "planner/my_trips.html",
        {
            "trips": trips
        }
    )


# -------------------------------------------------
# DELETE TRIP
# -------------------------------------------------

@login_required
def delete_trip(request, trip_id):

    trip = Trip.objects.get(
        id=trip_id,
        user=request.user
    )

    if request.method == "POST":
        trip.delete()

    return redirect("my_trips")


# -------------------------------------------------
# PROFILE
# -------------------------------------------------

@login_required
def profile(request):

    trips_count = Trip.objects.filter(
        user=request.user
    ).count()

    return render(
        request,
        "planner/profile.html",
        {
            "trips_count": trips_count
        }
    )


# -------------------------------------------------
# PLAN TRIP
# -------------------------------------------------

@login_required
def plan_trip(request):

    if request.method == "POST":

        form = TripForm(request.POST)

        if form.is_valid():

            trip = form.save(commit=False)

            trip.user = request.user

            trip.save()

            return render(
                request,
                "planner/trip_success.html",
                {
                    "trip": trip
                }
            )

    else:

        form = TripForm()

    return render(
        request,
        "planner/plan_trip.html",
        {
            "form": form
        }
    )


# -------------------------------------------------
# TRIP RESULT
# -------------------------------------------------






@login_required
def trip_result(request, trip_id):

    trip = get_object_or_404(
        Trip,
        id=trip_id,
        user=request.user
    )

    # -------------------------------------------------
    # USER INTERESTS
    # -------------------------------------------------

    interests = [
        interest.strip().lower()
        for interest in (trip.interests or "").split(",")
        if interest.strip()
    ]

    # -------------------------------------------------
    # DATABASE PLACES
    # -------------------------------------------------

    all_places = Place.objects.filter(
        destination__iexact=trip.destination
    ).order_by("-rating")

    scored_places = []

    for place in all_places:

        score = 0
        category = (place.category or "").lower()

        for interest in interests:
            if interest in category:
                score += 10

        score += float(place.rating or 0) * 2

        if place.average_cost is not None:
            estimated_cost = (
                float(place.average_cost) * trip.people
            )

            if estimated_cost <= float(trip.budget):
                score += 5
            else:
                score -= 2

        travel_type = (trip.travel_type or "").lower()

        if travel_type == "family":
            if any(word in category for word in [
                "historical", "spiritual", "nature", "scenic"
            ]):
                score += 5

        elif travel_type == "couple":
            if any(word in category for word in [
                "scenic", "nature", "romantic"
            ]):
                score += 5

        elif travel_type == "friends":
            if any(word in category for word in [
                "adventure", "shopping", "nature"
            ]):
                score += 5

        elif travel_type == "solo":
            if any(word in category for word in [
                "adventure", "historical", "spiritual", "shopping"
            ]):
                score += 5

        scored_places.append((place, score))

    scored_places.sort(
        key=lambda item: item[1],
        reverse=True
    )

    recommended_places = [
        place for place, score in scored_places
    ]

    # -------------------------------------------------
    # DATABASE PLACE REVIEWS
    # -------------------------------------------------

    for place in recommended_places:

        place.is_ai_generated = False

        place.user_reviews = Review.objects.filter(
            place=place
        ).select_related("user").order_by("-created_at")

        place.review_count = place.user_reviews.count()

        place.user_average = place.user_reviews.aggregate(
            average=Avg("rating")
        )["average"]

    # -------------------------------------------------
    # DATABASE RESTAURANTS
    # -------------------------------------------------

    restaurants = Restaurant.objects.filter(
        destination__iexact=trip.destination
    )

    scored_restaurants = []

    for restaurant in restaurants:

        score = 0

        if restaurant.food_type == trip.food_preference:
            score += 10

        if restaurant.food_type == "both":
            score += 7

        score += float(restaurant.rating or 0) * 2

        scored_restaurants.append((restaurant, score))

    scored_restaurants.sort(
        key=lambda item: item[1],
        reverse=True
    )

    recommended_restaurants = [
        restaurant
        for restaurant, score in scored_restaurants
    ]

    # -------------------------------------------------
    # RESTAURANT REVIEWS
    # -------------------------------------------------

    for restaurant in recommended_restaurants:

        restaurant.is_ai_generated = False

        restaurant.user_reviews = Review.objects.filter(
            restaurant=restaurant
        ).select_related("user").order_by("-created_at")

        restaurant.review_count = restaurant.user_reviews.count()

        restaurant.user_average = restaurant.user_reviews.aggregate(
            average=Avg("rating")
        )["average"]

    # -------------------------------------------------
    # GEMINI AI TRIP PLAN
    # -------------------------------------------------

    ai_plan = generate_ai_trip_plan(
        trip,
        recommended_places,
        recommended_restaurants
    )

    itinerary = []
    itinerary_source = "Rule-based fallback"

    if ai_plan:

        database_place_map = {
            p.name.strip().lower(): p
            for p in recommended_places
        }

        database_restaurant_map = {
            r.name.strip().lower(): r
            for r in recommended_restaurants
        }

        # -------------------------------------------------
        # FINAL PLACES
        # -------------------------------------------------

        final_places = []

        for item in ai_plan.get("places", []):

            if not isinstance(item, dict) or not item.get("name"):
                continue

            place_name = item["name"].strip().lower()

            if item.get("source") == "database":

                place = database_place_map.get(place_name)

                if place:
                    place.is_ai_generated = False
                    final_places.append(place)

            else:

                final_places.append(
                    SimpleNamespace(
                        id=None,
                        name=item["name"],
                        category=item.get(
                            "category",
                            "Attraction"
                        ),
                        description=item.get(
                            "description",
                            ""
                        ),
                        average_cost=item.get(
                            "average_cost"
                        ),
                        rating=None,
                        latitude=None,
                        longitude=None,
                        is_ai_generated=True,
                        review_count=0,
                        user_reviews=[],
                        user_average=None,
                    )
                )

        # -------------------------------------------------
        # FINAL RESTAURANTS
        # -------------------------------------------------

        final_restaurants = []

        for item in ai_plan.get("restaurants", []):

            if not isinstance(item, dict) or not item.get("name"):
                continue

            restaurant_name = item["name"].strip().lower()

            if item.get("source") == "database":

                restaurant = database_restaurant_map.get(
                    restaurant_name
                )

                if restaurant:
                    restaurant.is_ai_generated = False
                    final_restaurants.append(restaurant)

            else:

                final_restaurants.append(
                    SimpleNamespace(
                        id=None,
                        name=item["name"],
                        cuisine=item.get(
                            "cuisine",
                            "Indian"
                        ),
                        food_type=item.get(
                            "food_type",
                            "both"
                        ),
                        price_range=item.get(
                            "price_range"
                        ),
                        rating=None,
                        latitude=None,
                        longitude=None,
                        is_ai_generated=True,
                        review_count=0,
                        user_reviews=[],
                        user_average=None,
                    )
                )

        if final_places:
            recommended_places = final_places

        if final_restaurants:
            recommended_restaurants = final_restaurants

        itinerary = ai_plan.get("itinerary", [])

        if itinerary:
            itinerary_source = "Gemini AI"

    # -------------------------------------------------
    # GEOCODING - PLACES
    # -------------------------------------------------

    for place in recommended_places:

        if (
            getattr(place, "latitude", None) is None
            or getattr(place, "longitude", None) is None
        ):

            coordinates = get_coordinates(
                place.name,
                trip.destination
            )

            if coordinates:

                place.latitude = coordinates["latitude"]
                place.longitude = coordinates["longitude"]

                if place.id is not None:
                    place.save(
                        update_fields=[
                            "latitude",
                            "longitude"
                        ]
                    )

    # -------------------------------------------------
    # GEOCODING - RESTAURANTS
    # -------------------------------------------------

    for restaurant in recommended_restaurants:

        if (
            getattr(restaurant, "latitude", None) is None
            or getattr(restaurant, "longitude", None) is None
        ):

            coordinates = get_coordinates(
                restaurant.name,
                trip.destination
            )

            if coordinates:

                restaurant.latitude = coordinates["latitude"]
                restaurant.longitude = coordinates["longitude"]

                if restaurant.id is not None:
                    restaurant.save(
                        update_fields=[
                            "latitude",
                            "longitude"
                        ]
                    )

    # -------------------------------------------------
    # FALLBACK ITINERARY
    # -------------------------------------------------

    if not itinerary:

        place_index = 0
        restaurant_index = 0

        for day in range(1, trip.days + 1):

            morning = None
            afternoon = None
            evening = None
            restaurant = None

            if place_index < len(recommended_places):
                morning = recommended_places[place_index]
                place_index += 1

            if place_index < len(recommended_places):
                afternoon = recommended_places[place_index]
                place_index += 1

            if place_index < len(recommended_places):
                evening = recommended_places[place_index]
                place_index += 1

            if restaurant_index < len(recommended_restaurants):
                restaurant = recommended_restaurants[
                    restaurant_index
                ]
                restaurant_index += 1

            itinerary.append({
                "day": day,
                "morning": morning,
                "afternoon": afternoon,
                "restaurant": restaurant,
                "evening": evening,
            })

    # -------------------------------------------------
    # BUDGET BREAKDOWN
    # -------------------------------------------------

    total_budget = Decimal(str(trip.budget))

    hotel_budget = total_budget * Decimal("0.30")
    food_budget = total_budget * Decimal("0.20")
    travel_budget = total_budget * Decimal("0.15")
    activity_budget = total_budget * Decimal("0.25")
    misc_budget = total_budget * Decimal("0.10")

    # -------------------------------------------------
    # RECOMMENDATION MESSAGE
    # -------------------------------------------------

    if interests:

        interest_text = ", ".join(
            interest.title()
            for interest in interests
        )

        recommendation_message = (
            f"Your trip is personalized around {interest_text} "
            f"interests, your budget and your travel preferences."
        )

    else:

        recommendation_message = (
            "Your trip is personalized using your destination, "
            "budget and travel preferences."
        )

    # -------------------------------------------------
    # CONTEXT
    # -------------------------------------------------

    context = {
        "trip": trip,
        "recommended_places": recommended_places,
        "recommended_restaurants": recommended_restaurants,
        "itinerary": itinerary,
        "itinerary_source": itinerary_source,
        "recommendation_message": recommendation_message,
        "hotel_budget": hotel_budget,
        "food_budget": food_budget,
        "travel_budget": travel_budget,
        "activity_budget": activity_budget,
        "misc_budget": misc_budget,
        "total_budget": total_budget,
    }

    return render(
        request,
        "planner/trip_result.html",
        context
    )


@login_required
def add_review(request, place_id=None, restaurant_id=None):

    if request.method == "POST":

        form = ReviewForm(request.POST)

        if form.is_valid():

            review = form.save(commit=False)

            review.user = request.user

            if place_id:
                review.place_id = place_id

            if restaurant_id:
                review.restaurant_id = restaurant_id

            review.save()

    return redirect(request.META.get("HTTP_REFERER", "home"))
@login_required
def add_restaurant_review(request, restaurant_id):

    restaurant = Restaurant.objects.get(
        id=restaurant_id
    )

    if request.method == "POST":

        rating = request.POST.get("rating")
        review_text = request.POST.get("review_text")

        if rating and review_text:

            Review.objects.create(
                user=request.user,
                restaurant=restaurant,
                rating=int(rating),
                review_text=review_text
            )

    return redirect(
        "trip_result",
        trip_id=request.POST.get("trip_id")
    )
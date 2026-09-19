from decimal import Decimal

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
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

    # -------------------------------------------------
    # GET TRIP
    # -------------------------------------------------

    trip = Trip.objects.get(
        id=trip_id,
        user=request.user
    )

    # -------------------------------------------------
    # USER INTERESTS
    # -------------------------------------------------

    interests = [
        interest.strip().lower()
        for interest in trip.interests.split(",")
        if interest.strip()
    ]

    # -------------------------------------------------
    # ALL PLACES FOR DESTINATION
    # -------------------------------------------------

    all_places = Place.objects.filter(
        destination__iexact=trip.destination
    ).order_by("-rating")

    # -------------------------------------------------
    # AI PLACE RECOMMENDATION SCORING
    # -------------------------------------------------

    scored_places = []

    for place in all_places:

        score = 0

        category = place.category.lower()

        # -------------------------------------------------
        # INTEREST MATCHING
        # -------------------------------------------------

        for interest in interests:

            if interest in category:
                score += 10

        # -------------------------------------------------
        # RATING SCORE
        # -------------------------------------------------

        score += float(place.rating) * 2

        # -------------------------------------------------
        # BUDGET CONSIDERATION
        # -------------------------------------------------

        if place.average_cost:

            estimated_cost = (
                float(place.average_cost) * trip.people
            )

            if estimated_cost <= float(trip.budget):
                score += 5
            else:
                score -= 2

        # -------------------------------------------------
        # TRAVEL TYPE PERSONALIZATION
        # -------------------------------------------------

        travel_type = trip.travel_type.lower()

        # FAMILY
        if travel_type == "family":

            if any(
                word in category
                for word in [
                    "historical",
                    "spiritual",
                    "nature",
                    "scenic"
                ]
            ):
                score += 5

        # COUPLE
        elif travel_type == "couple":

            if any(
                word in category
                for word in [
                    "scenic",
                    "nature",
                    "romantic"
                ]
            ):
                score += 5

        # FRIENDS
        elif travel_type == "friends":

            if any(
                word in category
                for word in [
                    "adventure",
                    "shopping",
                    "nature"
                ]
            ):
                score += 5

        # SOLO
        elif travel_type == "solo":

            if any(
                word in category
                for word in [
                    "adventure",
                    "historical",
                    "spiritual",
                    "shopping"
                ]
            ):
                score += 5

        # -------------------------------------------------
        # SAVE PLACE WITH SCORE
        # -------------------------------------------------

        scored_places.append(
            (place, score)
        )

    # -------------------------------------------------
    # SORT PLACES BY AI SCORE
    # -------------------------------------------------

    scored_places.sort(
        key=lambda item: item[1],
        reverse=True
    )

    # -------------------------------------------------
    # FINAL RECOMMENDED PLACES
    # -------------------------------------------------

    recommended_places = [
        place
        for place, score in scored_places
   ]

    for place in recommended_places:

        place.user_reviews = Review.objects.filter(
            place=place
        ).select_related("user").order_by("-created_at")

        place.review_count = place.user_reviews.count()

        place.user_average = place.user_reviews.aggregate(
            average=Avg("rating")
        )["average"]

    # -------------------------------------------------
    # RESTAURANT RECOMMENDATIONS
    # -------------------------------------------------

    restaurants = Restaurant.objects.filter(
        destination__iexact=trip.destination
    )

    # -------------------------------------------------
    # AI RESTAURANT RECOMMENDATION SCORING
    # -------------------------------------------------

    scored_restaurants = []

    for restaurant in restaurants:

        score = 0

        # Food preference match
        if restaurant.food_type == trip.food_preference:
            score += 10

        # Both is suitable for everyone
        if restaurant.food_type == "both":
            score += 7

        # Rating score
        score += float(restaurant.rating) * 2

        # Save restaurant with score
        scored_restaurants.append(
            (restaurant, score)
        )

    # -------------------------------------------------
    # SORT RESTAURANTS BY AI SCORE
    # -------------------------------------------------

    scored_restaurants.sort(
        key=lambda item: item[1],
        reverse=True
    )

   # -------------------------------------------------
   # FINAL RECOMMENDED RESTAURANTS
   # -------------------------------------------------

    recommended_restaurants = [
        restaurant
        for restaurant, score in scored_restaurants
   ]

    for restaurant in recommended_restaurants:

        restaurant.user_reviews = Review.objects.filter(
            restaurant=restaurant
        ).select_related("user").order_by("-created_at")

        restaurant.review_count = restaurant.user_reviews.count()

        restaurant.user_average = restaurant.user_reviews.aggregate(
            average=Avg("rating")
    )["average"]

    total_budget = Decimal(trip.budget)

    # -------------------------------------------------
    # BUDGET BREAKDOWN
    # -------------------------------------------------

    total_budget = Decimal(trip.budget)

    hotel_budget = (
        total_budget * Decimal("0.30")
    )

    food_budget = (
        total_budget * Decimal("0.20")
    )

    travel_budget = (
        total_budget * Decimal("0.15")
    )

    activity_budget = (
        total_budget * Decimal("0.25")
    )

    misc_budget = (
        total_budget * Decimal("0.10")
    )

    # -------------------------------------------------
    # DAY-WISE AI ITINERARY
    # -------------------------------------------------

    itinerary = []

    place_index = 0
    restaurant_index = 0

    for day in range(1, trip.days + 1):

        morning = None
        afternoon = None
        evening = None
        restaurant = None

        # -------------------------------------------------
        # MORNING
        # -------------------------------------------------

        if place_index < len(recommended_places):

            morning = recommended_places[place_index]

            place_index += 1

        # -------------------------------------------------
        # AFTERNOON
        # -------------------------------------------------

        if place_index < len(recommended_places):

            afternoon = recommended_places[place_index]

            place_index += 1

        # -------------------------------------------------
        # EVENING
        # -------------------------------------------------

        if place_index < len(recommended_places):

            evening = recommended_places[place_index]

            place_index += 1

        # -------------------------------------------------
        # FOOD RECOMMENDATION
        # -------------------------------------------------

        if restaurant_index < len(recommended_restaurants):

            restaurant = recommended_restaurants[
                restaurant_index
            ]

            restaurant_index += 1

        # -------------------------------------------------
        # ADD DAY
        # -------------------------------------------------

        itinerary.append(
            {
                "day": day,
                "morning": morning,
                "afternoon": afternoon,
                "restaurant": restaurant,
                "evening": evening,
            }
        )

    # -------------------------------------------------
    # AI RECOMMENDATION MESSAGE
    # -------------------------------------------------

    if interests:

        interest_text = ", ".join(
            interest.title()
            for interest in interests
        )

        recommendation_message = (
            f"Your trip is personalized around "
            f"{interest_text} interests. "
            f"We selected highly-rated places "
            f"and restaurants that match your trip."
        )

    else:

        recommendation_message = (
            "Your itinerary is optimized using "
            "high-rated places and your trip preferences."
        )

    # -------------------------------------------------
    # CONTEXT
    # -------------------------------------------------

    context = {

        "trip": trip,

        "recommended_places":
            recommended_places,

        "recommended_restaurants":
            recommended_restaurants,

        "itinerary":
            itinerary,

        "recommendation_message":
            recommendation_message,

        "hotel_budget":
            hotel_budget,

        "food_budget":
            food_budget,

        "travel_budget":
            travel_budget,

        "activity_budget":
            activity_budget,

        "misc_budget":
            misc_budget,

        "total_budget":
            total_budget,
    }

    # -------------------------------------------------
    # RENDER RESULT PAGE
    # -------------------------------------------------

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
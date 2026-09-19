from django.contrib import admin
from .models import Trip, Place, Restaurant, Review


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = (
        "destination",
        "user",
        "days",
        "people",
        "budget",
        "food_preference",
        "travel_type",
        "created_at",
    )
    list_filter = ("destination", "food_preference", "travel_type")
    search_fields = ("destination", "user__username")


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "destination",
        "category",
        "average_cost",
        "rating",
    )
    list_filter = ("destination", "category")
    search_fields = ("name", "destination", "category")


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "destination",
        "cuisine",
        "price_range",
        "rating",
        "food_type",
    )
    list_filter = ("destination", "cuisine", "food_type")
    search_fields = ("name", "destination", "cuisine")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "place",
        "restaurant",
        "rating",
        "created_at",
    )
    list_filter = ("rating",)
    search_fields = ("user__username", "review_text")

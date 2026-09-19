from django.urls import path

from . import views


urlpatterns = [

    path(
        "",
        views.home,
        name="home"
    ),

    path(
        "login/",
        views.login_view,
        name="login"
    ),
    path("register/", views.register_view, name="register"),
    path("review/place/<int:place_id>/", views.add_review, name="add_place_review"),


    path(
        "logout/",
        views.logout_view,
        name="logout"
    ),
    path(
    "my-trips/",
    views.my_trips,
    name="my_trips"
   ),
   path(
    "delete-trip/<int:trip_id>/",
    views.delete_trip,
    name="delete_trip"
   ),
   path(
    "profile/",
    views.profile,
    name="profile"
   ),
    path(
        "plan/",
        views.plan_trip,
        name="plan_trip"
    ),

    path(
        "trip-result/<int:trip_id>/",
        views.trip_result,
        name="trip_result"
    ),
    path(
    "add-restaurant-review/<int:restaurant_id>/",
    views.add_restaurant_review,
    name="add_restaurant_review"
),

]
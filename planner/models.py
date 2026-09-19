from django.db import models
from django.contrib.auth.models import User


class Trip(models.Model):
    FOOD_CHOICES = [
        ("vegetarian", "Vegetarian"),
        ("non_vegetarian", "Non-Vegetarian"),
        ("both", "Both"),
    ]

    TRAVEL_TYPE_CHOICES = [
        ("solo", "Solo"),
        ("couple", "Couple"),
        ("family", "Family"),
        ("friends", "Friends"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    destination = models.CharField(max_length=100)
    days = models.PositiveIntegerField()
    people = models.PositiveIntegerField()
    budget = models.DecimalField(max_digits=10, decimal_places=2)

    food_preference = models.CharField(
        max_length=30,
        choices=FOOD_CHOICES
    )

    travel_type = models.CharField(
        max_length=30,
        choices=TRAVEL_TYPE_CHOICES
    )

    interests = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.destination} - {self.user.username}"


class Place(models.Model):
    name = models.CharField(max_length=150)
    destination = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    average_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=0
    )
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Restaurant(models.Model):
    FOOD_TYPE_CHOICES = [
        ("vegetarian", "Vegetarian"),
        ("non_vegetarian", "Non-Vegetarian"),
        ("both", "Both"),
    ]

    name = models.CharField(max_length=150)
    destination = models.CharField(max_length=100)
    cuisine = models.CharField(max_length=100)
    price_range = models.CharField(max_length=50)
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=0
    )
    food_type = models.CharField(
        max_length=30,
        choices=FOOD_TYPE_CHOICES
    )

    def __str__(self):
        return self.name


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    place = models.ForeignKey(
        Place,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    rating = models.PositiveIntegerField()
    review_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.rating}"
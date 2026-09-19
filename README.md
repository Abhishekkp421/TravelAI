# ✈️ TravelAI – AI-Based Personalized Travel Planner

TravelAI is a Django-based web application that helps users create personalized travel plans according to their destination, budget, travel type, food preference, and interests.

The system provides place recommendations, restaurant recommendations, budget breakdown, and a day-wise itinerary.

## 🚀 Features

- 👤 User Registration and Login
- 🔐 User Authentication
- 🗺️ Personalized Trip Planning
- 🤖 AI-Based Place Recommendations
- 🍴 Restaurant Recommendations
- 💰 Budget Breakdown
- 📅 Day-Wise Travel Itinerary
- ⭐ Place Reviews and Ratings
- ⭐ Restaurant Reviews and Ratings
- 🧳 My Trips
- 👤 User Profile
- 🗑️ Delete Saved Trips
- 📊 Admin Dashboard

## 🧠 Recommendation System

TravelAI currently uses a rule-based scoring system for personalization.

### Place Recommendation

Places are scored using:

- User interest matching
- Existing place rating
- Budget consideration
- Travel type personalization

Places with higher scores are recommended first.

### Restaurant Recommendation

Restaurants are scored using:

- Food preference matching
- Restaurant rating
- Compatibility with both vegetarian and non-vegetarian preferences

## 💰 Budget Breakdown

The selected trip budget is divided into:

| Category | Percentage |
|----------|------------|
| Hotel | 30% |
| Food | 20% |
| Travel | 15% |
| Activities | 25% |
| Miscellaneous | 10% |

## 📅 Itinerary

The application automatically creates a day-wise itinerary based on the recommended places and restaurants.

Each day can contain:

- Morning activity
- Afternoon activity
- Restaurant recommendation
- Evening activity

## ⭐ Reviews & Ratings

Users can submit reviews and ratings for:

- Tourist places
- Restaurants

The application displays:

- Review count
- Average user rating
- Username
- Rating stars
- Review text
- Review date

## 🛠️ Technology Stack

### Backend
- Python
- Django
- Django ORM

### Frontend
- HTML5
- CSS3
- JavaScript

### Database
- SQLite

### Tools
- Visual Studio Code
- Git
- GitHub

## 📁 Project Structure

```text
TravelAI/
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── planner/
│   ├── migrations/
│   ├── templates/
│   ├── static/
│   ├── admin.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
│
├── planner_seed_data_complete.json
├── manage.py
├── .gitignore
└── README.md
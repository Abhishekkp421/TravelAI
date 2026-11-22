# ✈️ TravelAI – AI-Based Personalized Travel Planner

TravelAI is a Django-based web application that helps users create personalized travel plans according to their destination, budget, travel type, food preference, and interests.

The application combines a rule-based recommendation system with Google's Gemini AI to generate personalized travel suggestions, recommend tourist attractions and restaurants, create day-wise itineraries, and provide budget breakdowns.

It also includes user authentication, trip management, reviews and ratings, and an interactive map to explore recommended locations.

## 🚀 Features

- 👤 User Registration and Login
- 🔐 User Authentication
- 🗺️ Personalized Trip Planning
- 🤖 Gemini AI-Based Travel Suggestions
- 📍 Tourist Place Recommendations
- 🍴 Restaurant Recommendations
- 💰 Smart Budget Breakdown
- 📅 AI-Assisted Day-Wise Travel Itinerary
- ⭐ Place Reviews and Ratings
- ⭐ Restaurant Reviews and Ratings
- 📊 Average User Ratings and Review Counts
- 🗺️ Interactive Map with Location Markers
- 📌 Location Popups with Place Information
- 🧳 My Trips – View Saved Trips
- 👤 User Profile
- 🗑️ Delete Saved Trips
- 📊 Admin Dashboard

## 🧠 Recommendation System

TravelAI uses a hybrid recommendation approach that combines rule-based scoring and Gemini AI.

### 1. Place Recommendation

Tourist places are ranked using a rule-based scoring system based on:

- User interest matching
- Existing place ratings
- Budget consideration
- Travel type personalization

Places with higher scores are prioritized in recommendations.

Gemini AI can also generate additional travel suggestions when suitable database recommendations are unavailable.

### 2. Restaurant Recommendation

Restaurants are recommended using:

- Food preference matching
- Restaurant ratings
- Vegetarian and non-vegetarian preferences
- Available restaurant information

Gemini AI can provide additional restaurant suggestions when required.

### 3. Gemini AI Integration

Google Gemini AI is used to generate personalized travel recommendations and itinerary suggestions based on the user's trip details.

The AI-generated content can include:

- Additional tourist attraction suggestions
- Restaurant suggestions
- Personalized travel recommendations
- Day-wise travel schedules

Database records and AI-generated suggestions are handled separately to distinguish available database information from AI-generated estimates.

**Note:** AI-generated prices, ratings, and availability are suggestions and are not independently verified.

## 💰 Budget Breakdown

The selected trip budget is divided into five categories:

| Category | Percentage |
|---|---:|
| Hotel | 30% |
| Food | 20% |
| Travel | 15% |
| Activities | 25% |
| Miscellaneous | 10% |
| **Total** | **100%** |

The application displays an estimated budget allocation according to the selected trip budget.

## 📅 Day-Wise Itinerary

TravelAI generates a personalized itinerary based on the trip duration and recommended places and restaurants.

Each day can contain:

- 🌅 Morning activity
- ☀️ Afternoon activity
- 🍽️ Restaurant recommendation
- 🌆 Evening activity

The itinerary includes available place descriptions, categories, cost information, and rating information.

## 🗺️ Interactive Travel Map

TravelAI provides an interactive map using Leaflet.js and OpenStreetMap.

Map features include:

- Displaying recommended tourist attractions
- Displaying recommended restaurants
- Different colored markers for attractions and restaurants
- Clickable markers with location information
- Automatic map positioning based on available coordinates

**Map Technologies:** Leaflet.js and OpenStreetMap.

## ⭐ Reviews and Ratings

Users can submit reviews and ratings for:

- Tourist places
- Restaurants

The application displays:

- Total review count
- Average user rating
- Username
- Rating stars
- Review text
- Review date

This feature allows users to share their experiences and view feedback from other users.

## 🧳 Trip Management

Authenticated users can:

- Create personalized trips
- View their saved trips
- Access previously generated trip plans
- Delete saved trips
- Manage their profile

## 🛠️ Technology Stack

### Backend
- Python
- Django
- Django ORM

### Frontend
- HTML5
- CSS3
- JavaScript
- Bootstrap (where used)

### Database
- SQLite

### AI Integration
- Google Gemini API
- `google-genai` Python SDK

### Maps
- Leaflet.js
- OpenStreetMap

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
```

## ⚙️ Installation and Setup

### 1. Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

### 2. Open the Project Directory

```bash
cd TravelAI
```

### 3. Create a Virtual Environment

```bash
python -m venv venv
```

### 4. Activate the Virtual Environment

Windows:

```bash
venv\Scripts\activate
```

### 5. Install Dependencies

```bash
pip install django google-genai
```

Install any additional packages used by your project.

### 6. Configure Gemini API

Configure your Gemini API key before using AI-powered features. Keep the API key private and do not commit it to GitHub.

### 7. Apply Database Migrations

```bash
python manage.py migrate
```

### 8. Create an Admin Account

```bash
python manage.py createsuperuser
```

### 9. Start the Development Server

```bash
python manage.py runserver
```

Open the application in your browser:

```text
http://127.0.0.1:8000/
```

## 🔮 Future Enhancements

- Weather-based travel recommendations
- Hotel recommendations and booking integration
- Real-time travel cost estimation
- Route optimization between recommended places
- Downloadable PDF travel itineraries
- Improved recommendation accuracy using user feedback
- Deployment to a cloud platform

## 👨‍💻 Project Information

**Project Name:** TravelAI – AI-Based Personalized Travel Planner

**Project Type:** Django-Based Web Application / Mini Project

**Core Technologies:** Python, Django, SQLite, JavaScript, Google Gemini AI, Leaflet.js

**Purpose:** To simplify travel planning through personalized recommendations, AI-assisted itinerary generation, and interactive location exploration.

---

**TravelAI – Plan Smarter, Travel Better! ✈️**
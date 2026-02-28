# Architecture

## Overview

NutriMatch is a Flask-based web application that provides personalized meal recommendations based on user health data, dietary preferences, and medical conditions. It features a curated catalog of South Indian restaurants with detailed nutritional information for each menu item.

## Architecture Diagram

```mermaid
flowchart TB
    subgraph Client["Client Layer"]
        Browser["Browser"]
        JS["main.js"]
        CSS["style.css"]
    end

    subgraph Server["Flask Application"]
        subgraph Routes
            Auth["Auth Routes\n/login, /register, /logout"]
            Main["Main Routes\n/"]
            Restaurants["Restaurant Routes\n/home, /restaurant/<id>"]
            Profile["Profile Routes\n/profile, /sync_fitbit"]
            Cart["Cart Routes\n/cart, /add_to_cart, /update_cart"]
        end

        subgraph Services
            Recommender["FoodRecommender\nml_recommender.py"]
        end

        subgraph Models
            User["User"]
            HealthData["HealthData"]
            HealthCondition["HealthCondition"]
            UserPreference["UserPreference"]
            Restaurant["Restaurant"]
            MenuItem["MenuItem"]
            CartItem["CartItem"]
        end
    end

    subgraph Data["Data Layer"]
        SQLite["SQLite (health_food.db)"]
    end

    Browser --> Auth
    Browser --> Main
    Browser --> Restaurants
    Browser --> Profile
    Browser --> Cart
    Browser --> JS
    Browser --> CSS

    Auth --> User
    Profile --> HealthData
    Profile --> HealthCondition
    Profile --> UserPreference
    Restaurants --> Restaurant
    Restaurants --> MenuItem
    Restaurants --> Recommender
    Cart --> CartItem
    Cart --> MenuItem

    Recommender --> HealthData
    Recommender --> HealthCondition
    Recommender --> UserPreference
    Recommender --> MenuItem

    User --> SQLite
    HealthData --> SQLite
    HealthCondition --> SQLite
    UserPreference --> SQLite
    Restaurant --> SQLite
    MenuItem --> SQLite
    CartItem --> SQLite
```

## Data Flow Diagram

```mermaid
sequenceDiagram
    participant U as User
    participant B as Browser
    participant F as Flask
    participant R as Recommender
    participant DB as Database

    U->>B: Register/Login
    B->>F: POST /register or /login
    F->>DB: Create/Verify User
    F->>DB: Create HealthData, Preferences, Conditions

    U->>B: View Profile
    B->>F: GET /profile
    F->>DB: Load user data
    F->>B: Render profile form

    U->>B: Update Profile
    B->>F: POST /profile
    F->>DB: Save HealthData, Preferences, Conditions

    U->>B: Browse Restaurants
    B->>F: GET /home
    F->>DB: Load restaurants
    F->>B: Render restaurant grid

    U->>B: View Menu
    B->>F: GET /restaurant/<id>
    F->>DB: Load menu items, user health
    F->>R: get_recommendations(menu, health, prefs, conditions)
    R->>R: Filter by dietary prefs
    R->>R: Score items, apply penalties
    R->>F: Sorted recommendations
    F->>B: Render menu with scores & warnings

    U->>B: Add to Cart
    B->>F: POST /add_to_cart/<id>
    F->>DB: Create/Update CartItem
    F->>B: JSON response

    U->>B: View Cart
    B->>F: GET /cart
    F->>DB: Load cart items
    F->>B: Render cart with totals
```

## Project Structure

```
smart-food/
├── app.py                 # Main Flask application, routes, DB init
├── config.py              # Configuration (env-based)
├── models.py              # SQLAlchemy models
├── ml_recommender.py      # Food recommendation engine
├── migrate_db.py          # Database migration helper
├── requirements.txt
├── ARCHITECTURE.md
├── README.md
├── .gitignore
├── instance/              # Flask instance folder
│   └── health_food.db    # SQLite database
├── templates/             # Jinja2 HTML templates
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── home.html
│   ├── restaurants.html
│   ├── menu.html
│   ├── profile.html
│   ├── cart.html
│   └── navbar.html
└── static/
    ├── css/
    │   └── style.css
    └── js/
        └── main.js
```

## Technology Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3, Flask |
| Database | SQLite, SQLAlchemy |
| Auth | Flask-Login, Flask-Bcrypt |
| Frontend | Jinja2, Vanilla JS, CSS |
| ML/Logic | Custom FoodRecommender |

## Key Components

### FoodRecommender

- **calculate_bmi()**: Computes BMI from weight (kg) and height (cm)
- **calculate_daily_needs()**: Harris-Benedict BMR + activity factor from steps
- **check_dietary_preferences()**: Strict filters for vegetarian, vegan, gluten-free, allergies
- **check_health_conditions()**: Condition-specific penalties (diabetes, hypertension, cholesterol, etc.)
- **get_recommendations()**: Scores items 0–100, returns ranked list with warnings and `is_safe` flag

### Models

| Model | Purpose |
|-------|---------|
| User | Auth, Fitbit tokens |
| HealthData | Weight, height, age, steps, vitals, targets |
| HealthCondition | Diabetes, hypertension, cholesterol, etc. |
| UserPreference | Dietary prefs, allergies, cuisines |
| Restaurant | Name, cuisine, rating, description |
| MenuItem | Nutrition, health tags, price |
| CartItem | User, menu item, quantity |

## Routes Summary

| Route | Methods | Auth | Description |
|-------|---------|------|-------------|
| / | GET | No | Landing page |
| /register | GET, POST | No | Registration |
| /login | GET, POST | No | Login |
| /logout | GET | Yes | Logout |
| /home | GET | Yes | Restaurant listing |
| /restaurant/<id> | GET | Yes | Menu with recommendations |
| /profile | GET, POST | Yes | Health profile form |
| /cart | GET | Yes | Cart view |
| /add_to_cart/<id> | POST | Yes | Add item (JSON) |
| /update_cart/<id> | POST | Yes | Update quantity (JSON) |
| /remove_from_cart/<id> | POST | Yes | Remove item (JSON) |
| /sync_fitbit | GET | Yes | Fitbit sync (placeholder) |


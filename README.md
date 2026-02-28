# HealthFood

Personalized meal recommendations based on your health profile, dietary preferences, and medical conditions.

## Features

- **Health Profile** – Track weight, height, age, steps, blood sugar, cholesterol, blood pressure, and more
- **Medical Conditions** – Diabetes, hypertension, cholesterol, heart disease, kidney/liver disease, celiac, IBS, GERD, and others
- **Dietary Preferences** – Vegetarian, vegan, gluten-free, dairy-free, low-carb, low-sodium, low-fat, allergies
- **AI Recommendations** – Menu items scored 0–100 based on your profile with health warnings
- **Restaurants** – Curated South Indian restaurants with detailed nutrition per dish
- **Cart** – Add items, track calories and protein, manage quantities

## Tech Stack

- **Backend:** Python, Flask, SQLAlchemy, Flask-Login, Flask-Bcrypt
- **Frontend:** Jinja2, Vanilla JS, CSS
- **Database:** SQLite
- **ML:** Custom `FoodRecommender` engine

## Setup

### Prerequisites

- Python 3.8+
- pip

### Installation

```bash
git clone <repository-url>
cd smart-food
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Configuration

Create a `.env` file (optional, for production):

```
SECRET_KEY=your-secure-secret-key
DATABASE_URL=sqlite:///health_food.db
```

### Run

```bash
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000)

### Database

On first run, the app creates tables and seeds 10 South Indian restaurants with ~100 menu items. To reset:

```bash
rm -rf instance/
python app.py
```

Or run migrations manually:

```bash
python migrate_db.py
```

## Project Structure

```
smart-food/
├── app.py              # Main Flask app, routes
├── config.py           # Configuration
├── models.py           # SQLAlchemy models
├── ml_recommender.py   # Recommendation engine
├── migrate_db.py       # DB helper
├── requirements.txt
├── ARCHITECTURE.md     # Architecture & diagrams
├── templates/
└── static/
```

## Documentation

See [ARCHITECTURE.md](ARCHITECTURE.md) for architecture diagrams, data flow, and component details.

## License

MIT

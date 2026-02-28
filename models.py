from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    fitbit_access_token = db.Column(db.String(500))
    fitbit_refresh_token = db.Column(db.String(500))
    
    health_data = db.relationship('HealthData', backref='user', lazy=True, cascade='all, delete-orphan')
    preferences = db.relationship('UserPreference', backref='user', lazy=True, cascade='all, delete-orphan')
    cart_items = db.relationship('CartItem', backref='user', lazy=True, cascade='all, delete-orphan')
    health_conditions = db.relationship('HealthCondition', backref='user', lazy=True, cascade='all, delete-orphan')

class HealthData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    
    weight = db.Column(db.Float)
    height = db.Column(db.Float)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    
    steps = db.Column(db.Integer, default=0)
    calories_burned = db.Column(db.Float, default=0)
    heart_rate = db.Column(db.Integer)
    sleep_hours = db.Column(db.Float)
    
    blood_pressure_systolic = db.Column(db.Integer)
    blood_pressure_diastolic = db.Column(db.Integer)
    blood_sugar = db.Column(db.Float)
    cholesterol_total = db.Column(db.Float)
    cholesterol_ldl = db.Column(db.Float)
    cholesterol_hdl = db.Column(db.Float)
    target_calories = db.Column(db.Float)
    target_protein = db.Column(db.Float)
    target_carbs = db.Column(db.Float)
    target_fats = db.Column(db.Float)

class HealthCondition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Common conditions
    has_diabetes = db.Column(db.Boolean, default=False)
    diabetes_type = db.Column(db.String(20))
    has_hypertension = db.Column(db.Boolean, default=False)
    has_high_cholesterol = db.Column(db.Boolean, default=False)
    has_heart_disease = db.Column(db.Boolean, default=False)
    has_kidney_disease = db.Column(db.Boolean, default=False)
    has_liver_disease = db.Column(db.Boolean, default=False)
    has_thyroid_disorder = db.Column(db.Boolean, default=False)
    has_celiac_disease = db.Column(db.Boolean, default=False)
    has_ibs = db.Column(db.Boolean, default=False)
    has_gerd = db.Column(db.Boolean, default=False)
    has_obesity = db.Column(db.Boolean, default=False)
    has_anemia = db.Column(db.Boolean, default=False)
    
    other_conditions = db.Column(db.String(500))
    current_medications = db.Column(db.String(500))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class UserPreference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    is_vegetarian = db.Column(db.Boolean, default=False)
    is_vegan = db.Column(db.Boolean, default=False)
    is_gluten_free = db.Column(db.Boolean, default=False)
    is_dairy_free = db.Column(db.Boolean, default=False)
    is_low_carb = db.Column(db.Boolean, default=False)
    is_low_sodium = db.Column(db.Boolean, default=False)
    is_low_fat = db.Column(db.Boolean, default=False)
    
    allergies = db.Column(db.String(200))
    favorite_cuisines = db.Column(db.String(200))

class Restaurant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    cuisine_type = db.Column(db.String(50))
    rating = db.Column(db.Float, default=4.0)
    image_url = db.Column(db.String(300))
    description = db.Column(db.Text)
    
    menu_items = db.relationship('MenuItem', backref='restaurant', lazy=True, cascade='all, delete-orphan')

class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(300))
    
    calories = db.Column(db.Float)
    protein = db.Column(db.Float)
    carbs = db.Column(db.Float)
    fats = db.Column(db.Float)
    fiber = db.Column(db.Float)
    sugar = db.Column(db.Float)
    sodium = db.Column(db.Float)
    saturated_fat = db.Column(db.Float)
    cholesterol = db.Column(db.Float)
    is_vegetarian = db.Column(db.Boolean, default=False)
    is_vegan = db.Column(db.Boolean, default=False)
    is_gluten_free = db.Column(db.Boolean, default=False)
    is_low_carb = db.Column(db.Boolean, default=False)
    is_low_sodium = db.Column(db.Boolean, default=False)
    is_low_sugar = db.Column(db.Boolean, default=False)
    is_heart_healthy = db.Column(db.Boolean, default=False)
    is_diabetic_friendly = db.Column(db.Boolean, default=False)
    
    category = db.Column(db.String(50))
    
    glycemic_index = db.Column(db.String(20))

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_item.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    menu_item = db.relationship('MenuItem')
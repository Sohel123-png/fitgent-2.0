from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json
from datetime import datetime, timezone

app = Flask(__name__,
            static_folder='static',
            template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_key_123')

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='User')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # User profile information
    name = db.Column(db.String(100))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))
    weight_kg = db.Column(db.Float)
    height_cm = db.Column(db.Float)
    activity_level = db.Column(db.String(20), default='moderate')

    # Diet preferences
    diet_goal = db.Column(db.String(20), default='maintain')  # maintain, lose, gain
    diet_type = db.Column(db.String(20), default='balanced')  # balanced, high_protein, low_carb, etc.
    allergies = db.Column(db.String(200))  # Stored as JSON string

    # Relationships
    diet_plans = db.relationship('DietPlan', backref='user', lazy=True)
    health_stats = db.relationship('HealthStat', backref='user', lazy=True)
    reminders = db.relationship('Reminder', backref='user', lazy=True)
    chat_messages = db.relationship('ChatMessage', backref='user', lazy=True)

    # Workout relationships
    user_workout_plans = db.relationship('UserWorkoutPlan', backref='user', lazy=True)
    workout_logs = db.relationship('WorkoutLog', backref='user', lazy=True)
    trainer_profile = db.relationship('Trainer', backref='user', lazy=True, uselist=False)
    trainer_clients = db.relationship('TrainerClient', backref='client', lazy=True, foreign_keys='TrainerClient.client_id')
    nutrition_goals = db.relationship('NutritionGoal', backref='user', lazy=True)
    sent_messages = db.relationship('TrainerMessage', backref='sender', lazy=True, foreign_keys='TrainerMessage.sender_id')

    # E-commerce relationships
    cart = db.relationship('Cart', backref='user', lazy=True, uselist=False)
    orders = db.relationship('Order', backref='user', lazy=True)

    # Notification relationships
    device_tokens = db.relationship('DeviceToken', backref='user', lazy=True)
    notification_preferences = db.relationship('NotificationPreference', backref='user', lazy=True)
    notifications = db.relationship('Notification', backref='user', lazy=True)

    # User address information
    shipping_address = db.Column(db.Text)
    billing_address = db.Column(db.Text)
    phone = db.Column(db.String(20))

    # Firebase Cloud Messaging token for push notifications
    fcm_token = db.Column(db.String(255))  # Mobile FCM token
    watch_token = db.Column(db.String(255))  # Smartwatch FCM token

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def get_diet_preferences(self):
        """Get user's diet preferences as a dictionary."""
        try:
            allergies = json.loads(self.allergies) if self.allergies else []
        except:
            allergies = []

        return {
            'weight_kg': self.weight_kg or 70,
            'height_cm': self.height_cm or 170,
            'age': self.age or 30,
            'gender': self.gender or 'male',
            'activity_level': self.activity_level or 'moderate',
            'goal': self.diet_goal or 'maintain',
            'diet_type': self.diet_type or 'balanced',
            'allergies': allergies
        }

    def set_allergies(self, allergies_list):
        """Set allergies from a list."""
        self.allergies = json.dumps(allergies_list)

    def get_allergies(self):
        """Get allergies as a list."""
        try:
            return json.loads(self.allergies) if self.allergies else []
        except:
            return []

    def set_allergies(self, allergies_list):
        """Set allergies from a list."""
        self.allergies = json.dumps(allergies_list)

    def get_diet_preferences(self):
        """Get user's diet preferences as a dictionary."""
        return {
            'weight_kg': self.weight_kg or 70,
            'height_cm': self.height_cm or 170,
            'age': self.age or 30,
            'gender': self.gender or 'male',
            'activity_level': self.activity_level or 'moderate',
            'goal': self.diet_goal or 'maintain',
            'diet_type': self.diet_type or 'balanced',
            'allergies': self.get_allergies(),
            'num_days': 7
        }


class DietPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    plan_data = db.Column(db.Text, nullable=False)  # Stored as JSON string

    def get_plan(self):
        """Get the diet plan as a dictionary."""
        try:
            return json.loads(self.plan_data)
        except:
            return {}

    def set_plan(self, plan_dict):
        """Set the diet plan from a dictionary."""
        self.plan_data = json.dumps(plan_dict)


class HealthStat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, default=lambda: datetime.now(timezone.utc).date())
    weight_kg = db.Column(db.Float)
    calories_consumed = db.Column(db.Integer)
    calories_burned = db.Column(db.Integer)
    steps = db.Column(db.Integer)
    water_ml = db.Column(db.Integer)
    sleep_hours = db.Column(db.Float)
    notes = db.Column(db.Text)


class Reminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reminder_type = db.Column(db.String(20), nullable=False)  # meal, water, exercise
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    time = db.Column(db.Time, nullable=False)  # Time of day for the reminder
    days = db.Column(db.String(50), nullable=False)  # JSON string of days (e.g., ["Monday", "Wednesday", "Friday"])
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def get_days(self):
        """Get days as a list."""
        try:
            return json.loads(self.days) if self.days else []
        except:
            return []

    def set_days(self, days_list):
        """Set days from a list."""
        self.days = json.dumps(days_list)


class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # user, assistant
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(20), nullable=False)  # fitness, diet, wellness, progress
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    muscle_group = db.Column(db.String(50))  # chest, back, legs, shoulders, arms, core
    difficulty = db.Column(db.String(20))  # beginner, intermediate, advanced
    equipment = db.Column(db.String(100))  # barbell, dumbbell, machine, bodyweight, etc.
    instructions = db.Column(db.Text)
    video_url = db.Column(db.String(200))
    image_url = db.Column(db.String(200))

    # Relationships
    workout_exercises = db.relationship('WorkoutExercise', backref='exercise', lazy=True, cascade="all, delete-orphan")


class WorkoutPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    difficulty = db.Column(db.String(20), nullable=False)  # beginner, intermediate, advanced
    duration_weeks = db.Column(db.Integer, default=4)
    goal = db.Column(db.String(50))  # strength, hypertrophy, endurance, weight_loss
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    is_public = db.Column(db.Boolean, default=True)

    # Creator can be null for system-generated plans
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # Relationships
    workouts = db.relationship('Workout', backref='workout_plan', lazy=True, cascade="all, delete-orphan")
    user_workout_plans = db.relationship('UserWorkoutPlan', backref='workout_plan', lazy=True, cascade="all, delete-orphan")


class Workout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    workout_plan_id = db.Column(db.Integer, db.ForeignKey('workout_plan.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    day_of_week = db.Column(db.Integer)  # 0=Monday, 1=Tuesday, etc.
    week_number = db.Column(db.Integer, default=1)
    duration_minutes = db.Column(db.Integer)

    # Relationships
    workout_exercises = db.relationship('WorkoutExercise', backref='workout', lazy=True, cascade="all, delete-orphan")


class WorkoutExercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey('workout.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercise.id'), nullable=False)
    sets = db.Column(db.Integer)
    reps = db.Column(db.String(50))  # Can be a range like "8-12" or specific like "10"
    rest_seconds = db.Column(db.Integer)
    order = db.Column(db.Integer)  # Order in the workout
    notes = db.Column(db.Text)


class UserWorkoutPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    workout_plan_id = db.Column(db.Integer, db.ForeignKey('workout_plan.id'), nullable=False)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True)
    progress = db.Column(db.Float, default=0.0)  # 0-100%
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class WorkoutLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    workout_id = db.Column(db.Integer, db.ForeignKey('workout.id'))
    date = db.Column(db.Date, nullable=False, default=lambda: datetime.now(timezone.utc).date())
    duration_minutes = db.Column(db.Integer)
    calories_burned = db.Column(db.Integer)
    notes = db.Column(db.Text)
    rating = db.Column(db.Integer)  # 1-5 stars
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    exercise_logs = db.relationship('ExerciseLog', backref='workout_log', lazy=True, cascade="all, delete-orphan")


class ExerciseLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    workout_log_id = db.Column(db.Integer, db.ForeignKey('workout_log.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercise.id'), nullable=False)
    sets_completed = db.Column(db.Integer)
    reps = db.Column(db.String(200))  # JSON string of reps for each set
    weights = db.Column(db.String(200))  # JSON string of weights for each set (in kg)
    notes = db.Column(db.Text)


class Trainer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    bio = db.Column(db.Text)
    specialization = db.Column(db.String(100))  # strength, weight loss, bodybuilding, etc.
    experience_years = db.Column(db.Integer)
    certification = db.Column(db.String(200))
    hourly_rate = db.Column(db.Float)
    is_available = db.Column(db.Boolean, default=True)

    # Relationships
    clients = db.relationship('TrainerClient', backref='trainer', lazy=True, cascade="all, delete-orphan")
    workout_plans = db.relationship('WorkoutPlan', backref='creator', lazy=True, foreign_keys=[WorkoutPlan.creator_id])


class TrainerClient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainer.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, active, completed, cancelled
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    messages = db.relationship('TrainerMessage', backref='trainer_client', lazy=True, cascade="all, delete-orphan")


class TrainerMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trainer_client_id = db.Column(db.Integer, db.ForeignKey('trainer_client.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    is_read = db.Column(db.Boolean, default=False)


class NutritionGoal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    calories = db.Column(db.Integer)
    protein_g = db.Column(db.Integer)
    carbs_g = db.Column(db.Integer)
    fat_g = db.Column(db.Integer)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class ProductCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(200))
    parent_id = db.Column(db.Integer, db.ForeignKey('product_category.id'))

    # Relationships
    products = db.relationship('Product', backref='category', lazy=True)
    subcategories = db.relationship('ProductCategory', backref=db.backref('parent', remote_side=[id]), lazy=True)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    sale_price = db.Column(db.Float)
    stock_quantity = db.Column(db.Integer, default=0)
    sku = db.Column(db.String(50), unique=True)
    image_url = db.Column(db.String(200))
    category_id = db.Column(db.Integer, db.ForeignKey('product_category.id'))
    is_featured = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    weight_g = db.Column(db.Integer)  # Weight in grams
    dimensions = db.Column(db.String(100))  # Format: "LxWxH" in cm

    # Product details as JSON
    details = db.Column(db.Text)  # JSON string with additional product details

    # Relationships
    cart_items = db.relationship('CartItem', backref='product', lazy=True)
    order_items = db.relationship('OrderItem', backref='product', lazy=True)

    def get_details(self):
        """Get product details as a dictionary."""
        try:
            return json.loads(self.details) if self.details else {}
        except:
            return {}

    def set_details(self, details_dict):
        """Set product details from a dictionary."""
        self.details = json.dumps(details_dict)

    def get_final_price(self):
        """Get the final price (sale price if available, otherwise regular price)."""
        return self.sale_price if self.sale_price and self.sale_price < self.price else self.price


class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    items = db.relationship('CartItem', backref='cart', lazy=True, cascade="all, delete-orphan")

    def get_total(self):
        """Calculate the total price of all items in the cart."""
        return sum(item.quantity * item.product.get_final_price() for item in self.items)

    def get_item_count(self):
        """Get the total number of items in the cart."""
        return sum(item.quantity for item in self.items)


class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('cart.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    added_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def get_subtotal(self):
        """Calculate the subtotal for this item."""
        return self.quantity * self.product.get_final_price()


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, processing, shipped, delivered, cancelled
    total_amount = db.Column(db.Float, nullable=False)
    shipping_address = db.Column(db.Text, nullable=False)
    billing_address = db.Column(db.Text, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    payment_status = db.Column(db.String(20), default='pending')  # pending, paid, failed, refunded
    shipping_method = db.Column(db.String(50))
    shipping_cost = db.Column(db.Float, default=0.0)
    tax_amount = db.Column(db.Float, default=0.0)
    discount_code = db.Column(db.String(50))
    discount_amount = db.Column(db.Float, default=0.0)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Payment details as JSON
    payment_details = db.Column(db.Text)  # JSON string with payment gateway response

    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade="all, delete-orphan")

    def get_payment_details(self):
        """Get payment details as a dictionary."""
        try:
            return json.loads(self.payment_details) if self.payment_details else {}
        except:
            return {}

    def set_payment_details(self, details_dict):
        """Set payment details from a dictionary."""
        self.payment_details = json.dumps(details_dict)


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    price = db.Column(db.Float, nullable=False)  # Price at the time of purchase
    subtotal = db.Column(db.Float, nullable=False)  # price * quantity


class DeviceToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    device_type = db.Column(db.String(20), nullable=False)  # mobile, watch
    token = db.Column(db.String(255), nullable=False, unique=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_used = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class NotificationPreference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    notification_type = db.Column(db.String(50), nullable=False)  # meal, workout, goal, water, etc.
    enabled = db.Column(db.Boolean, default=True)
    send_mobile = db.Column(db.Boolean, default=True)
    send_watch = db.Column(db.Boolean, default=True)
    quiet_hours_start = db.Column(db.Time)  # Start time for quiet hours (no notifications)
    quiet_hours_end = db.Column(db.Time)  # End time for quiet hours
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    notification_type = db.Column(db.String(50), nullable=False)  # meal, workout, goal, water, etc.
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    data = db.Column(db.Text)  # JSON string with additional data
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    scheduled_for = db.Column(db.DateTime)  # When the notification should be sent
    sent_at = db.Column(db.DateTime)  # When the notification was actually sent

    def get_data(self):
        """Get notification data as a dictionary."""
        try:
            return json.loads(self.data) if self.data else {}
        except:
            return {}

    def set_data(self, data_dict):
        """Set notification data from a dictionary."""
        self.data = json.dumps(data_dict)


class NotificationDelivery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    notification_id = db.Column(db.Integer, db.ForeignKey('notification.id'), nullable=False)
    device_token_id = db.Column(db.Integer, db.ForeignKey('device_token.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, sent, delivered, failed
    sent_at = db.Column(db.DateTime)
    delivered_at = db.Column(db.DateTime)
    error = db.Column(db.Text)  # Error message if delivery failed

    # Relationships
    notification = db.relationship('Notification', backref='deliveries', lazy=True)
    device_token = db.relationship('DeviceToken', backref='deliveries', lazy=True)

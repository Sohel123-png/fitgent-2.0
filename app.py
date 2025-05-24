from flask import Flask, jsonify, render_template
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from flask_cors import CORS
from db import db, app as db_app, User
from auth import auth_bp
from diet_api import diet_bp
from reminders_api import reminders_bp
from fitness_api import fitness_bp
from chatbot_api import chatbot_bp
from workout_api import workout_bp
from notifications_api import notifications_bp
from google_fit_api import google_fit_bp
from health_ai_engine import health_ai_bp
from dotenv import load_dotenv
import os

load_dotenv()

app = db_app
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'secret123')

# Set up session secret key
app.secret_key = os.getenv('SECRET_KEY', 'dev_key_123')

# For Google OAuth
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # For development only

# Initialize extensions
jwt = JWTManager(app)
CORS(app)  # Enable CORS for all routes

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(diet_bp)
app.register_blueprint(reminders_bp)
app.register_blueprint(fitness_bp)
app.register_blueprint(chatbot_bp)
app.register_blueprint(workout_bp)
app.register_blueprint(notifications_bp)
app.register_blueprint(google_fit_bp, url_prefix='/api/google-fit')
app.register_blueprint(health_ai_bp, url_prefix='/api/health-ai')

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/gaming-dashboard')
def gaming_dashboard():
    """Render the gaming-style dashboard."""
    return render_template('gaming_dashboard.html')

@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    identity = get_jwt_identity()
    return jsonify(msg=f"Hello {identity['email']} with role {identity['role']}")

@app.route('/admin', methods=['GET'])
@jwt_required()
def admin_only():
    identity = get_jwt_identity()
    if identity['role'] != 'Admin':
        return jsonify(msg="Admins only!"), 403
    return jsonify(msg="Welcome Admin")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

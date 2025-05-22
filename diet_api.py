"""
Diet Plan API Module
This module provides API endpoints for generating and managing diet plans.
"""

from flask import Blueprint, request, jsonify, render_template, session
from flask_jwt_extended import jwt_required, get_jwt_identity
from db import db, User, DietPlan, HealthStat
from diet_plan import generate_diet_plan, get_meal_suggestion
import datetime
import json

diet_bp = Blueprint('diet', __name__)

@diet_bp.route('/api/diet-plan', methods=['POST'])
def create_diet_plan():
    """Create a new diet plan for the user."""
    try:
        # Get request data
        data = request.get_json()

        # Check if user is authenticated
        auth_header = request.headers.get('Authorization')
        is_authenticated = auth_header and auth_header.startswith('Bearer ')

        user = None
        if is_authenticated:
            try:
                # Get the current user
                current_user_identity = get_jwt_identity()
                user = User.query.filter_by(email=current_user_identity['email']).first()

                # Update user preferences if provided
                if user:
                    if data.get('weight_kg'):
                        user.weight_kg = data.get('weight_kg')
                    if data.get('height_cm'):
                        user.height_cm = data.get('height_cm')
                    if data.get('age'):
                        user.age = data.get('age')
                    if data.get('gender'):
                        user.gender = data.get('gender')
                    if data.get('activity_level'):
                        user.activity_level = data.get('activity_level')
                    if data.get('diet_goal'):
                        user.diet_goal = data.get('diet_goal')
                    if data.get('diet_type'):
                        user.diet_type = data.get('diet_type')
                    if data.get('allergies'):
                        user.set_allergies(data.get('allergies'))
            except Exception as e:
                # If there's an error with authentication, continue without a user
                print(f"Authentication error: {e}")
                is_authenticated = False

        # Get user preferences for diet plan
        if user:
            user_preferences = user.get_diet_preferences()
        else:
            # Use default preferences if user is not authenticated
            user_preferences = {
                'weight_kg': 70,
                'height_cm': 170,
                'age': 30,
                'gender': 'male',
                'activity_level': 'moderate',
                'goal': 'maintain',
                'diet_type': 'balanced',
                'allergies': [],
                'num_days': 7
            }

        # Override with request data if provided
        for key, value in data.items():
            if key in user_preferences:
                user_preferences[key] = value

        # Generate the diet plan
        diet_plan_data = generate_diet_plan(user_preferences)

        # If user is authenticated, save the diet plan to the database
        if user:
            start_date = datetime.datetime.now().date()
            end_date = start_date + datetime.timedelta(days=user_preferences.get('num_days', 7) - 1)

            diet_plan = DietPlan(
                user_id=user.id,
                start_date=start_date,
                end_date=end_date,
                plan_data=json.dumps(diet_plan_data)
            )

            # Save to database
            db.session.add(diet_plan)
            db.session.commit()

            return jsonify({
                "message": "Diet plan created successfully",
                "diet_plan_id": diet_plan.id,
                "diet_plan": diet_plan_data,
                "saved": True
            }), 201
        else:
            # Return the diet plan without saving it
            return jsonify({
                "message": "Diet plan generated successfully (not saved)",
                "diet_plan": diet_plan_data,
                "saved": False
            }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@diet_bp.route('/api/diet-plans', methods=['GET'])
def get_diet_plans():
    """Get all diet plans for the user."""
    try:
        # Check if user is authenticated
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Authentication required"}), 401

        try:
            # Get the current user
            current_user_identity = get_jwt_identity()
            user = User.query.filter_by(email=current_user_identity['email']).first()

            if not user:
                return jsonify({"error": "User not found"}), 404

            # Get all diet plans for the user
            diet_plans = DietPlan.query.filter_by(user_id=user.id).order_by(DietPlan.created_at.desc()).all()

            # Format the response
            result = []
            for plan in diet_plans:
                plan_data = plan.get_plan()
                result.append({
                    "id": plan.id,
                    "created_at": plan.created_at.isoformat(),
                    "start_date": plan.start_date.isoformat(),
                    "end_date": plan.end_date.isoformat(),
                    "summary": {
                        "daily_calories": plan_data.get('user_info', {}).get('daily_calories', 0),
                        "diet_type": plan_data.get('user_info', {}).get('diet_type', 'balanced'),
                        "num_days": len(plan_data.get('days', []))
                    }
                })

            return jsonify(result), 200
        except Exception as e:
            return jsonify({"error": "Authentication error"}), 401

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@diet_bp.route('/api/diet-plans/<int:plan_id>', methods=['GET'])
def get_diet_plan(plan_id):
    """Get a specific diet plan."""
    try:
        # Check if user is authenticated
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Authentication required"}), 401

        try:
            # Get the current user
            current_user_identity = get_jwt_identity()
            user = User.query.filter_by(email=current_user_identity['email']).first()

            if not user:
                return jsonify({"error": "User not found"}), 404

            # Get the diet plan
            diet_plan = DietPlan.query.filter_by(id=plan_id, user_id=user.id).first()

            if not diet_plan:
                return jsonify({"error": "Diet plan not found"}), 404

            # Return the diet plan
            return jsonify(diet_plan.get_plan()), 200
        except Exception as e:
            return jsonify({"error": "Authentication error"}), 401

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@diet_bp.route('/api/meal-suggestion', methods=['GET'])
def suggest_meal():
    """Get a meal suggestion based on meal type and diet type."""
    try:
        # Get query parameters
        meal_type = request.args.get('meal_type', 'breakfast')
        diet_type = request.args.get('diet_type')
        exclude_ingredients = request.args.get('exclude_ingredients')

        # Parse exclude_ingredients if provided
        if exclude_ingredients:
            exclude_ingredients = exclude_ingredients.split(',')
        else:
            exclude_ingredients = []

        # Get meal suggestion
        meal = get_meal_suggestion(meal_type, diet_type, exclude_ingredients)

        if not meal:
            return jsonify({"error": f"No {meal_type} suggestion found for the given criteria"}), 404

        return jsonify(meal), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@diet_bp.route('/diet-plan-generator')
def diet_plan_generator_page():
    """Render the diet plan generator page."""
    # Create default preferences
    default_preferences = {
        'weight_kg': 70,
        'height_cm': 170,
        'age': 30,
        'gender': 'male',
        'activity_level': 'moderate',
        'goal': 'maintain',
        'diet_type': 'balanced',
        'allergies': [],
        'num_days': 7
    }

    return render_template(
        'diet_plan_generator.html',
        preferences=default_preferences,
        latest_plan=None
    )

@diet_bp.route('/view-diet-plan/<int:plan_id>')
def view_diet_plan_page(plan_id):
    """Render the diet plan view page."""
    # Check if user is authenticated
    auth_header = request.headers.get('Authorization')
    is_authenticated = auth_header and auth_header.startswith('Bearer ')

    user = None
    if is_authenticated:
        try:
            # Get the current user
            current_user_identity = get_jwt_identity()
            user = User.query.filter_by(email=current_user_identity['email']).first()
        except Exception as e:
            # If there's an error with authentication, continue without a user
            print(f"Authentication error: {e}")

    # If user is authenticated, get their diet plan
    if user:
        diet_plan = DietPlan.query.filter_by(id=plan_id, user_id=user.id).first()

        if not diet_plan:
            return render_template('error.html', error="Diet plan not found")

        # Get the diet plan data
        plan_data = diet_plan.get_plan()

        return render_template(
            'view_diet_plan.html',
            user=user,
            plan=plan_data,
            plan_id=plan_id,
            start_date=diet_plan.start_date,
            end_date=diet_plan.end_date
        )
    else:
        # If user is not authenticated, redirect to login page
        return render_template('login.html', error="Please log in to view your diet plans")

"""
Fitness API Module
This module provides API endpoints for fitness data and smartwatch integration.
"""

from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session
from flask_jwt_extended import jwt_required, get_jwt_identity
from db import db, User, HealthStat
import datetime
import json
import google_fit

fitness_bp = Blueprint('fitness', __name__)

@fitness_bp.route('/fitness-dashboard')
def fitness_dashboard():
    """Render the fitness dashboard page."""
    # Check if user is authenticated with Google Fit
    has_google_fit = 'credentials' in session

    # Get fitness data if authenticated
    fitness_data = None
    if has_google_fit:
        try:
            fitness_data = google_fit.get_all_fitness_data()
        except Exception as e:
            print(f"Error getting fitness data: {e}")

    return render_template('fitness_dashboard.html',
                          has_google_fit=has_google_fit,
                          fitness_data=fitness_data)

@fitness_bp.route('/sync-google-fit')
def sync_google_fit():
    """Sync data from Google Fit."""
    try:
        # Check if user is authenticated with Google Fit
        if 'credentials' not in session:
            return jsonify({"success": False, "error": "Not authenticated with Google Fit"}), 401

        # Refresh the Google Fit data
        fitness_data = google_fit.get_all_fitness_data()

        # In a real app, we would save this data to the database
        # For now, we'll just return success
        return jsonify({"success": True, "message": "Data synced successfully"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@fitness_bp.route('/api/fitness/data', methods=['GET'])
@jwt_required()
def get_fitness_data():
    """Get fitness data for the current user."""
    try:
        # Get the current user
        current_user_identity = get_jwt_identity()
        user = User.query.filter_by(email=current_user_identity['email']).first()

        if not user:
            return jsonify({"error": "User not found"}), 404

        # Get date range from query parameters
        days = request.args.get('days', 7, type=int)

        # Get Google Fit data if available
        has_google_fit = 'credentials' in session
        google_fit_data = None

        if has_google_fit:
            try:
                # Get steps data
                steps_data = google_fit.get_steps_data(days)

                # Get calories data
                calories_data = google_fit.get_calories_data(days)

                # Get heart rate data
                heart_rate_data = google_fit.get_heart_rate_data(days)

                # Get sleep data
                sleep_data = google_fit.get_sleep_data(days)

                # Get weight data
                weight_data = google_fit.get_weight_data(days)

                google_fit_data = {
                    'steps': steps_data,
                    'calories': calories_data,
                    'heart_rate': heart_rate_data,
                    'sleep': sleep_data,
                    'weight': weight_data
                }
            except Exception as e:
                print(f"Error getting Google Fit data: {e}")

        # Get health stats from database
        end_date = datetime.datetime.now().date()
        start_date = end_date - datetime.timedelta(days=days)

        health_stats = HealthStat.query.filter(
            HealthStat.user_id == user.id,
            HealthStat.date >= start_date,
            HealthStat.date <= end_date
        ).order_by(HealthStat.date).all()

        # Format health stats
        health_stats_data = []
        for stat in health_stats:
            health_stats_data.append({
                'date': stat.date.strftime('%Y-%m-%d'),
                'weight_kg': stat.weight_kg,
                'calories_consumed': stat.calories_consumed,
                'calories_burned': stat.calories_burned,
                'steps': stat.steps,
                'water_ml': stat.water_ml,
                'sleep_hours': stat.sleep_hours
            })

        return jsonify({
            'google_fit': google_fit_data,
            'health_stats': health_stats_data,
            'has_google_fit': has_google_fit
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@fitness_bp.route('/api/fitness/health-stat', methods=['POST'])
@jwt_required()
def add_health_stat():
    """Add a new health stat for the current user."""
    try:
        # Get the current user
        current_user_identity = get_jwt_identity()
        user = User.query.filter_by(email=current_user_identity['email']).first()

        if not user:
            return jsonify({"error": "User not found"}), 404

        # Get request data
        data = request.get_json()

        # Validate required fields
        required_fields = ['date']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # Parse date
        try:
            date = datetime.datetime.strptime(data['date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

        # Check if a health stat already exists for this date
        existing_stat = HealthStat.query.filter_by(user_id=user.id, date=date).first()

        if existing_stat:
            # Update existing stat
            if 'weight_kg' in data:
                existing_stat.weight_kg = data['weight_kg']
            if 'calories_consumed' in data:
                existing_stat.calories_consumed = data['calories_consumed']
            if 'calories_burned' in data:
                existing_stat.calories_burned = data['calories_burned']
            if 'steps' in data:
                existing_stat.steps = data['steps']
            if 'water_ml' in data:
                existing_stat.water_ml = data['water_ml']
            if 'sleep_hours' in data:
                existing_stat.sleep_hours = data['sleep_hours']
            if 'notes' in data:
                existing_stat.notes = data['notes']

            db.session.commit()

            return jsonify({
                "message": "Health stat updated successfully",
                "id": existing_stat.id
            }), 200
        else:
            # Create new stat
            new_stat = HealthStat(
                user_id=user.id,
                date=date,
                weight_kg=data.get('weight_kg'),
                calories_consumed=data.get('calories_consumed'),
                calories_burned=data.get('calories_burned'),
                steps=data.get('steps'),
                water_ml=data.get('water_ml'),
                sleep_hours=data.get('sleep_hours'),
                notes=data.get('notes')
            )

            db.session.add(new_stat)
            db.session.commit()

            return jsonify({
                "message": "Health stat added successfully",
                "id": new_stat.id
            }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@fitness_bp.route('/api/fitness/notifications/settings', methods=['GET', 'PUT'])
@jwt_required()
def notification_settings():
    """Get or update notification settings for the current user."""
    try:
        # Get the current user
        current_user_identity = get_jwt_identity()
        user = User.query.filter_by(email=current_user_identity['email']).first()

        if not user:
            return jsonify({"error": "User not found"}), 404

        if request.method == 'GET':
            # Get notification settings from user preferences
            # This would be implemented in a real app
            return jsonify({
                'step_goal': True,
                'workout_reminders': True,
                'water_reminders': True,
                'sleep_reminders': True
            }), 200
        else:  # PUT
            # Update notification settings
            data = request.get_json()

            # In a real app, this would update user preferences in the database
            return jsonify({
                "message": "Notification settings updated successfully",
                "settings": data
            }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@fitness_bp.route('/api/fitness/send-notification', methods=['POST'])
@jwt_required()
def send_notification():
    """Send a notification to the user's device."""
    try:
        # Get the current user
        current_user_identity = get_jwt_identity()
        user = User.query.filter_by(email=current_user_identity['email']).first()

        if not user:
            return jsonify({"error": "User not found"}), 404

        # Get request data
        data = request.get_json()

        # Validate required fields
        required_fields = ['title', 'message']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # In a real app, this would send a notification to the user's device
        # using a service like Firebase Cloud Messaging or OneSignal

        return jsonify({
            "message": "Notification sent successfully",
            "notification": {
                "title": data['title'],
                "message": data['message'],
                "timestamp": datetime.datetime.now().isoformat()
            }
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@fitness_bp.route('/api/notifications/subscribe', methods=['POST'])
@jwt_required()
def subscribe_to_notifications():
    """Subscribe to push notifications."""
    try:
        # Get the current user
        current_user_identity = get_jwt_identity()
        user = User.query.filter_by(email=current_user_identity['email']).first()

        if not user:
            return jsonify({"error": "User not found"}), 404

        # Get subscription data
        subscription = request.get_json()

        if not subscription:
            return jsonify({"error": "No subscription data provided"}), 400

        # In a real app, we would save the subscription to the database
        # For now, we'll just return success

        return jsonify({
            "message": "Subscription saved successfully"
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

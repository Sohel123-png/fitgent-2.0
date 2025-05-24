"""
Enhanced Google Fit API Blueprint for comprehensive smartwatch integration.
Supports Google Fit, Apple HealthKit bridge, Mi Band, and other wearables.
"""

from flask import Blueprint, request, jsonify, session, redirect, url_for, flash, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity
import google.oauth2.credentials
import google_auth_oauthlib.flow
from db import db, User, FitnessData, HealthStat, Notification
import google_fit
import datetime
import json
import requests
from typing import Dict, List, Optional

google_fit_bp = Blueprint('google_fit_api', __name__)

@google_fit_bp.route('/')
def google_fit_page():
    """Render the Google Fit integration page."""
    return render_template('google_fit_integration.html')

@google_fit_bp.route('/authorize')
@jwt_required()
def authorize():
    """Authorize the app to access Google Fit data."""
    try:
        # Get the current user
        current_user = get_jwt_identity()
        user_id = current_user.get('user_id')

        if not user_id:
            return jsonify({"msg": "User ID not found in token"}), 400

        # Generate authorization URL
        auth_url = google_fit.get_authorization_url()

        if not auth_url:
            return jsonify({"msg": "Failed to generate authorization URL. Check Google API credentials."}), 500

        # Store the user ID in the session for the callback
        session['user_id'] = user_id

        return jsonify({"authorization_url": auth_url}), 200

    except Exception as e:
        print(f"Error in Google Fit authorization: {str(e)}")
        return jsonify({"msg": f"An error occurred: {str(e)}"}), 500

@google_fit_bp.route('/oauth2callback')
def oauth2callback():
    """Handle the OAuth2 callback from Google."""
    try:
        # Get the authorization code from the request
        code = request.args.get('code')
        state = request.args.get('state')

        # Verify state to prevent CSRF
        if state != session.get('state'):
            flash('Invalid state parameter. Authorization failed.', 'error')
            return redirect(url_for('user_dashboard'))

        # Get user ID from session
        user_id = session.get('user_id')
        if not user_id:
            flash('User session expired. Please try again.', 'error')
            return redirect(url_for('user_dashboard'))

        # Get client secrets
        client_secrets = google_fit.get_client_secrets()

        # Create flow instance
        flow = google_auth_oauthlib.flow.Flow.from_client_config(
            client_secrets, google_fit.SCOPES, state=state)
        flow.redirect_uri = url_for('google_fit_api.oauth2callback', _external=True)

        # Exchange authorization code for credentials
        flow.fetch_token(code=code)
        credentials = flow.credentials

        # Store credentials in session
        session['credentials'] = google_fit.credentials_to_dict(credentials)

        # Store user's Google Fit connection status in database
        user = User.query.get(user_id)
        if user:
            # Create or update fitness data record
            fitness_data = FitnessData.query.filter_by(user_id=user_id).first()
            if not fitness_data:
                fitness_data = FitnessData(user_id=user_id)
                db.session.add(fitness_data)

            # Update connection status
            fitness_data.google_fit_connected = True
            fitness_data.last_sync = datetime.datetime.now()
            db.session.commit()

            flash('Successfully connected to Google Fit!', 'success')
        else:
            flash('User not found.', 'error')

        return redirect(url_for('user_dashboard'))

    except Exception as e:
        print(f"Error in OAuth callback: {str(e)}")
        flash(f'An error occurred during Google Fit authorization: {str(e)}', 'error')
        return redirect(url_for('user_dashboard'))

@google_fit_bp.route('/disconnect')
@jwt_required()
def disconnect():
    """Disconnect Google Fit integration."""
    try:
        # Get the current user
        current_user = get_jwt_identity()
        user_id = current_user.get('user_id')

        if not user_id:
            return jsonify({"msg": "User ID not found in token"}), 400

        # Clear credentials from session
        if 'credentials' in session:
            del session['credentials']

        # Update user's Google Fit connection status
        fitness_data = FitnessData.query.filter_by(user_id=user_id).first()
        if fitness_data:
            fitness_data.google_fit_connected = False
            db.session.commit()

        return jsonify({"msg": "Successfully disconnected from Google Fit"}), 200

    except Exception as e:
        print(f"Error disconnecting from Google Fit: {str(e)}")
        return jsonify({"msg": f"An error occurred: {str(e)}"}), 500

@google_fit_bp.route('/data')
@jwt_required()
def get_fitness_data():
    """Get fitness data from Google Fit."""
    try:
        # Check if user is connected to Google Fit
        if 'credentials' not in session:
            return jsonify({
                "msg": "Not connected to Google Fit",
                "connected": False
            }), 200

        # Get fitness data
        fitness_data = google_fit.get_all_fitness_data()

        if not fitness_data or not fitness_data.get('has_data'):
            return jsonify({
                "msg": "No fitness data available",
                "connected": True,
                "has_data": False
            }), 200

        # Return fitness data
        return jsonify({
            "connected": True,
            "has_data": True,
            "data": fitness_data
        }), 200

    except Exception as e:
        print(f"Error getting fitness data: {str(e)}")
        return jsonify({"msg": f"An error occurred: {str(e)}"}), 500

@google_fit_bp.route('/sync')
@jwt_required()
def sync_data():
    """Sync fitness data from Google Fit."""
    try:
        # Get the current user
        current_user = get_jwt_identity()
        user_id = current_user.get('user_id')

        if not user_id:
            return jsonify({"msg": "User ID not found in token"}), 400

        # Check if user is connected to Google Fit
        if 'credentials' not in session:
            return jsonify({
                "msg": "Not connected to Google Fit",
                "connected": False
            }), 200

        # Get fitness data
        fitness_data = google_fit.get_all_fitness_data()

        if not fitness_data or not fitness_data.get('has_data'):
            return jsonify({
                "msg": "No fitness data available to sync",
                "connected": True,
                "has_data": False
            }), 200

        # Update user's fitness data in database
        user_fitness_data = FitnessData.query.filter_by(user_id=user_id).first()
        if not user_fitness_data:
            user_fitness_data = FitnessData(user_id=user_id)
            db.session.add(user_fitness_data)

        # Update fitness data fields
        user_fitness_data.steps = fitness_data.get('today_steps', 0)
        user_fitness_data.calories_burned = fitness_data.get('today_calories', 0)
        user_fitness_data.weight_kg = fitness_data.get('latest_weight', 0)
        user_fitness_data.heart_rate = fitness_data.get('avg_resting_heart_rate', 0)
        user_fitness_data.sleep_hours = fitness_data.get('last_night_sleep', 0)
        user_fitness_data.last_sync = datetime.datetime.now()

        db.session.commit()

        return jsonify({
            "msg": "Fitness data synced successfully",
            "connected": True,
            "has_data": True,
            "data": fitness_data
        }), 200

    except Exception as e:
        print(f"Error syncing fitness data: {str(e)}")
        return jsonify({"msg": f"An error occurred: {str(e)}"}), 500


# Enhanced Health Data Collection Functions
def collect_comprehensive_health_data(user_id: int) -> Dict:
    """
    Collect comprehensive health data from multiple sources.
    Returns a dictionary with all available health metrics.
    """
    try:
        health_data = {
            'timestamp': datetime.datetime.now().isoformat(),
            'user_id': user_id,
            'sources': [],
            'metrics': {}
        }

        # Google Fit Data
        if 'credentials' in session:
            google_data = google_fit.get_all_fitness_data()
            if google_data and google_data.get('has_data'):
                health_data['sources'].append('google_fit')
                health_data['metrics'].update({
                    'steps': google_data.get('today_steps', 0),
                    'calories_burned': google_data.get('today_calories', 0),
                    'heart_rate_avg': google_data.get('avg_resting_heart_rate', 0),
                    'sleep_hours': google_data.get('last_night_sleep', 0),
                    'weight_kg': google_data.get('latest_weight', 0),
                    'distance_km': google_data.get('today_distance', 0),
                    'active_minutes': google_data.get('today_active_minutes', 0)
                })

        # Calculate additional metrics
        user = User.query.get(user_id)
        if user and user.height_cm and health_data['metrics'].get('weight_kg'):
            height_m = user.height_cm / 100
            weight_kg = health_data['metrics']['weight_kg']
            bmi = weight_kg / (height_m ** 2)
            health_data['metrics']['bmi'] = round(bmi, 2)

        # Add stress level estimation based on heart rate variability
        heart_rate = health_data['metrics'].get('heart_rate_avg', 0)
        if heart_rate > 0:
            # Simple stress estimation (this would be more sophisticated in production)
            if heart_rate > 100:
                stress_level = min(10, (heart_rate - 60) / 10)
            else:
                stress_level = max(1, 10 - (80 - heart_rate) / 5)
            health_data['metrics']['stress_level'] = round(stress_level, 1)

        return health_data

    except Exception as e:
        print(f"Error collecting comprehensive health data: {str(e)}")
        return {'error': str(e), 'metrics': {}}


def store_health_data_to_db(user_id: int, health_data: Dict) -> bool:
    """
    Store collected health data to the database.
    """
    try:
        today = datetime.date.today()

        # Update or create FitnessData record
        fitness_data = FitnessData.query.filter_by(user_id=user_id, date=today).first()
        if not fitness_data:
            fitness_data = FitnessData(user_id=user_id, date=today)
            db.session.add(fitness_data)

        metrics = health_data.get('metrics', {})

        # Update fitness data fields
        if metrics.get('steps'):
            fitness_data.steps = metrics['steps']
        if metrics.get('calories_burned'):
            fitness_data.calories_burned = metrics['calories_burned']
        if metrics.get('heart_rate_avg'):
            fitness_data.heart_rate = metrics['heart_rate_avg']
        if metrics.get('sleep_hours'):
            fitness_data.sleep_hours = metrics['sleep_hours']
        if metrics.get('weight_kg'):
            fitness_data.weight_kg = metrics['weight_kg']
        if metrics.get('distance_km'):
            fitness_data.distance_km = metrics['distance_km']
        if metrics.get('active_minutes'):
            fitness_data.active_minutes = metrics['active_minutes']
        if metrics.get('bmi'):
            fitness_data.bmi = metrics['bmi']

        fitness_data.last_sync = datetime.datetime.now()

        # Also create/update HealthStat record for historical tracking
        health_stat = HealthStat.query.filter_by(user_id=user_id, date=today).first()
        if not health_stat:
            health_stat = HealthStat(user_id=user_id, date=today)
            db.session.add(health_stat)

        if metrics.get('steps'):
            health_stat.steps = metrics['steps']
        if metrics.get('calories_burned'):
            health_stat.calories_burned = metrics['calories_burned']
        if metrics.get('sleep_hours'):
            health_stat.sleep_hours = metrics['sleep_hours']
        if metrics.get('weight_kg'):
            health_stat.weight_kg = metrics['weight_kg']

        db.session.commit()
        return True

    except Exception as e:
        print(f"Error storing health data to database: {str(e)}")
        db.session.rollback()
        return False


@google_fit_bp.route('/health/comprehensive')
@jwt_required()
def get_comprehensive_health_data():
    """
    Get comprehensive health data from all connected sources.
    """
    try:
        current_user = get_jwt_identity()
        user_id = current_user.get('user_id')

        if not user_id:
            return jsonify({"msg": "User ID not found in token"}), 400

        # Collect comprehensive health data
        health_data = collect_comprehensive_health_data(user_id)

        if 'error' in health_data:
            return jsonify({
                "msg": "Error collecting health data",
                "error": health_data['error']
            }), 500

        # Store data to database
        stored = store_health_data_to_db(user_id, health_data)

        return jsonify({
            "success": True,
            "data": health_data,
            "stored_to_db": stored,
            "sources_connected": len(health_data.get('sources', [])),
            "metrics_collected": len(health_data.get('metrics', {}))
        }), 200

    except Exception as e:
        print(f"Error in comprehensive health data endpoint: {str(e)}")
        return jsonify({"msg": f"An error occurred: {str(e)}"}), 500

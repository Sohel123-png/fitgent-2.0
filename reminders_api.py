"""
Reminders API Module
This module provides API endpoints for managing reminders.
"""

from flask import Blueprint, request, jsonify, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity
from db import db, User, Reminder
import datetime
import json

reminders_bp = Blueprint('reminders', __name__)

@reminders_bp.route('/api/reminders', methods=['GET'])
@jwt_required()
def get_reminders():
    """Get all reminders for the user."""
    try:
        # Get the current user
        current_user_identity = get_jwt_identity()
        user = User.query.filter_by(email=current_user_identity['email']).first()

        if not user:
            return jsonify({"error": "User not found"}), 404

        # Get all reminders for the user
        reminders = Reminder.query.filter_by(user_id=user.id).order_by(Reminder.time).all()

        # Format the response
        result = []
        for reminder in reminders:
            result.append({
                "id": reminder.id,
                "reminder_type": reminder.reminder_type,
                "title": reminder.title,
                "description": reminder.description,
                "time": reminder.time.strftime('%H:%M'),
                "days": reminder.get_days(),
                "is_active": reminder.is_active,
                "created_at": reminder.created_at.isoformat()
            })

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@reminders_bp.route('/api/reminders', methods=['POST'])
@jwt_required()
def create_reminder():
    """Create a new reminder."""
    try:
        # Get the current user
        current_user_identity = get_jwt_identity()
        user = User.query.filter_by(email=current_user_identity['email']).first()

        if not user:
            return jsonify({"error": "User not found"}), 404

        # Get request data
        data = request.get_json()

        # Validate required fields
        required_fields = ['reminder_type', 'title', 'time', 'days']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # Validate reminder type
        valid_types = ['meal', 'water', 'exercise']
        if data['reminder_type'] not in valid_types:
            return jsonify({"error": f"Invalid reminder type. Must be one of: {', '.join(valid_types)}"}), 400

        # Parse time
        try:
            time_obj = datetime.datetime.strptime(data['time'], '%H:%M').time()
        except ValueError:
            return jsonify({"error": "Invalid time format. Use HH:MM (24-hour format)"}), 400

        # Create a new reminder
        reminder = Reminder(
            user_id=user.id,
            reminder_type=data['reminder_type'],
            title=data['title'],
            description=data.get('description', ''),
            time=time_obj,
            is_active=data.get('is_active', True)
        )

        # Set days
        reminder.set_days(data['days'])

        # Save to database
        db.session.add(reminder)
        db.session.commit()

        return jsonify({
            "message": "Reminder created successfully",
            "reminder_id": reminder.id
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@reminders_bp.route('/api/reminders/<int:reminder_id>', methods=['PUT'])
@jwt_required()
def update_reminder(reminder_id):
    """Update a specific reminder."""
    try:
        # Get the current user
        current_user_identity = get_jwt_identity()
        user = User.query.filter_by(email=current_user_identity['email']).first()

        if not user:
            return jsonify({"error": "User not found"}), 404

        # Get the reminder
        reminder = Reminder.query.filter_by(id=reminder_id, user_id=user.id).first()

        if not reminder:
            return jsonify({"error": "Reminder not found"}), 404

        # Get request data
        data = request.get_json()

        # Update reminder fields
        if 'reminder_type' in data:
            valid_types = ['meal', 'water', 'exercise']
            if data['reminder_type'] not in valid_types:
                return jsonify({"error": f"Invalid reminder type. Must be one of: {', '.join(valid_types)}"}), 400
            reminder.reminder_type = data['reminder_type']

        if 'title' in data:
            reminder.title = data['title']

        if 'description' in data:
            reminder.description = data['description']

        if 'time' in data:
            try:
                time_obj = datetime.datetime.strptime(data['time'], '%H:%M').time()
                reminder.time = time_obj
            except ValueError:
                return jsonify({"error": "Invalid time format. Use HH:MM (24-hour format)"}), 400

        if 'days' in data:
            reminder.set_days(data['days'])

        if 'is_active' in data:
            reminder.is_active = data['is_active']

        # Save to database
        db.session.commit()

        return jsonify({
            "message": "Reminder updated successfully"
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@reminders_bp.route('/api/reminders/<int:reminder_id>', methods=['DELETE'])
@jwt_required()
def delete_reminder(reminder_id):
    """Delete a specific reminder."""
    try:
        # Get the current user
        current_user_identity = get_jwt_identity()
        user = User.query.filter_by(email=current_user_identity['email']).first()

        if not user:
            return jsonify({"error": "User not found"}), 404

        # Get the reminder
        reminder = Reminder.query.filter_by(id=reminder_id, user_id=user.id).first()

        if not reminder:
            return jsonify({"error": "Reminder not found"}), 404

        # Delete the reminder
        db.session.delete(reminder)
        db.session.commit()

        return jsonify({
            "message": "Reminder deleted successfully"
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@reminders_bp.route('/api/reminders/today', methods=['GET'])
def get_todays_reminders():
    """Get all reminders for today."""
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

            # Get current day of week
            today = datetime.datetime.now().strftime('%A')  # e.g., 'Monday'

            # Get all active reminders for the user
            reminders = Reminder.query.filter_by(user_id=user.id, is_active=True).order_by(Reminder.time).all()

            # Filter reminders for today
            todays_reminders = []
            for reminder in reminders:
                days = reminder.get_days()
                if today in days:
                    todays_reminders.append({
                        "id": reminder.id,
                        "reminder_type": reminder.reminder_type,
                        "title": reminder.title,
                        "description": reminder.description,
                        "time": reminder.time.strftime('%H:%M'),
                        "days": days,
                        "is_active": reminder.is_active
                    })

            return jsonify(todays_reminders), 200
        except Exception as e:
            return jsonify({"error": "Authentication error"}), 401

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@reminders_bp.route('/reminders', methods=['GET'])
def reminders_page():
    """Render the reminders management page."""
    return render_template('reminders.html')

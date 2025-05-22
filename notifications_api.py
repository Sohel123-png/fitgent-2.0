"""
Notifications API Module
This module provides API endpoints for managing notifications and device tokens.
"""

from flask import Blueprint, request, jsonify, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity
from db import db, User, Notification, NotificationPreference, DeviceToken, NotificationDelivery
from db import Reminder, WorkoutLog, HealthStat, UserWorkoutPlan, Workout, NutritionGoal
import datetime
import json
import os
import requests
import time
import uuid
from functools import wraps

# Initialize Firebase Admin SDK for FCM
try:
    import firebase_admin
    from firebase_admin import credentials, messaging

    # Check if Firebase credentials exist
    firebase_cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
    if firebase_cred_path and os.path.exists(firebase_cred_path):
        cred = credentials.Certificate(firebase_cred_path)
        firebase_admin.initialize_app(cred)
        firebase_enabled = True
    else:
        firebase_enabled = False
except ImportError:
    firebase_enabled = False
    print("Firebase Admin SDK not installed. Push notifications will be simulated.")

notifications_bp = Blueprint('notifications', __name__)

# Helper functions
def get_current_user():
    """Get the current user from JWT token."""
    current_user_identity = get_jwt_identity()
    return User.query.filter_by(email=current_user_identity['email']).first()

def firebase_required(f):
    """Decorator to check if Firebase is configured."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not firebase_enabled:
            return jsonify({"error": "Firebase is not configured. Push notifications are disabled."}), 503
        return f(*args, **kwargs)
    return decorated_function

def send_push_notification(device_token, title, body, data=None):
    """Send a push notification using Firebase Cloud Messaging."""
    if not firebase_enabled:
        # Simulate sending a notification
        print(f"SIMULATED NOTIFICATION to {device_token}: {title} - {body}")
        time.sleep(0.5)  # Simulate network delay
        return True, None

    try:
        # Create message
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body
            ),
            data=data or {},
            token=device_token
        )

        # Send message
        response = messaging.send(message)
        return True, response
    except Exception as e:
        return False, str(e)

def create_notification(user_id, notification_type, title, message, data=None, scheduled_for=None):
    """Create a notification in the database."""
    notification = Notification(
        user_id=user_id,
        notification_type=notification_type,
        title=title,
        message=message,
        scheduled_for=scheduled_for or datetime.datetime.now()
    )

    if data:
        notification.set_data(data)

    db.session.add(notification)
    db.session.commit()

    return notification

def deliver_notification(notification, immediate=False):
    """Deliver a notification to all user devices based on preferences."""
    user = User.query.get(notification.user_id)
    if not user:
        return False

    # Check if notification should be delivered now
    if not immediate and notification.scheduled_for > datetime.datetime.now():
        return False

    # Get user preferences for this notification type
    preference = NotificationPreference.query.filter_by(
        user_id=user.id,
        notification_type=notification.notification_type
    ).first()

    # If no specific preference, create default
    if not preference:
        preference = NotificationPreference(
            user_id=user.id,
            notification_type=notification.notification_type,
            enabled=True,
            send_mobile=True,
            send_watch=True
        )
        db.session.add(preference)
        db.session.commit()

    # Check if notifications are enabled
    if not preference.enabled:
        return False

    # Check quiet hours
    if preference.quiet_hours_start and preference.quiet_hours_end:
        now = datetime.datetime.now().time()
        if preference.quiet_hours_start < preference.quiet_hours_end:
            # Normal case: quiet hours within same day
            if preference.quiet_hours_start <= now <= preference.quiet_hours_end:
                return False
        else:
            # Edge case: quiet hours span midnight
            if preference.quiet_hours_start <= now or now <= preference.quiet_hours_end:
                return False

    # Get user devices
    devices = []

    # Add mobile device if preference allows
    if preference.send_mobile and user.fcm_token:
        mobile_device = DeviceToken.query.filter_by(
            user_id=user.id,
            device_type='mobile',
            token=user.fcm_token,
            is_active=True
        ).first()

        if not mobile_device:
            mobile_device = DeviceToken(
                user_id=user.id,
                device_type='mobile',
                token=user.fcm_token,
                is_active=True
            )
            db.session.add(mobile_device)
            db.session.commit()

        devices.append(mobile_device)

    # Add watch device if preference allows
    if preference.send_watch and user.watch_token:
        watch_device = DeviceToken.query.filter_by(
            user_id=user.id,
            device_type='watch',
            token=user.watch_token,
            is_active=True
        ).first()

        if not watch_device:
            watch_device = DeviceToken(
                user_id=user.id,
                device_type='watch',
                token=user.watch_token,
                is_active=True
            )
            db.session.add(watch_device)
            db.session.commit()

        devices.append(watch_device)

    # Send notification to each device
    success = False
    for device in devices:
        # Create delivery record
        delivery = NotificationDelivery(
            notification_id=notification.id,
            device_token_id=device.id,
            status='pending'
        )
        db.session.add(delivery)
        db.session.commit()

        # Send notification
        success_device, response = send_push_notification(
            device.token,
            notification.title,
            notification.message,
            notification.get_data()
        )

        # Update delivery status
        if success_device:
            delivery.status = 'sent'
            delivery.sent_at = datetime.datetime.now()
            success = True
        else:
            delivery.status = 'failed'
            delivery.error = str(response)

        db.session.commit()

    # Update notification status
    if success:
        notification.sent_at = datetime.datetime.now()
        db.session.commit()

    return success

# Routes
@notifications_bp.route('/notifications')
def notifications_page():
    """Render the notifications management page."""
    return render_template('notifications.html')

# API Endpoints
@notifications_bp.route('/api/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    """Get all notifications for the user."""
    try:
        user = get_current_user()

        if not user:
            return jsonify({"error": "User not found"}), 404

        # Get query parameters
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'

        # Build query
        query = Notification.query.filter_by(user_id=user.id)

        if unread_only:
            query = query.filter_by(is_read=False)

        # Get total count
        total_count = query.count()

        # Get notifications with pagination
        notifications = query.order_by(Notification.created_at.desc()).offset(offset).limit(limit).all()

        # Format response
        result = []
        for notification in notifications:
            result.append({
                "id": notification.id,
                "notification_type": notification.notification_type,
                "title": notification.title,
                "message": notification.message,
                "data": notification.get_data(),
                "is_read": notification.is_read,
                "created_at": notification.created_at.isoformat(),
                "scheduled_for": notification.scheduled_for.isoformat() if notification.scheduled_for else None,
                "sent_at": notification.sent_at.isoformat() if notification.sent_at else None
            })

        return jsonify({
            "notifications": result,
            "total_count": total_count,
            "limit": limit,
            "offset": offset,
            "has_more": total_count > (offset + limit)
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@notifications_bp.route('/api/notifications/<int:notification_id>/read', methods=['PUT'])
@jwt_required()
def mark_notification_read(notification_id):
    """Mark a notification as read."""
    try:
        user = get_current_user()

        if not user:
            return jsonify({"error": "User not found"}), 404

        # Get the notification
        notification = Notification.query.filter_by(id=notification_id, user_id=user.id).first()

        if not notification:
            return jsonify({"error": "Notification not found"}), 404

        # Mark as read
        notification.is_read = True
        db.session.commit()

        return jsonify({
            "message": "Notification marked as read",
            "notification_id": notification.id
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@notifications_bp.route('/api/notifications/read-all', methods=['PUT'])
@jwt_required()
def mark_all_notifications_read():
    """Mark all notifications as read."""
    try:
        user = get_current_user()

        if not user:
            return jsonify({"error": "User not found"}), 404

        # Update all unread notifications
        count = Notification.query.filter_by(user_id=user.id, is_read=False).update({'is_read': True})
        db.session.commit()

        return jsonify({
            "message": f"{count} notifications marked as read"
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@notifications_bp.route('/api/notifications/<int:notification_id>', methods=['DELETE'])
@jwt_required()
def delete_notification(notification_id):
    """Delete a notification."""
    try:
        user = get_current_user()

        if not user:
            return jsonify({"error": "User not found"}), 404

        # Get the notification
        notification = Notification.query.filter_by(id=notification_id, user_id=user.id).first()

        if not notification:
            return jsonify({"error": "Notification not found"}), 404

        # Delete the notification
        db.session.delete(notification)
        db.session.commit()

        return jsonify({
            "message": "Notification deleted",
            "notification_id": notification_id
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@notifications_bp.route('/api/notification-preferences', methods=['GET'])
@jwt_required()
def get_notification_preferences():
    """Get notification preferences for the user."""
    try:
        user = get_current_user()

        if not user:
            return jsonify({"error": "User not found"}), 404

        # Get all preferences
        preferences = NotificationPreference.query.filter_by(user_id=user.id).all()

        # Format response
        result = []
        for pref in preferences:
            result.append({
                "id": pref.id,
                "notification_type": pref.notification_type,
                "enabled": pref.enabled,
                "send_mobile": pref.send_mobile,
                "send_watch": pref.send_watch,
                "quiet_hours_start": pref.quiet_hours_start.strftime('%H:%M') if pref.quiet_hours_start else None,
                "quiet_hours_end": pref.quiet_hours_end.strftime('%H:%M') if pref.quiet_hours_end else None
            })

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@notifications_bp.route('/api/notification-preferences', methods=['POST'])
@jwt_required()
def create_notification_preference():
    """Create or update a notification preference."""
    try:
        user = get_current_user()

        if not user:
            return jsonify({"error": "User not found"}), 404

        # Get request data
        data = request.get_json()

        # Validate required fields
        if 'notification_type' not in data:
            return jsonify({"error": "Notification type is required"}), 400

        # Check if preference already exists
        preference = NotificationPreference.query.filter_by(
            user_id=user.id,
            notification_type=data['notification_type']
        ).first()

        if preference:
            # Update existing preference
            if 'enabled' in data:
                preference.enabled = data['enabled']

            if 'send_mobile' in data:
                preference.send_mobile = data['send_mobile']

            if 'send_watch' in data:
                preference.send_watch = data['send_watch']

            if 'quiet_hours_start' in data and data['quiet_hours_start']:
                try:
                    preference.quiet_hours_start = datetime.datetime.strptime(data['quiet_hours_start'], '%H:%M').time()
                except ValueError:
                    return jsonify({"error": "Invalid quiet_hours_start format. Use HH:MM (24-hour format)"}), 400

            if 'quiet_hours_end' in data and data['quiet_hours_end']:
                try:
                    preference.quiet_hours_end = datetime.datetime.strptime(data['quiet_hours_end'], '%H:%M').time()
                except ValueError:
                    return jsonify({"error": "Invalid quiet_hours_end format. Use HH:MM (24-hour format)"}), 400
        else:
            # Create new preference
            preference = NotificationPreference(
                user_id=user.id,
                notification_type=data['notification_type'],
                enabled=data.get('enabled', True),
                send_mobile=data.get('send_mobile', True),
                send_watch=data.get('send_watch', True)
            )

            # Parse quiet hours if provided
            if 'quiet_hours_start' in data and data['quiet_hours_start']:
                try:
                    preference.quiet_hours_start = datetime.datetime.strptime(data['quiet_hours_start'], '%H:%M').time()
                except ValueError:
                    return jsonify({"error": "Invalid quiet_hours_start format. Use HH:MM (24-hour format)"}), 400

            if 'quiet_hours_end' in data and data['quiet_hours_end']:
                try:
                    preference.quiet_hours_end = datetime.datetime.strptime(data['quiet_hours_end'], '%H:%M').time()
                except ValueError:
                    return jsonify({"error": "Invalid quiet_hours_end format. Use HH:MM (24-hour format)"}), 400

            db.session.add(preference)

        db.session.commit()

        return jsonify({
            "message": "Notification preference saved",
            "preference_id": preference.id
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@notifications_bp.route('/api/device-tokens', methods=['POST'])
@jwt_required()
def register_device_token():
    """Register a device token for push notifications."""
    try:
        user = get_current_user()

        if not user:
            return jsonify({"error": "User not found"}), 404

        # Get request data
        data = request.get_json()

        # Validate required fields
        required_fields = ['device_type', 'token']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # Validate device type
        valid_types = ['mobile', 'watch']
        if data['device_type'] not in valid_types:
            return jsonify({"error": f"Invalid device type. Must be one of: {', '.join(valid_types)}"}), 400

        # Check if token already exists
        device = DeviceToken.query.filter_by(token=data['token']).first()

        if device:
            # Update existing token
            device.user_id = user.id
            device.device_type = data['device_type']
            device.is_active = True
            device.last_used = datetime.datetime.now()
        else:
            # Create new token
            device = DeviceToken(
                user_id=user.id,
                device_type=data['device_type'],
                token=data['token'],
                is_active=True
            )
            db.session.add(device)

        # Update user's FCM token
        if data['device_type'] == 'mobile':
            user.fcm_token = data['token']
        elif data['device_type'] == 'watch':
            user.watch_token = data['token']

        db.session.commit()

        return jsonify({
            "message": "Device token registered successfully",
            "device_id": device.id
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@notifications_bp.route('/api/device-tokens/<string:token>', methods=['DELETE'])
@jwt_required()
def unregister_device_token(token):
    """Unregister a device token."""
    try:
        user = get_current_user()

        if not user:
            return jsonify({"error": "User not found"}), 404

        # Find the device token
        device = DeviceToken.query.filter_by(token=token, user_id=user.id).first()

        if not device:
            return jsonify({"error": "Device token not found"}), 404

        # Deactivate the token
        device.is_active = False

        # Remove from user if it's the current token
        if device.device_type == 'mobile' and user.fcm_token == token:
            user.fcm_token = None
        elif device.device_type == 'watch' and user.watch_token == token:
            user.watch_token = None

        db.session.commit()

        return jsonify({
            "message": "Device token unregistered successfully"
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@notifications_bp.route('/api/notifications/send', methods=['POST'])
@jwt_required()
@firebase_required
def send_notification():
    """Send a notification to a user."""
    try:
        user = get_current_user()

        if not user:
            return jsonify({"error": "User not found"}), 404

        # Check if user has admin role
        if user.role != 'Admin':
            return jsonify({"error": "Only admins can send notifications"}), 403

        # Get request data
        data = request.get_json()

        # Validate required fields
        required_fields = ['user_id', 'notification_type', 'title', 'message']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # Get target user
        target_user = User.query.get(data['user_id'])
        if not target_user:
            return jsonify({"error": "Target user not found"}), 404

        # Create notification
        notification = create_notification(
            user_id=target_user.id,
            notification_type=data['notification_type'],
            title=data['title'],
            message=data['message'],
            data=data.get('data'),
            scheduled_for=datetime.datetime.now()
        )

        # Deliver notification
        success = deliver_notification(notification, immediate=True)

        return jsonify({
            "message": "Notification sent successfully" if success else "Notification created but delivery failed",
            "notification_id": notification.id,
            "delivery_status": "sent" if success else "failed"
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@notifications_bp.route('/api/notifications/test', methods=['POST'])
@jwt_required()
@firebase_required
def test_notification():
    """Send a test notification to the current user."""
    try:
        user = get_current_user()

        if not user:
            return jsonify({"error": "User not found"}), 404

        # Create test notification
        notification = create_notification(
            user_id=user.id,
            notification_type='test',
            title='Test Notification',
            message='This is a test notification from FitGen.',
            data={'test': True},
            scheduled_for=datetime.datetime.now()
        )

        # Deliver notification
        success = deliver_notification(notification, immediate=True)

        return jsonify({
            "message": "Test notification sent successfully" if success else "Test notification created but delivery failed",
            "notification_id": notification.id,
            "delivery_status": "sent" if success else "failed"
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# Scheduled notification processing
def process_scheduled_notifications():
    """Process all scheduled notifications that are due."""
    try:
        # Get all scheduled notifications that are due
        now = datetime.datetime.now()
        notifications = Notification.query.filter(
            Notification.scheduled_for <= now,
            Notification.sent_at.is_(None)
        ).all()

        for notification in notifications:
            deliver_notification(notification)

        return len(notifications)
    except Exception as e:
        db.session.rollback()
        print(f"Error processing scheduled notifications: {str(e)}")
        return 0

# Automatic notification generation
def generate_meal_reminders():
    """Generate meal reminder notifications for all users."""
    try:
        # Get all users with active meal reminders
        reminders = Reminder.query.filter_by(reminder_type='meal', is_active=True).all()

        # Get current day of week
        today = datetime.datetime.now().strftime('%A')  # e.g., 'Monday'

        for reminder in reminders:
            # Check if reminder is scheduled for today
            if today not in reminder.get_days():
                continue

            # Check if a notification has already been sent today
            user_id = reminder.user_id
            today_date = datetime.datetime.now().date()
            existing_notification = Notification.query.filter(
                Notification.user_id == user_id,
                Notification.notification_type == 'meal_reminder',
                Notification.created_at >= today_date,
                Notification.created_at < today_date + datetime.timedelta(days=1),
                Notification.title == reminder.title
            ).first()

            if existing_notification:
                continue

            # Create notification
            notification = create_notification(
                user_id=user_id,
                notification_type='meal_reminder',
                title=reminder.title,
                message=reminder.description or f"Time for your {reminder.title.lower()}!",
                data={'reminder_id': reminder.id},
                scheduled_for=datetime.datetime.combine(today_date, reminder.time)
            )

        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error generating meal reminders: {str(e)}")
        return False

def generate_workout_reminders():
    """Generate workout reminder notifications for all users."""
    try:
        # Get all users with active workout plans
        user_plans = UserWorkoutPlan.query.filter_by(is_active=True).all()

        # Get current day of week and date
        today = datetime.datetime.now()
        day_of_week = today.weekday()  # 0=Monday, 1=Tuesday, etc.
        today_date = today.date()

        for user_plan in user_plans:
            # Calculate which week of the plan the user is in
            days_elapsed = (today_date - user_plan.start_date).days
            week_number = (days_elapsed // 7) + 1

            # Get today's workout
            workout = Workout.query.filter_by(
                workout_plan_id=user_plan.workout_plan_id,
                week_number=week_number,
                day_of_week=day_of_week
            ).first()

            if not workout:
                continue

            # Check if a notification has already been sent today
            existing_notification = Notification.query.filter(
                Notification.user_id == user_plan.user_id,
                Notification.notification_type == 'workout_reminder',
                Notification.created_at >= today_date,
                Notification.created_at < today_date + datetime.timedelta(days=1)
            ).first()

            if existing_notification:
                continue

            # Create notification
            notification = create_notification(
                user_id=user_plan.user_id,
                notification_type='workout_reminder',
                title=f"Workout: {workout.name}",
                message=workout.description or f"It's time for your {workout.name} workout today!",
                data={'workout_id': workout.id},
                scheduled_for=datetime.datetime.combine(today_date, datetime.time(8, 0))  # 8:00 AM by default
            )

        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error generating workout reminders: {str(e)}")
        return False

def generate_goal_achievement_notifications():
    """Generate notifications for users who have achieved their goals."""
    try:
        # Get all users with health stats
        users = User.query.filter(User.health_stats.any()).all()
        today_date = datetime.datetime.now().date()

        for user in users:
            # Get the most recent health stat
            latest_stat = HealthStat.query.filter_by(user_id=user.id).order_by(HealthStat.date.desc()).first()

            if not latest_stat or latest_stat.date < today_date - datetime.timedelta(days=7):
                continue  # Skip if no recent stats

            # Get the previous health stat for comparison
            previous_stat = HealthStat.query.filter(
                HealthStat.user_id == user.id,
                HealthStat.date < latest_stat.date
            ).order_by(HealthStat.date.desc()).first()

            if not previous_stat:
                continue  # Skip if no previous stats for comparison

            # Check for weight goal achievement
            if user.weight_goal_kg and latest_stat.weight_kg:
                # Weight loss goal
                if user.weight_kg > user.weight_goal_kg and latest_stat.weight_kg <= user.weight_goal_kg:
                    # Create weight goal achievement notification
                    create_notification(
                        user_id=user.id,
                        notification_type='goal_achievement',
                        title='Weight Goal Achieved! 🎉',
                        message=f'Congratulations! You have reached your weight goal of {user.weight_goal_kg} kg.',
                        data={'type': 'weight', 'goal': user.weight_goal_kg, 'current': latest_stat.weight_kg},
                        scheduled_for=datetime.datetime.now()
                    )
                # Weight gain goal
                elif user.weight_kg < user.weight_goal_kg and latest_stat.weight_kg >= user.weight_goal_kg:
                    # Create weight goal achievement notification
                    create_notification(
                        user_id=user.id,
                        notification_type='goal_achievement',
                        title='Weight Goal Achieved! 🎉',
                        message=f'Congratulations! You have reached your weight goal of {user.weight_goal_kg} kg.',
                        data={'type': 'weight', 'goal': user.weight_goal_kg, 'current': latest_stat.weight_kg},
                        scheduled_for=datetime.datetime.now()
                    )

            # Check for steps goal achievement
            if latest_stat.steps and previous_stat.steps:
                # Daily steps goal (10,000 steps by default)
                steps_goal = 10000
                if latest_stat.steps >= steps_goal and previous_stat.steps < steps_goal:
                    # Check if notification already sent today
                    existing_notification = Notification.query.filter(
                        Notification.user_id == user.id,
                        Notification.notification_type == 'goal_achievement',
                        Notification.created_at >= today_date,
                        Notification.created_at < today_date + datetime.timedelta(days=1),
                        Notification.title.like('Step Goal%')
                    ).first()

                    if not existing_notification:
                        # Create steps goal achievement notification
                        create_notification(
                            user_id=user.id,
                            notification_type='goal_achievement',
                            title='Step Goal Achieved! 🚶',
                            message=f'Great job! You have reached your daily step goal of {steps_goal:,} steps.',
                            data={'type': 'steps', 'goal': steps_goal, 'current': latest_stat.steps},
                            scheduled_for=datetime.datetime.now()
                        )

            # Check for calories goal achievement
            if user.diet_goal and latest_stat.calories_consumed:
                # Get nutrition goal
                nutrition_goal = NutritionGoal.query.filter_by(user_id=user.id, is_active=True).first()

                if nutrition_goal and nutrition_goal.calories:
                    # Check if user is within calorie goal
                    calorie_diff = abs(latest_stat.calories_consumed - nutrition_goal.calories)
                    calorie_threshold = nutrition_goal.calories * 0.05  # 5% threshold

                    if calorie_diff <= calorie_threshold:
                        # Check if notification already sent today
                        existing_notification = Notification.query.filter(
                            Notification.user_id == user.id,
                            Notification.notification_type == 'goal_achievement',
                            Notification.created_at >= today_date,
                            Notification.created_at < today_date + datetime.timedelta(days=1),
                            Notification.title.like('Calorie Goal%')
                        ).first()

                        if not existing_notification:
                            # Create calorie goal achievement notification
                            create_notification(
                                user_id=user.id,
                                notification_type='goal_achievement',
                                title='Calorie Goal Achieved! 🍎',
                                message=f'Well done! You have stayed within your daily calorie goal of {nutrition_goal.calories:,} calories.',
                                data={'type': 'calories', 'goal': nutrition_goal.calories, 'current': latest_stat.calories_consumed},
                                scheduled_for=datetime.datetime.now()
                            )

        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error generating goal achievement notifications: {str(e)}")
        return False

# Schedule notification tasks
def schedule_notification_tasks():
    """Schedule all notification tasks to run at appropriate times."""
    # Process any pending notifications
    process_scheduled_notifications()

    # Generate meal reminders for today
    generate_meal_reminders()

    # Generate workout reminders for today
    generate_workout_reminders()

    # Generate goal achievement notifications
    generate_goal_achievement_notifications()

    print(f"Notification tasks scheduled at {datetime.datetime.now()}")
    return True
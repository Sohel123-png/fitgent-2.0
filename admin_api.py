"""
Admin API Module
This module provides API endpoints for admin functionality.
"""

from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from db import db, User, DietPlan, HealthStat, Reminder
from sqlalchemy import func, desc, extract
import datetime
import json

admin_bp = Blueprint('admin', __name__)

def admin_required(fn):
    """Decorator to check if the user is an admin."""
    @jwt_required()
    def wrapper(*args, **kwargs):
        identity = get_jwt_identity()
        if identity['role'] != 'Admin':
            return jsonify({"error": "Admin access required"}), 403
        return fn(*args, **kwargs)
    wrapper.__name__ = fn.__name__
    return wrapper

@admin_bp.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Render the admin dashboard page."""
    return render_template('admin_dashboard.html')

@admin_bp.route('/api/admin/users', methods=['GET'])
@admin_required
def get_users():
    """Get all users."""
    try:
        # Get query parameters for pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')
        
        # Query users with pagination and search
        query = User.query
        
        if search:
            query = query.filter(User.email.like(f'%{search}%'))
        
        users_pagination = query.order_by(User.created_at.desc()).paginate(page=page, per_page=per_page)
        
        # Format the response
        users = []
        for user in users_pagination.items:
            users.append({
                "id": user.id,
                "email": user.email,
                "role": user.role,
                "name": user.name,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "diet_plans_count": len(user.diet_plans),
                "reminders_count": len(user.reminders),
                "health_stats_count": len(user.health_stats)
            })
        
        return jsonify({
            "users": users,
            "total": users_pagination.total,
            "pages": users_pagination.pages,
            "current_page": users_pagination.page
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/api/admin/users/<int:user_id>', methods=['GET'])
@admin_required
def get_user(user_id):
    """Get a specific user."""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Get user's diet plans
        diet_plans = []
        for plan in user.diet_plans:
            diet_plans.append({
                "id": plan.id,
                "created_at": plan.created_at.isoformat() if plan.created_at else None,
                "start_date": plan.start_date.isoformat() if plan.start_date else None,
                "end_date": plan.end_date.isoformat() if plan.end_date else None
            })
        
        # Get user's health stats
        health_stats = []
        for stat in user.health_stats:
            health_stats.append({
                "id": stat.id,
                "date": stat.date.isoformat() if stat.date else None,
                "weight_kg": stat.weight_kg,
                "calories_consumed": stat.calories_consumed,
                "calories_burned": stat.calories_burned,
                "steps": stat.steps,
                "water_ml": stat.water_ml,
                "sleep_hours": stat.sleep_hours
            })
        
        # Get user's reminders
        reminders = []
        for reminder in user.reminders:
            reminders.append({
                "id": reminder.id,
                "reminder_type": reminder.reminder_type,
                "title": reminder.title,
                "time": reminder.time.strftime('%H:%M') if reminder.time else None,
                "days": reminder.get_days(),
                "is_active": reminder.is_active
            })
        
        # Format the response
        user_data = {
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "name": user.name,
            "age": user.age,
            "gender": user.gender,
            "weight_kg": user.weight_kg,
            "height_cm": user.height_cm,
            "activity_level": user.activity_level,
            "diet_goal": user.diet_goal,
            "diet_type": user.diet_type,
            "allergies": user.get_allergies(),
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "diet_plans": diet_plans,
            "health_stats": health_stats,
            "reminders": reminders
        }
        
        return jsonify(user_data), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/api/admin/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    """Update a specific user."""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Get request data
        data = request.get_json()
        
        # Update user fields
        if 'email' in data:
            # Check if email is already taken by another user
            existing_user = User.query.filter(User.email == data['email'], User.id != user_id).first()
            if existing_user:
                return jsonify({"error": "Email already in use"}), 400
            user.email = data['email']
        
        if 'role' in data:
            user.role = data['role']
        
        if 'name' in data:
            user.name = data['name']
        
        if 'age' in data:
            user.age = data['age']
        
        if 'gender' in data:
            user.gender = data['gender']
        
        if 'weight_kg' in data:
            user.weight_kg = data['weight_kg']
        
        if 'height_cm' in data:
            user.height_cm = data['height_cm']
        
        if 'activity_level' in data:
            user.activity_level = data['activity_level']
        
        if 'diet_goal' in data:
            user.diet_goal = data['diet_goal']
        
        if 'diet_type' in data:
            user.diet_type = data['diet_type']
        
        if 'allergies' in data:
            user.set_allergies(data['allergies'])
        
        if 'password' in data and data['password']:
            user.set_password(data['password'])
        
        # Save to database
        db.session.commit()
        
        return jsonify({"message": "User updated successfully"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """Delete a specific user."""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Delete the user
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({"message": "User deleted successfully"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/api/admin/users', methods=['POST'])
@admin_required
def create_user():
    """Create a new user."""
    try:
        # Get request data
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'password']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Check if email is already taken
        if User.query.filter_by(email=data['email']).first():
            return jsonify({"error": "Email already in use"}), 400
        
        # Create a new user
        user = User(
            email=data['email'],
            role=data.get('role', 'User'),
            name=data.get('name', ''),
            age=data.get('age'),
            gender=data.get('gender'),
            weight_kg=data.get('weight_kg'),
            height_cm=data.get('height_cm'),
            activity_level=data.get('activity_level', 'moderate'),
            diet_goal=data.get('diet_goal', 'maintain'),
            diet_type=data.get('diet_type', 'balanced')
        )
        
        # Set password
        user.set_password(data['password'])
        
        # Set allergies if provided
        if 'allergies' in data:
            user.set_allergies(data['allergies'])
        
        # Save to database
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            "message": "User created successfully",
            "user_id": user.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/api/admin/analytics/users', methods=['GET'])
@admin_required
def get_user_analytics():
    """Get user analytics."""
    try:
        # Get total users count
        total_users = User.query.count()
        
        # Get users by role
        users_by_role = db.session.query(
            User.role, func.count(User.id)
        ).group_by(User.role).all()
        
        # Get new users per month for the last 6 months
        six_months_ago = datetime.datetime.now() - datetime.timedelta(days=180)
        new_users_by_month = db.session.query(
            extract('year', User.created_at).label('year'),
            extract('month', User.created_at).label('month'),
            func.count(User.id)
        ).filter(User.created_at >= six_months_ago).group_by('year', 'month').all()
        
        # Format the response
        users_by_role_data = {role: count for role, count in users_by_role}
        
        new_users_by_month_data = []
        for year, month, count in new_users_by_month:
            month_name = datetime.date(int(year), int(month), 1).strftime('%B %Y')
            new_users_by_month_data.append({
                "month": month_name,
                "count": count
            })
        
        return jsonify({
            "total_users": total_users,
            "users_by_role": users_by_role_data,
            "new_users_by_month": new_users_by_month_data
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/api/admin/analytics/activity', methods=['GET'])
@admin_required
def get_activity_analytics():
    """Get activity analytics."""
    try:
        # Get total counts
        total_diet_plans = DietPlan.query.count()
        total_health_stats = HealthStat.query.count()
        total_reminders = Reminder.query.count()
        
        # Get diet plans created per month for the last 6 months
        six_months_ago = datetime.datetime.now() - datetime.timedelta(days=180)
        diet_plans_by_month = db.session.query(
            extract('year', DietPlan.created_at).label('year'),
            extract('month', DietPlan.created_at).label('month'),
            func.count(DietPlan.id)
        ).filter(DietPlan.created_at >= six_months_ago).group_by('year', 'month').all()
        
        # Get most popular diet types
        diet_types = db.session.query(
            User.diet_type, func.count(User.id)
        ).filter(User.diet_type.isnot(None)).group_by(User.diet_type).all()
        
        # Get most popular diet goals
        diet_goals = db.session.query(
            User.diet_goal, func.count(User.id)
        ).filter(User.diet_goal.isnot(None)).group_by(User.diet_goal).all()
        
        # Format the response
        diet_plans_by_month_data = []
        for year, month, count in diet_plans_by_month:
            month_name = datetime.date(int(year), int(month), 1).strftime('%B %Y')
            diet_plans_by_month_data.append({
                "month": month_name,
                "count": count
            })
        
        diet_types_data = {diet_type: count for diet_type, count in diet_types}
        diet_goals_data = {diet_goal: count for diet_goal, count in diet_goals}
        
        return jsonify({
            "total_diet_plans": total_diet_plans,
            "total_health_stats": total_health_stats,
            "total_reminders": total_reminders,
            "diet_plans_by_month": diet_plans_by_month_data,
            "diet_types": diet_types_data,
            "diet_goals": diet_goals_data
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

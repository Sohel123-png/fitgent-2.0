"""
Workout API Module
This module provides API endpoints for workout plans, exercises, and trainer connections.
"""

from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from db import db, User, Exercise, WorkoutPlan, Workout, WorkoutExercise, UserWorkoutPlan
from db import WorkoutLog, ExerciseLog, Trainer, TrainerClient, TrainerMessage, NutritionGoal
import datetime
import json
import os
from sqlalchemy import func, desc

workout_bp = Blueprint('workout', __name__)

# Helper functions
def get_current_user():
    """Get the current user from JWT token."""
    current_user_identity = get_jwt_identity()
    return User.query.filter_by(email=current_user_identity['email']).first()

# Routes
@workout_bp.route('/workout-plans')
def workout_plans_page():
    """Render the workout plans page."""
    return render_template('workout_plans.html')

@workout_bp.route('/workout-tracker')
def workout_tracker_page():
    """Render the workout tracker page."""
    return render_template('workout_tracker.html')

@workout_bp.route('/trainers')
def trainers_page():
    """Render the trainers page."""
    return render_template('trainers.html')

@workout_bp.route('/nutrition-goals')
def nutrition_goals_page():
    """Render the nutrition goals page."""
    return render_template('nutrition_goals.html')

# API Endpoints
@workout_bp.route('/api/exercises', methods=['GET'])
@jwt_required()
def get_exercises():
    """Get all exercises or filter by muscle group, difficulty, or equipment."""
    try:
        # Get query parameters
        muscle_group = request.args.get('muscle_group')
        difficulty = request.args.get('difficulty')
        equipment = request.args.get('equipment')

        # Build query
        query = Exercise.query

        if muscle_group:
            query = query.filter(Exercise.muscle_group == muscle_group)

        if difficulty:
            query = query.filter(Exercise.difficulty == difficulty)

        if equipment:
            query = query.filter(Exercise.equipment == equipment)

        # Execute query
        exercises = query.all()

        # Format response
        result = []
        for exercise in exercises:
            result.append({
                'id': exercise.id,
                'name': exercise.name,
                'description': exercise.description,
                'muscle_group': exercise.muscle_group,
                'difficulty': exercise.difficulty,
                'equipment': exercise.equipment,
                'instructions': exercise.instructions,
                'video_url': exercise.video_url,
                'image_url': exercise.image_url
            })

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@workout_bp.route('/api/exercises/<int:exercise_id>', methods=['GET'])
@jwt_required()
def get_exercise(exercise_id):
    """Get a specific exercise by ID."""
    try:
        exercise = Exercise.query.get(exercise_id)

        if not exercise:
            return jsonify({"error": "Exercise not found"}), 404

        result = {
            'id': exercise.id,
            'name': exercise.name,
            'description': exercise.description,
            'muscle_group': exercise.muscle_group,
            'difficulty': exercise.difficulty,
            'equipment': exercise.equipment,
            'instructions': exercise.instructions,
            'video_url': exercise.video_url,
            'image_url': exercise.image_url
        }

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@workout_bp.route('/api/workout-plans', methods=['GET'])
@jwt_required()
def get_workout_plans():
    """Get all workout plans or filter by difficulty or goal."""
    try:
        user = get_current_user()

        if not user:
            return jsonify({"error": "User not found"}), 404

        # Get query parameters
        difficulty = request.args.get('difficulty')
        goal = request.args.get('goal')

        # Build query for public plans and user's own plans
        query = WorkoutPlan.query.filter(
            (WorkoutPlan.is_public == True) |
            (WorkoutPlan.creator_id == user.id)
        )

        if difficulty:
            query = query.filter(WorkoutPlan.difficulty == difficulty)

        if goal:
            query = query.filter(WorkoutPlan.goal == goal)

        # Execute query
        workout_plans = query.all()

        # Format response
        result = []
        for plan in workout_plans:
            # Check if user is already following this plan
            user_plan = UserWorkoutPlan.query.filter_by(
                user_id=user.id,
                workout_plan_id=plan.id,
                is_active=True
            ).first()

            creator = User.query.get(plan.creator_id) if plan.creator_id else None

            result.append({
                'id': plan.id,
                'name': plan.name,
                'description': plan.description,
                'difficulty': plan.difficulty,
                'duration_weeks': plan.duration_weeks,
                'goal': plan.goal,
                'created_at': plan.created_at.isoformat(),
                'is_public': plan.is_public,
                'creator': creator.name if creator else 'FitGen System',
                'is_following': bool(user_plan),
                'workouts_count': len(plan.workouts)
            })

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@workout_bp.route('/api/workout-plans/<int:plan_id>', methods=['GET'])
@jwt_required()
def get_workout_plan(plan_id):
    """Get a specific workout plan by ID with all workouts and exercises."""
    try:
        user = get_current_user()

        if not user:
            return jsonify({"error": "User not found"}), 404

        plan = WorkoutPlan.query.get(plan_id)

        if not plan:
            return jsonify({"error": "Workout plan not found"}), 404

        # Check if user has access to this plan
        if not plan.is_public and plan.creator_id != user.id:
            return jsonify({"error": "You don't have access to this workout plan"}), 403

        # Get all workouts for this plan
        workouts = []
        for workout in plan.workouts:
            workout_exercises = []

            for we in workout.workout_exercises:
                exercise = we.exercise
                workout_exercises.append({
                    'id': we.id,
                    'exercise_id': exercise.id,
                    'name': exercise.name,
                    'sets': we.sets,
                    'reps': we.reps,
                    'rest_seconds': we.rest_seconds,
                    'order': we.order,
                    'notes': we.notes,
                    'muscle_group': exercise.muscle_group,
                    'equipment': exercise.equipment,
                    'image_url': exercise.image_url
                })

            # Sort exercises by order
            workout_exercises.sort(key=lambda x: x['order'])

            workouts.append({
                'id': workout.id,
                'name': workout.name,
                'description': workout.description,
                'day_of_week': workout.day_of_week,
                'week_number': workout.week_number,
                'duration_minutes': workout.duration_minutes,
                'exercises': workout_exercises
            })

        # Sort workouts by week and day
        workouts.sort(key=lambda x: (x['week_number'], x['day_of_week']))

        # Check if user is following this plan
        user_plan = UserWorkoutPlan.query.filter_by(
            user_id=user.id,
            workout_plan_id=plan.id,
            is_active=True
        ).first()

        creator = User.query.get(plan.creator_id) if plan.creator_id else None

        result = {
            'id': plan.id,
            'name': plan.name,
            'description': plan.description,
            'difficulty': plan.difficulty,
            'duration_weeks': plan.duration_weeks,
            'goal': plan.goal,
            'created_at': plan.created_at.isoformat(),
            'is_public': plan.is_public,
            'creator': creator.name if creator else 'FitGen System',
            'is_following': bool(user_plan),
            'progress': user_plan.progress if user_plan else 0,
            'start_date': user_plan.start_date.isoformat() if user_plan and user_plan.start_date else None,
            'end_date': user_plan.end_date.isoformat() if user_plan and user_plan.end_date else None,
            'workouts': workouts
        }

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@workout_bp.route('/api/workout-plans/<int:plan_id>/follow', methods=['POST'])
@jwt_required()
def follow_workout_plan(plan_id):
    """Start following a workout plan."""
    try:
        user = get_current_user()

        if not user:
            return jsonify({"error": "User not found"}), 404

        plan = WorkoutPlan.query.get(plan_id)

        if not plan:
            return jsonify({"error": "Workout plan not found"}), 404

        # Check if user has access to this plan
        if not plan.is_public and plan.creator_id != user.id:
            return jsonify({"error": "You don't have access to this workout plan"}), 403

        # Check if user is already following this plan
        existing_plan = UserWorkoutPlan.query.filter_by(
            user_id=user.id,
            workout_plan_id=plan.id,
            is_active=True
        ).first()

        if existing_plan:
            return jsonify({"error": "You are already following this workout plan"}), 400

        # Set all other active plans to inactive
        UserWorkoutPlan.query.filter_by(
            user_id=user.id,
            is_active=True
        ).update({'is_active': False})

        # Create new user workout plan
        start_date = datetime.datetime.now().date()
        end_date = start_date + datetime.timedelta(weeks=plan.duration_weeks)

        user_plan = UserWorkoutPlan(
            user_id=user.id,
            workout_plan_id=plan.id,
            start_date=start_date,
            end_date=end_date,
            is_active=True,
            progress=0.0
        )

        db.session.add(user_plan)
        db.session.commit()

        return jsonify({
            "message": "You are now following this workout plan",
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@workout_bp.route('/api/workout-plans/<int:plan_id>/unfollow', methods=['POST'])
@jwt_required()
def unfollow_workout_plan(plan_id):
    """Stop following a workout plan."""
    try:
        user = get_current_user()

        if not user:
            return jsonify({"error": "User not found"}), 404

        # Check if user is following this plan
        user_plan = UserWorkoutPlan.query.filter_by(
            user_id=user.id,
            workout_plan_id=plan_id,
            is_active=True
        ).first()

        if not user_plan:
            return jsonify({"error": "You are not following this workout plan"}), 400

        # Set plan to inactive
        user_plan.is_active = False
        db.session.commit()

        return jsonify({
            "message": "You have stopped following this workout plan"
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@workout_bp.route('/api/user/active-workout-plan', methods=['GET'])
@jwt_required()
def get_active_workout_plan():
    """Get the user's active workout plan."""
    try:
        user = get_current_user()

        if not user:
            return jsonify({"error": "User not found"}), 404

        # Get user's active workout plan
        user_plan = UserWorkoutPlan.query.filter_by(
            user_id=user.id,
            is_active=True
        ).first()

        if not user_plan:
            return jsonify({
                "has_active_plan": False,
                "message": "You are not following any workout plan"
            }), 200

        # Get the workout plan details
        plan = user_plan.workout_plan

        # Calculate days elapsed and remaining
        today = datetime.datetime.now().date()
        days_elapsed = (today - user_plan.start_date).days
        days_remaining = (user_plan.end_date - today).days
        total_days = (user_plan.end_date - user_plan.start_date).days

        # Calculate which workout to do today
        week_number = (days_elapsed // 7) + 1
        day_of_week = today.weekday()  # 0=Monday, 1=Tuesday, etc.

        # Get today's workout
        today_workout = Workout.query.filter_by(
            workout_plan_id=plan.id,
            week_number=week_number,
            day_of_week=day_of_week
        ).first()

        # Format response
        result = {
            'has_active_plan': True,
            'plan_id': plan.id,
            'plan_name': plan.name,
            'difficulty': plan.difficulty,
            'goal': plan.goal,
            'start_date': user_plan.start_date.isoformat(),
            'end_date': user_plan.end_date.isoformat(),
            'progress': user_plan.progress,
            'days_elapsed': days_elapsed,
            'days_remaining': days_remaining,
            'total_days': total_days,
            'current_week': week_number,
            'today_workout': None
        }

        if today_workout:
            workout_exercises = []

            for we in today_workout.workout_exercises:
                exercise = we.exercise
                workout_exercises.append({
                    'id': we.id,
                    'exercise_id': exercise.id,
                    'name': exercise.name,
                    'sets': we.sets,
                    'reps': we.reps,
                    'rest_seconds': we.rest_seconds,
                    'order': we.order,
                    'notes': we.notes,
                    'muscle_group': exercise.muscle_group,
                    'equipment': exercise.equipment,
                    'image_url': exercise.image_url
                })

            # Sort exercises by order
            workout_exercises.sort(key=lambda x: x['order'])

            result['today_workout'] = {
                'id': today_workout.id,
                'name': today_workout.name,
                'description': today_workout.description,
                'duration_minutes': today_workout.duration_minutes,
                'exercises': workout_exercises
            }

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@workout_bp.route('/api/workout-logs', methods=['POST'])
@jwt_required()
def log_workout():
    """Log a completed workout."""
    try:
        user = get_current_user()

        if not user:
            return jsonify({"error": "User not found"}), 404

        # Get request data
        data = request.get_json()

        # Validate required fields
        required_fields = ['workout_id', 'date', 'duration_minutes', 'exercise_logs']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # Parse date
        try:
            date = datetime.datetime.strptime(data['date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

        # Create workout log
        workout_log = WorkoutLog(
            user_id=user.id,
            workout_id=data['workout_id'],
            date=date,
            duration_minutes=data['duration_minutes'],
            calories_burned=data.get('calories_burned'),
            notes=data.get('notes'),
            rating=data.get('rating')
        )

        db.session.add(workout_log)
        db.session.flush()  # Get ID without committing

        # Add exercise logs
        for exercise_data in data['exercise_logs']:
            # Validate required fields
            if 'exercise_id' not in exercise_data or 'sets_completed' not in exercise_data:
                db.session.rollback()
                return jsonify({"error": "Each exercise log must have exercise_id and sets_completed"}), 400

            # Create exercise log
            exercise_log = ExerciseLog(
                workout_log_id=workout_log.id,
                exercise_id=exercise_data['exercise_id'],
                sets_completed=exercise_data['sets_completed'],
                reps=json.dumps(exercise_data.get('reps', [])),
                weights=json.dumps(exercise_data.get('weights', [])),
                notes=exercise_data.get('notes')
            )

            db.session.add(exercise_log)

        # Update user's active workout plan progress
        user_plan = UserWorkoutPlan.query.filter_by(
            user_id=user.id,
            is_active=True
        ).first()

        if user_plan:
            # Get total number of workouts in the plan
            total_workouts = Workout.query.filter_by(
                workout_plan_id=user_plan.workout_plan_id
            ).count()

            # Get number of completed workouts
            completed_workouts = WorkoutLog.query.filter(
                WorkoutLog.user_id == user.id,
                WorkoutLog.date >= user_plan.start_date,
                WorkoutLog.date <= user_plan.end_date
            ).count() + 1  # +1 for the current workout

            # Update progress
            if total_workouts > 0:
                user_plan.progress = min(100.0, (completed_workouts / total_workouts) * 100)

        db.session.commit()

        return jsonify({
            "message": "Workout logged successfully",
            "workout_log_id": workout_log.id,
            "progress": user_plan.progress if user_plan else None
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@workout_bp.route('/api/workout-logs', methods=['GET'])
@jwt_required()
def get_workout_logs():
    """Get workout logs for the current user."""
    try:
        user = get_current_user()

        if not user:
            return jsonify({"error": "User not found"}), 404

        # Get query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = request.args.get('limit', 10, type=int)

        # Build query
        query = WorkoutLog.query.filter_by(user_id=user.id)

        if start_date:
            try:
                start = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
                query = query.filter(WorkoutLog.date >= start)
            except ValueError:
                return jsonify({"error": "Invalid start_date format. Use YYYY-MM-DD"}), 400

        if end_date:
            try:
                end = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
                query = query.filter(WorkoutLog.date <= end)
            except ValueError:
                return jsonify({"error": "Invalid end_date format. Use YYYY-MM-DD"}), 400

        # Order by date descending and limit results
        logs = query.order_by(WorkoutLog.date.desc()).limit(limit).all()

        # Format response
        result = []
        for log in logs:
            workout = Workout.query.get(log.workout_id) if log.workout_id else None

            # Get exercise logs
            exercise_logs = []
            for ex_log in log.exercise_logs:
                exercise = Exercise.query.get(ex_log.exercise_id)

                if not exercise:
                    continue

                exercise_logs.append({
                    'id': ex_log.id,
                    'exercise_id': ex_log.exercise_id,
                    'name': exercise.name,
                    'sets_completed': ex_log.sets_completed,
                    'reps': json.loads(ex_log.reps) if ex_log.reps else [],
                    'weights': json.loads(ex_log.weights) if ex_log.weights else [],
                    'notes': ex_log.notes,
                    'muscle_group': exercise.muscle_group,
                    'equipment': exercise.equipment
                })

            result.append({
                'id': log.id,
                'date': log.date.isoformat(),
                'workout_id': log.workout_id,
                'workout_name': workout.name if workout else 'Custom Workout',
                'duration_minutes': log.duration_minutes,
                'calories_burned': log.calories_burned,
                'notes': log.notes,
                'rating': log.rating,
                'exercise_logs': exercise_logs
            })

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@workout_bp.route('/api/trainers', methods=['GET'])
@jwt_required()
def get_trainers():
    """Get all available trainers."""
    try:
        # Get query parameters
        specialization = request.args.get('specialization')

        # Build query
        query = Trainer.query.filter_by(is_available=True)

        if specialization:
            query = query.filter(Trainer.specialization == specialization)

        # Execute query
        trainers = query.all()

        # Format response
        result = []
        for trainer in trainers:
            user = User.query.get(trainer.user_id)

            if not user:
                continue

            result.append({
                'id': trainer.id,
                'user_id': trainer.user_id,
                'name': user.name,
                'bio': trainer.bio,
                'specialization': trainer.specialization,
                'experience_years': trainer.experience_years,
                'certification': trainer.certification,
                'hourly_rate': trainer.hourly_rate
            })

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@workout_bp.route('/api/trainers/<int:trainer_id>', methods=['GET'])
@jwt_required()
def get_trainer(trainer_id):
    """Get a specific trainer by ID."""
    try:
        trainer = Trainer.query.get(trainer_id)

        if not trainer:
            return jsonify({"error": "Trainer not found"}), 404

        user = User.query.get(trainer.user_id)

        if not user:
            return jsonify({"error": "Trainer user not found"}), 404

        # Get trainer's workout plans
        plans = WorkoutPlan.query.filter_by(
            creator_id=trainer.user_id,
            is_public=True
        ).all()

        workout_plans = []
        for plan in plans:
            workout_plans.append({
                'id': plan.id,
                'name': plan.name,
                'description': plan.description,
                'difficulty': plan.difficulty,
                'duration_weeks': plan.duration_weeks,
                'goal': plan.goal
            })

        result = {
            'id': trainer.id,
            'user_id': trainer.user_id,
            'name': user.name,
            'bio': trainer.bio,
            'specialization': trainer.specialization,
            'experience_years': trainer.experience_years,
            'certification': trainer.certification,
            'hourly_rate': trainer.hourly_rate,
            'workout_plans': workout_plans
        }

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@workout_bp.route('/api/trainers/<int:trainer_id>/request', methods=['POST'])
@jwt_required()
def request_trainer(trainer_id):
    """Request a trainer for 1-on-1 coaching."""
    try:
        user = get_current_user()

        if not user:
            return jsonify({"error": "User not found"}), 404

        trainer = Trainer.query.get(trainer_id)

        if not trainer:
            return jsonify({"error": "Trainer not found"}), 404

        # Check if user already has an active request with this trainer
        existing_request = TrainerClient.query.filter_by(
            trainer_id=trainer.id,
            client_id=user.id,
            status='pending'
        ).first()

        if existing_request:
            return jsonify({"error": "You already have a pending request with this trainer"}), 400

        # Check if user already has an active relationship with this trainer
        existing_relationship = TrainerClient.query.filter_by(
            trainer_id=trainer.id,
            client_id=user.id,
            status='active'
        ).first()

        if existing_relationship:
            return jsonify({"error": "You are already working with this trainer"}), 400

        # Get request data
        data = request.get_json() or {}

        # Create trainer client relationship
        trainer_client = TrainerClient(
            trainer_id=trainer.id,
            client_id=user.id,
            status='pending'
        )

        db.session.add(trainer_client)
        db.session.flush()  # Get ID without committing

        # Add initial message if provided
        if 'message' in data and data['message']:
            message = TrainerMessage(
                trainer_client_id=trainer_client.id,
                sender_id=user.id,
                content=data['message']
            )

            db.session.add(message)

        db.session.commit()

        return jsonify({
            "message": "Trainer request sent successfully",
            "trainer_client_id": trainer_client.id
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@workout_bp.route('/api/trainer-clients', methods=['GET'])
@jwt_required()
def get_trainer_clients():
    """Get all trainer-client relationships for the current user (as either trainer or client)."""
    try:
        user = get_current_user()

        if not user:
            return jsonify({"error": "User not found"}), 404

        # Check if user is a trainer
        trainer = Trainer.query.filter_by(user_id=user.id).first()

        result = {
            'as_trainer': [],
            'as_client': []
        }

        # Get relationships where user is the trainer
        if trainer:
            trainer_clients = TrainerClient.query.filter_by(trainer_id=trainer.id).all()

            for tc in trainer_clients:
                client = User.query.get(tc.client_id)

                if not client:
                    continue

                # Get latest message
                latest_message = TrainerMessage.query.filter_by(
                    trainer_client_id=tc.id
                ).order_by(TrainerMessage.timestamp.desc()).first()

                result['as_trainer'].append({
                    'id': tc.id,
                    'client_id': tc.client_id,
                    'client_name': client.name,
                    'status': tc.status,
                    'start_date': tc.start_date.isoformat() if tc.start_date else None,
                    'end_date': tc.end_date.isoformat() if tc.end_date else None,
                    'created_at': tc.created_at.isoformat(),
                    'latest_message': {
                        'content': latest_message.content,
                        'sender_id': latest_message.sender_id,
                        'timestamp': latest_message.timestamp.isoformat(),
                        'is_read': latest_message.is_read
                    } if latest_message else None
                })

        # Get relationships where user is the client
        client_trainers = TrainerClient.query.filter_by(client_id=user.id).all()

        for ct in client_trainers:
            trainer_obj = Trainer.query.get(ct.trainer_id)

            if not trainer_obj:
                continue

            trainer_user = User.query.get(trainer_obj.user_id)

            if not trainer_user:
                continue

            # Get latest message
            latest_message = TrainerMessage.query.filter_by(
                trainer_client_id=ct.id
            ).order_by(TrainerMessage.timestamp.desc()).first()

            result['as_client'].append({
                'id': ct.id,
                'trainer_id': ct.trainer_id,
                'trainer_name': trainer_user.name,
                'status': ct.status,
                'start_date': ct.start_date.isoformat() if ct.start_date else None,
                'end_date': ct.end_date.isoformat() if ct.end_date else None,
                'created_at': ct.created_at.isoformat(),
                'latest_message': {
                    'content': latest_message.content,
                    'sender_id': latest_message.sender_id,
                    'timestamp': latest_message.timestamp.isoformat(),
                    'is_read': latest_message.is_read
                } if latest_message else None
            })

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@workout_bp.route('/api/trainer-clients/<int:trainer_client_id>/messages', methods=['GET'])
@jwt_required()
def get_trainer_messages(trainer_client_id):
    """Get all messages for a trainer-client relationship."""
    try:
        user = get_current_user()

        if not user:
            return jsonify({"error": "User not found"}), 404

        # Get the trainer-client relationship
        trainer_client = TrainerClient.query.get(trainer_client_id)

        if not trainer_client:
            return jsonify({"error": "Trainer-client relationship not found"}), 404

        # Check if user is part of this relationship
        trainer = Trainer.query.filter_by(id=trainer_client.trainer_id).first()

        if not trainer:
            return jsonify({"error": "Trainer not found"}), 404

        if trainer.user_id != user.id and trainer_client.client_id != user.id:
            return jsonify({"error": "You don't have access to these messages"}), 403

        # Get all messages
        messages = TrainerMessage.query.filter_by(
            trainer_client_id=trainer_client.id
        ).order_by(TrainerMessage.timestamp.asc()).all()

        # Format response
        result = []
        for message in messages:
            sender = User.query.get(message.sender_id)

            if not sender:
                continue

            # Mark message as read if user is the recipient
            if message.sender_id != user.id and not message.is_read:
                message.is_read = True
                db.session.commit()

            result.append({
                'id': message.id,
                'sender_id': message.sender_id,
                'sender_name': sender.name,
                'content': message.content,
                'timestamp': message.timestamp.isoformat(),
                'is_read': message.is_read
            })

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@workout_bp.route('/api/trainer-clients/<int:trainer_client_id>/messages', methods=['POST'])
@jwt_required()
def send_trainer_message(trainer_client_id):
    """Send a message in a trainer-client relationship."""
    try:
        user = get_current_user()

        if not user:
            return jsonify({"error": "User not found"}), 404

        # Get the trainer-client relationship
        trainer_client = TrainerClient.query.get(trainer_client_id)

        if not trainer_client:
            return jsonify({"error": "Trainer-client relationship not found"}), 404

        # Check if user is part of this relationship
        trainer = Trainer.query.filter_by(id=trainer_client.trainer_id).first()

        if not trainer:
            return jsonify({"error": "Trainer not found"}), 404

        if trainer.user_id != user.id and trainer_client.client_id != user.id:
            return jsonify({"error": "You don't have access to this conversation"}), 403

        # Get request data
        data = request.get_json()

        if 'content' not in data or not data['content'].strip():
            return jsonify({"error": "Message content is required"}), 400

        # Create message
        message = TrainerMessage(
            trainer_client_id=trainer_client.id,
            sender_id=user.id,
            content=data['content'].strip()
        )

        db.session.add(message)
        db.session.commit()

        return jsonify({
            'id': message.id,
            'sender_id': message.sender_id,
            'sender_name': user.name,
            'content': message.content,
            'timestamp': message.timestamp.isoformat(),
            'is_read': message.is_read
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@workout_bp.route('/api/trainer-clients/<int:trainer_client_id>/status', methods=['PUT'])
@jwt_required()
def update_trainer_client_status(trainer_client_id):
    """Update the status of a trainer-client relationship."""
    try:
        user = get_current_user()

        if not user:
            return jsonify({"error": "User not found"}), 404

        # Get the trainer-client relationship
        trainer_client = TrainerClient.query.get(trainer_client_id)

        if not trainer_client:
            return jsonify({"error": "Trainer-client relationship not found"}), 404

        # Check if user is the trainer
        trainer = Trainer.query.filter_by(id=trainer_client.trainer_id).first()

        if not trainer or trainer.user_id != user.id:
            return jsonify({"error": "Only the trainer can update the status"}), 403

        # Get request data
        data = request.get_json()

        if 'status' not in data:
            return jsonify({"error": "Status is required"}), 400

        # Validate status
        valid_statuses = ['pending', 'active', 'completed', 'cancelled']
        if data['status'] not in valid_statuses:
            return jsonify({"error": f"Invalid status. Choose from: {', '.join(valid_statuses)}"}), 400

        # Update status
        old_status = trainer_client.status
        trainer_client.status = data['status']

        # Set start date if activating
        if data['status'] == 'active' and old_status != 'active':
            trainer_client.start_date = datetime.datetime.now().date()

        # Set end date if completing or cancelling
        if data['status'] in ['completed', 'cancelled'] and old_status == 'active':
            trainer_client.end_date = datetime.datetime.now().date()

        db.session.commit()

        return jsonify({
            "message": f"Status updated to {data['status']}",
            "start_date": trainer_client.start_date.isoformat() if trainer_client.start_date else None,
            "end_date": trainer_client.end_date.isoformat() if trainer_client.end_date else None
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@workout_bp.route('/api/nutrition-goals', methods=['GET'])
@jwt_required()
def get_nutrition_goals():
    """Get the user's nutrition goals."""
    try:
        user = get_current_user()

        if not user:
            return jsonify({"error": "User not found"}), 404

        # Get active nutrition goal
        active_goal = NutritionGoal.query.filter_by(
            user_id=user.id,
            is_active=True
        ).first()

        # Get historical goals
        historical_goals = NutritionGoal.query.filter_by(
            user_id=user.id,
            is_active=False
        ).order_by(NutritionGoal.end_date.desc()).limit(5).all()

        # Format response
        result = {
            'active_goal': None,
            'historical_goals': []
        }

        if active_goal:
            result['active_goal'] = {
                'id': active_goal.id,
                'calories': active_goal.calories,
                'protein_g': active_goal.protein_g,
                'carbs_g': active_goal.carbs_g,
                'fat_g': active_goal.fat_g,
                'start_date': active_goal.start_date.isoformat(),
                'end_date': active_goal.end_date.isoformat() if active_goal.end_date else None
            }

        for goal in historical_goals:
            result['historical_goals'].append({
                'id': goal.id,
                'calories': goal.calories,
                'protein_g': goal.protein_g,
                'carbs_g': goal.carbs_g,
                'fat_g': goal.fat_g,
                'start_date': goal.start_date.isoformat(),
                'end_date': goal.end_date.isoformat() if goal.end_date else None
            })

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@workout_bp.route('/api/nutrition-goals', methods=['POST'])
@jwt_required()
def create_nutrition_goal():
    """Create a new nutrition goal."""
    try:
        user = get_current_user()

        if not user:
            return jsonify({"error": "User not found"}), 404

        # Get request data
        data = request.get_json()

        # Validate required fields
        required_fields = ['calories', 'protein_g', 'carbs_g', 'fat_g']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # Set all current active goals to inactive
        NutritionGoal.query.filter_by(
            user_id=user.id,
            is_active=True
        ).update({'is_active': False, 'end_date': datetime.datetime.now().date()})

        # Create new goal
        goal = NutritionGoal(
            user_id=user.id,
            calories=data['calories'],
            protein_g=data['protein_g'],
            carbs_g=data['carbs_g'],
            fat_g=data['fat_g'],
            start_date=datetime.datetime.now().date(),
            is_active=True
        )

        db.session.add(goal)
        db.session.commit()

        return jsonify({
            'id': goal.id,
            'calories': goal.calories,
            'protein_g': goal.protein_g,
            'carbs_g': goal.carbs_g,
            'fat_g': goal.fat_g,
            'start_date': goal.start_date.isoformat(),
            'message': 'Nutrition goal created successfully'
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
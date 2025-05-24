"""
AI Health Recommendation Engine for FitGent 2.0
Provides personalized health recommendations based on smartwatch data and user patterns.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from db import db, User, FitnessData, HealthStat, Notification
import datetime
import json
from typing import Dict, List, Optional
import statistics

health_ai_bp = Blueprint('health_ai', __name__)

class HealthAIEngine:
    """AI-powered health recommendation engine."""

    @staticmethod
    def generate_personalized_recommendations(user_id: int, health_data: Dict) -> Dict:
        """
        Generate comprehensive personalized health recommendations.
        """
        try:
            recommendations = {
                'hydration': [],
                'movement': [],
                'nutrition': [],
                'sleep': [],
                'stress': [],
                'study_breaks': [],
                'achievements': [],
                'wellness_score': 0
            }

            metrics = health_data.get('metrics', {})
            user = User.query.get(user_id)

            # Get historical data for trend analysis
            historical_data = HealthAIEngine._get_historical_trends(user_id)

            # Generate movement recommendations
            recommendations['movement'] = HealthAIEngine._generate_movement_recommendations(
                metrics, historical_data, user
            )

            # Generate hydration recommendations
            recommendations['hydration'] = HealthAIEngine._generate_hydration_recommendations(
                metrics, user
            )

            # Generate nutrition recommendations
            recommendations['nutrition'] = HealthAIEngine._generate_nutrition_recommendations(
                metrics, historical_data, user
            )

            # Generate sleep recommendations
            recommendations['sleep'] = HealthAIEngine._generate_sleep_recommendations(
                metrics, historical_data
            )

            # Generate stress management recommendations
            recommendations['stress'] = HealthAIEngine._generate_stress_recommendations(
                metrics, historical_data
            )

            # Generate study break recommendations
            recommendations['study_breaks'] = HealthAIEngine._generate_study_break_recommendations(
                metrics, user
            )

            # Generate achievements
            recommendations['achievements'] = HealthAIEngine._generate_achievements(
                metrics, historical_data, user
            )

            # Calculate wellness score
            recommendations['wellness_score'] = HealthAIEngine._calculate_wellness_score(
                metrics, historical_data
            )

            return recommendations

        except Exception as e:
            print(f"Error generating personalized recommendations: {str(e)}")
            return {'error': str(e)}

    @staticmethod
    def _get_historical_trends(user_id: int, days: int = 7) -> Dict:
        """Get historical health data trends."""
        try:
            end_date = datetime.date.today()
            start_date = end_date - datetime.timedelta(days=days-1)

            health_stats = HealthStat.query.filter(
                HealthStat.user_id == user_id,
                HealthStat.date >= start_date,
                HealthStat.date <= end_date
            ).order_by(HealthStat.date).all()

            if not health_stats:
                return {}

            steps_data = [stat.steps for stat in health_stats if stat.steps]
            sleep_data = [stat.sleep_hours for stat in health_stats if stat.sleep_hours]
            calories_data = [stat.calories_burned for stat in health_stats if stat.calories_burned]

            trends = {}

            if steps_data:
                trends['avg_steps'] = statistics.mean(steps_data)
                trends['steps_trend'] = 'increasing' if len(steps_data) > 1 and steps_data[-1] > steps_data[0] else 'stable'
                trends['best_step_day'] = max(steps_data)
                trends['consistent_days'] = len([s for s in steps_data if s >= 8000])

            if sleep_data:
                trends['avg_sleep'] = statistics.mean(sleep_data)
                trends['sleep_consistency'] = statistics.stdev(sleep_data) if len(sleep_data) > 1 else 0
                trends['good_sleep_days'] = len([s for s in sleep_data if 7 <= s <= 9])

            if calories_data:
                trends['avg_calories'] = statistics.mean(calories_data)
                trends['active_days'] = len([c for c in calories_data if c >= 300])

            return trends

        except Exception as e:
            print(f"Error getting historical trends: {str(e)}")
            return {}

    @staticmethod
    def _generate_movement_recommendations(metrics: Dict, trends: Dict, user) -> List[Dict]:
        """Generate personalized movement recommendations."""
        recommendations = []
        steps = metrics.get('steps', 0)
        avg_steps = trends.get('avg_steps', 0)

        current_hour = datetime.datetime.now().hour

        # Morning recommendations (6-12)
        if 6 <= current_hour <= 12:
            if steps < 2000:
                recommendations.append({
                    'type': 'urgent',
                    'priority': 'high',
                    'message': 'Start your day with movement! Take a 10-minute morning walk.',
                    'action': 'Go for a quick walk or do 5 minutes of stretching',
                    'estimated_benefit': '+500 steps, improved energy',
                    'timing': 'now'
                })

        # Afternoon recommendations (12-18)
        elif 12 <= current_hour <= 18:
            if steps < avg_steps * 0.6:
                recommendations.append({
                    'type': 'suggestion',
                    'priority': 'medium',
                    'message': f'You\'re behind your usual pace. You have {steps} steps vs your average {int(avg_steps)}.',
                    'action': 'Take the stairs, walk during lunch, or do desk exercises',
                    'estimated_benefit': f'+{int(avg_steps - steps)} steps to reach your average',
                    'timing': 'within 2 hours'
                })

        # Evening recommendations (18-22)
        elif 18 <= current_hour <= 22:
            if steps < 8000:
                recommendations.append({
                    'type': 'reminder',
                    'priority': 'medium',
                    'message': f'Evening movement boost! {8000 - steps} more steps to reach 8K goal.',
                    'action': 'Take an evening walk or do light exercises',
                    'estimated_benefit': 'Better sleep quality, goal achievement',
                    'timing': 'before bedtime'
                })

        # Achievement recognition
        if steps >= 10000:
            recommendations.append({
                'type': 'achievement',
                'priority': 'positive',
                'message': '🎉 Fantastic! You\'ve crushed your 10K step goal!',
                'action': 'Keep up the great work tomorrow',
                'estimated_benefit': 'Excellent cardiovascular health',
                'badge': 'Step Master'
            })

        return recommendations

    @staticmethod
    def _generate_hydration_recommendations(metrics: Dict, user) -> List[Dict]:
        """Generate smart hydration recommendations."""
        recommendations = []
        weight_kg = metrics.get('weight_kg', user.weight_kg if user else 70)
        steps = metrics.get('steps', 0)
        calories_burned = metrics.get('calories_burned', 0)

        # Base water requirement: 35ml per kg body weight
        base_water_ml = weight_kg * 35

        # Additional water for activity
        activity_water = (steps / 1000) * 50 + (calories_burned / 100) * 100
        total_recommended = base_water_ml + activity_water

        current_hour = datetime.datetime.now().hour

        if 6 <= current_hour <= 10:
            recommendations.append({
                'type': 'morning_boost',
                'priority': 'high',
                'message': 'Start your day hydrated! Drink 2 glasses of water.',
                'action': 'Drink 500ml of water to kickstart your metabolism',
                'estimated_benefit': 'Better energy, improved focus',
                'timing': 'within 30 minutes'
            })

        if calories_burned > 300:
            recommendations.append({
                'type': 'activity_hydration',
                'priority': 'high',
                'message': f'You\'ve burned {calories_burned} calories! Time to rehydrate.',
                'action': f'Drink an extra {int(activity_water)}ml of water',
                'estimated_benefit': 'Optimal recovery, maintained performance',
                'timing': 'now'
            })

        recommendations.append({
            'type': 'daily_goal',
            'priority': 'info',
            'message': f'Daily hydration goal: {int(total_recommended)}ml based on your activity.',
            'action': 'Sip water regularly throughout the day',
            'estimated_benefit': 'Optimal hydration for your lifestyle',
            'timing': 'throughout the day'
        })

        return recommendations

    @staticmethod
    def _generate_nutrition_recommendations(metrics: Dict, trends: Dict, user) -> List[Dict]:
        """Generate intelligent nutrition recommendations."""
        recommendations = []
        calories_burned = metrics.get('calories_burned', 0)
        steps = metrics.get('steps', 0)
        current_hour = datetime.datetime.now().hour

        # Pre-workout nutrition (if high activity detected)
        if calories_burned > 200 and 6 <= current_hour <= 10:
            recommendations.append({
                'type': 'pre_workout',
                'priority': 'medium',
                'message': 'Fuel your active morning! Have a balanced breakfast.',
                'action': 'Eat protein + complex carbs (eggs with toast, or oatmeal with nuts)',
                'estimated_benefit': 'Sustained energy, better performance',
                'timing': '30-60 minutes before activity'
            })

        # Post-workout nutrition
        if calories_burned > 400:
            recommendations.append({
                'type': 'post_workout',
                'priority': 'high',
                'message': f'Great workout! You burned {calories_burned} calories.',
                'action': 'Have a protein-rich snack within 30 minutes (Greek yogurt, protein shake)',
                'estimated_benefit': 'Faster recovery, muscle preservation',
                'timing': 'within 30 minutes'
            })

        # Study fuel recommendations
        if 9 <= current_hour <= 17:  # Study/work hours
            recommendations.append({
                'type': 'brain_fuel',
                'priority': 'medium',
                'message': 'Keep your brain sharp! Choose smart snacks.',
                'action': 'Try nuts, berries, dark chocolate, or green tea',
                'estimated_benefit': 'Better focus, sustained mental energy',
                'timing': 'during study breaks'
            })

        # Evening nutrition
        if 18 <= current_hour <= 20 and steps > 8000:
            recommendations.append({
                'type': 'recovery_dinner',
                'priority': 'medium',
                'message': 'You\'ve been active today! Time for a recovery meal.',
                'action': 'Include lean protein, vegetables, and complex carbs',
                'estimated_benefit': 'Muscle recovery, better sleep',
                'timing': '2-3 hours before bed'
            })

        return recommendations

    @staticmethod
    def _generate_sleep_recommendations(metrics: Dict, trends: Dict) -> List[Dict]:
        """Generate personalized sleep recommendations."""
        recommendations = []
        sleep_hours = metrics.get('sleep_hours', 0)
        avg_sleep = trends.get('avg_sleep', 0)
        sleep_consistency = trends.get('sleep_consistency', 0)

        current_hour = datetime.datetime.now().hour

        # Sleep quality analysis
        if sleep_hours > 0:
            if sleep_hours < 6:
                recommendations.append({
                    'type': 'urgent',
                    'priority': 'high',
                    'message': f'Only {sleep_hours:.1f} hours of sleep detected. This affects your health!',
                    'action': 'Aim for 7-9 hours tonight. Set a bedtime reminder.',
                    'estimated_benefit': 'Better recovery, improved focus, stronger immunity',
                    'timing': 'tonight'
                })
            elif 7 <= sleep_hours <= 9:
                recommendations.append({
                    'type': 'achievement',
                    'priority': 'positive',
                    'message': f'Perfect sleep duration! {sleep_hours:.1f} hours is ideal. 😴',
                    'action': 'Maintain this sleep schedule',
                    'estimated_benefit': 'Optimal recovery and performance',
                    'badge': 'Sleep Champion'
                })

        # Sleep consistency recommendations
        if sleep_consistency > 1.5:  # High variability
            recommendations.append({
                'type': 'consistency',
                'priority': 'medium',
                'message': 'Your sleep schedule varies significantly. Consistency helps!',
                'action': 'Try to sleep and wake at the same time daily',
                'estimated_benefit': 'Better sleep quality, easier wake-ups',
                'timing': 'establish routine'
            })

        # Evening wind-down recommendations
        if 20 <= current_hour <= 22:
            recommendations.append({
                'type': 'wind_down',
                'priority': 'medium',
                'message': 'Start winding down for better sleep quality.',
                'action': 'Dim lights, avoid screens, try reading or meditation',
                'estimated_benefit': 'Faster sleep onset, deeper sleep',
                'timing': '1-2 hours before bed'
            })

        return recommendations

    @staticmethod
    def _generate_stress_recommendations(metrics: Dict, trends: Dict) -> List[Dict]:
        """Generate stress management recommendations."""
        recommendations = []
        stress_level = metrics.get('stress_level', 0)
        heart_rate = metrics.get('heart_rate_avg', 0)

        if stress_level > 7:
            recommendations.append({
                'type': 'urgent',
                'priority': 'high',
                'message': 'Elevated stress levels detected. Take a break!',
                'action': 'Try 5 minutes of deep breathing or a short walk',
                'estimated_benefit': 'Reduced stress, better focus',
                'timing': 'now'
            })
        elif stress_level > 5:
            recommendations.append({
                'type': 'prevention',
                'priority': 'medium',
                'message': 'Moderate stress detected. Prevent it from escalating.',
                'action': 'Take micro-breaks every hour, practice mindfulness',
                'estimated_benefit': 'Maintained calm, sustained productivity',
                'timing': 'throughout the day'
            })

        if heart_rate > 100:
            recommendations.append({
                'type': 'heart_rate_alert',
                'priority': 'high',
                'message': f'Elevated heart rate ({heart_rate} bpm) detected.',
                'action': 'Sit down, breathe deeply, and relax for a few minutes',
                'estimated_benefit': 'Cardiovascular health, stress reduction',
                'timing': 'immediately'
            })

        return recommendations

    @staticmethod
    def _generate_study_break_recommendations(metrics: Dict, user) -> List[Dict]:
        """Generate smart study break recommendations."""
        recommendations = []
        current_hour = datetime.datetime.now().hour
        steps = metrics.get('steps', 0)

        # Study hours detection (9 AM - 6 PM)
        if 9 <= current_hour <= 18:
            # Low activity during study hours
            if steps < (current_hour - 6) * 200:  # Expected steps per hour
                recommendations.append({
                    'type': 'study_break',
                    'priority': 'medium',
                    'message': 'Time for an active study break! Your body needs movement.',
                    'action': 'Do 2 minutes of stretching, walk around, or do jumping jacks',
                    'estimated_benefit': 'Better focus, reduced fatigue, improved circulation',
                    'timing': 'every 45-60 minutes'
                })

            # Pomodoro-style recommendations
            recommendations.append({
                'type': 'productivity_break',
                'priority': 'info',
                'message': 'Maximize your study efficiency with regular breaks.',
                'action': 'Study for 25 minutes, then take a 5-minute active break',
                'estimated_benefit': 'Enhanced learning, better retention',
                'timing': 'every 25-30 minutes'
            })

        return recommendations

    @staticmethod
    def _generate_achievements(metrics: Dict, trends: Dict, user) -> List[Dict]:
        """Generate achievement badges and recognition."""
        achievements = []
        steps = metrics.get('steps', 0)
        sleep_hours = metrics.get('sleep_hours', 0)
        calories_burned = metrics.get('calories_burned', 0)

        # Step achievements
        if steps >= 15000:
            achievements.append({
                'type': 'elite',
                'badge': 'Step Elite',
                'message': f'Incredible! {steps} steps today! You\'re in the top 5%!',
                'icon': '🏆',
                'points': 100
            })
        elif steps >= 12000:
            achievements.append({
                'type': 'excellent',
                'badge': 'Step Champion',
                'message': f'Outstanding! {steps} steps shows real dedication!',
                'icon': '🥇',
                'points': 75
            })
        elif steps >= 10000:
            achievements.append({
                'type': 'good',
                'badge': 'Daily Walker',
                'message': f'Great job! You hit your 10K step goal!',
                'icon': '🚶‍♂️',
                'points': 50
            })

        # Sleep achievements
        if 7.5 <= sleep_hours <= 8.5:
            achievements.append({
                'type': 'excellent',
                'badge': 'Sleep Master',
                'message': f'Perfect sleep! {sleep_hours:.1f} hours is optimal.',
                'icon': '😴',
                'points': 60
            })

        # Calorie burn achievements
        if calories_burned >= 600:
            achievements.append({
                'type': 'excellent',
                'badge': 'Calorie Crusher',
                'message': f'Amazing workout! {calories_burned} calories burned!',
                'icon': '🔥',
                'points': 80
            })

        # Consistency achievements
        consistent_days = trends.get('consistent_days', 0)
        if consistent_days >= 5:
            achievements.append({
                'type': 'consistency',
                'badge': 'Consistency King',
                'message': f'{consistent_days} days of 8K+ steps this week!',
                'icon': '📈',
                'points': 90
            })

        return achievements

    @staticmethod
    def _calculate_wellness_score(metrics: Dict, trends: Dict) -> Dict:
        """Calculate comprehensive wellness score."""
        try:
            score = 0
            max_score = 100
            breakdown = {}

            # Steps score (25 points)
            steps = metrics.get('steps', 0)
            if steps >= 12000:
                steps_score = 25
            elif steps >= 10000:
                steps_score = 22
            elif steps >= 8000:
                steps_score = 18
            elif steps >= 5000:
                steps_score = 12
            else:
                steps_score = max(0, steps / 5000 * 12)

            score += steps_score
            breakdown['steps'] = round(steps_score)

            # Sleep score (25 points)
            sleep_hours = metrics.get('sleep_hours', 0)
            if sleep_hours > 0:
                if 7 <= sleep_hours <= 9:
                    sleep_score = 25
                elif 6 <= sleep_hours < 7 or 9 < sleep_hours <= 10:
                    sleep_score = 18
                elif 5 <= sleep_hours < 6 or 10 < sleep_hours <= 11:
                    sleep_score = 10
                else:
                    sleep_score = 5
            else:
                sleep_score = 0

            score += sleep_score
            breakdown['sleep'] = round(sleep_score)

            # Activity score (20 points)
            calories_burned = metrics.get('calories_burned', 0)
            if calories_burned >= 600:
                activity_score = 20
            elif calories_burned >= 400:
                activity_score = 16
            elif calories_burned >= 250:
                activity_score = 12
            else:
                activity_score = max(0, calories_burned / 250 * 12)

            score += activity_score
            breakdown['activity'] = round(activity_score)

            # Consistency score (15 points)
            consistent_days = trends.get('consistent_days', 0)
            consistency_score = min(15, (consistent_days / 7) * 15)
            score += consistency_score
            breakdown['consistency'] = round(consistency_score)

            # Heart health score (15 points)
            heart_rate = metrics.get('heart_rate_avg', 0)
            if heart_rate > 0:
                if 60 <= heart_rate <= 80:
                    heart_score = 15
                elif 50 <= heart_rate < 60 or 80 < heart_rate <= 90:
                    heart_score = 12
                elif 90 < heart_rate <= 100:
                    heart_score = 8
                else:
                    heart_score = 5
            else:
                heart_score = 10  # Neutral if no data

            score += heart_score
            breakdown['heart_health'] = round(heart_score)

            # Determine grade and recommendations
            percentage = (score / max_score) * 100

            if percentage >= 85:
                grade = 'Excellent'
                grade_message = 'Outstanding wellness! You\'re crushing your health goals! 🌟'
            elif percentage >= 70:
                grade = 'Good'
                grade_message = 'Great job! You\'re on the right track to optimal health! 💪'
            elif percentage >= 55:
                grade = 'Fair'
                grade_message = 'Good progress! A few improvements can boost your wellness significantly! 📈'
            else:
                grade = 'Needs Improvement'
                grade_message = 'Let\'s work together to improve your health! Small steps lead to big changes! 🎯'

            return {
                'score': round(score),
                'max_score': max_score,
                'percentage': round(percentage),
                'grade': grade,
                'grade_message': grade_message,
                'breakdown': breakdown,
                'improvement_areas': HealthAIEngine._identify_improvement_areas(breakdown)
            }

        except Exception as e:
            print(f"Error calculating wellness score: {str(e)}")
            return {'score': 0, 'grade': 'Error', 'breakdown': {}}

    @staticmethod
    def _identify_improvement_areas(breakdown: Dict) -> List[str]:
        """Identify areas that need improvement based on scores."""
        improvement_areas = []

        if breakdown.get('steps', 0) < 15:
            improvement_areas.append('Increase daily steps - aim for 8,000+ steps')
        if breakdown.get('sleep', 0) < 18:
            improvement_areas.append('Improve sleep quality - aim for 7-9 hours')
        if breakdown.get('activity', 0) < 12:
            improvement_areas.append('Boost physical activity - try to burn 250+ calories')
        if breakdown.get('consistency', 0) < 10:
            improvement_areas.append('Build consistency - maintain regular activity patterns')
        if breakdown.get('heart_health', 0) < 12:
            improvement_areas.append('Focus on cardiovascular health - monitor heart rate')

        return improvement_areas


# API Routes for Health AI Engine
@health_ai_bp.route('/recommendations')
@jwt_required()
def get_ai_recommendations():
    """Get AI-powered health recommendations."""
    try:
        current_user = get_jwt_identity()
        user_id = current_user.get('user_id')

        if not user_id:
            return jsonify({"msg": "User ID not found in token"}), 400

        # Get latest health data
        today = datetime.date.today()
        fitness_data = FitnessData.query.filter_by(user_id=user_id, date=today).first()

        if not fitness_data:
            return jsonify({
                "msg": "No health data available for today",
                "recommendations": {
                    'message': 'Connect your smartwatch to get personalized recommendations!'
                }
            }), 200

        # Prepare health data
        health_data = {
            'metrics': {
                'steps': fitness_data.steps or 0,
                'calories_burned': fitness_data.calories_burned or 0,
                'heart_rate_avg': fitness_data.heart_rate or 0,
                'sleep_hours': fitness_data.sleep_hours or 0,
                'weight_kg': fitness_data.weight_kg or 0,
                'distance_km': fitness_data.distance_km or 0,
                'active_minutes': fitness_data.active_minutes or 0,
                'bmi': fitness_data.bmi or 0
            }
        }

        # Generate AI recommendations
        recommendations = HealthAIEngine.generate_personalized_recommendations(user_id, health_data)

        return jsonify({
            "success": True,
            "timestamp": datetime.datetime.now().isoformat(),
            "recommendations": recommendations,
            "health_data": health_data
        }), 200

    except Exception as e:
        print(f"Error getting AI recommendations: {str(e)}")
        return jsonify({"msg": f"An error occurred: {str(e)}"}), 500


@health_ai_bp.route('/wellness-score')
@jwt_required()
def get_wellness_score():
    """Get current wellness score and analysis."""
    try:
        current_user = get_jwt_identity()
        user_id = current_user.get('user_id')

        if not user_id:
            return jsonify({"msg": "User ID not found in token"}), 400

        # Get current health data
        today = datetime.date.today()
        fitness_data = FitnessData.query.filter_by(user_id=user_id, date=today).first()

        if not fitness_data:
            return jsonify({
                "msg": "No health data available",
                "wellness_score": {"score": 0, "grade": "No Data"}
            }), 200

        # Prepare metrics
        metrics = {
            'steps': fitness_data.steps or 0,
            'calories_burned': fitness_data.calories_burned or 0,
            'heart_rate_avg': fitness_data.heart_rate or 0,
            'sleep_hours': fitness_data.sleep_hours or 0
        }

        # Get trends
        trends = HealthAIEngine._get_historical_trends(user_id)

        # Calculate wellness score
        wellness_score = HealthAIEngine._calculate_wellness_score(metrics, trends)

        return jsonify({
            "success": True,
            "wellness_score": wellness_score,
            "metrics": metrics,
            "trends": trends
        }), 200

    except Exception as e:
        print(f"Error getting wellness score: {str(e)}")
        return jsonify({"msg": f"An error occurred: {str(e)}"}), 500
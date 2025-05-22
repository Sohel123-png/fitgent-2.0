"""
Chatbot API Module
This module provides API endpoints for the AI fitness and diet chatbot.
"""

from flask import Blueprint, request, jsonify, render_template, session
from flask_jwt_extended import jwt_required, get_jwt_identity
from db import db, User, ChatMessage, HealthStat
import datetime
import os
import re

chatbot_bp = Blueprint('chatbot', __name__)

# Constants for the chatbot
# Using a rule-based approach instead of OpenAI API

# System prompts for different categories
SYSTEM_PROMPTS = {
    "fitness": """You are FitBot, an AI fitness assistant for the FitGen platform.
Your purpose is to provide accurate, helpful, and motivating fitness advice.
You can suggest workouts, explain exercise techniques, and help users stay on track with their fitness goals.
Only answer questions related to fitness, exercise, physical activity, and workout routines.
If asked about topics outside of fitness, politely redirect the conversation back to fitness topics.
Keep responses concise (under 150 words) unless detailed explanations are requested.
Use an encouraging and motivational tone.
Base your advice on scientific evidence and best practices in fitness.
When suggesting workouts, consider the user's fitness level, goals, and any limitations they mention.
Do not provide medical advice or diagnose conditions - suggest consulting healthcare professionals when appropriate.""",

    "diet": """You are NutriBot, an AI nutrition assistant for the FitGen platform.
Your purpose is to provide accurate, helpful, and practical dietary advice.
You can suggest meal plans, explain nutrition concepts, and help users make healthier food choices.
Only answer questions related to nutrition, diet, food, meal planning, and eating habits.
If asked about topics outside of nutrition, politely redirect the conversation back to diet topics.
Keep responses concise (under 150 words) unless detailed explanations are requested.
Use an encouraging and supportive tone.
Base your advice on scientific evidence and best practices in nutrition.
When suggesting meal plans, consider the user's dietary preferences, goals, and any restrictions they mention.
Do not provide medical advice or diagnose conditions - suggest consulting healthcare professionals when appropriate.""",

    "wellness": """You are WellBot, an AI mental wellness assistant for the FitGen platform.
Your purpose is to provide supportive, helpful, and evidence-based mental wellness advice.
You can suggest stress management techniques, mindfulness practices, and help users improve their mental wellbeing.
Only answer questions related to mental wellness, stress management, sleep, mindfulness, and mental health habits.
If asked about topics outside of mental wellness, politely redirect the conversation back to wellness topics.
Keep responses concise (under 150 words) unless detailed explanations are requested.
Use a calm, supportive, and empathetic tone.
Base your advice on scientific evidence and best practices in mental wellness.
When suggesting techniques, consider the user's current state, goals, and any limitations they mention.
Do not provide medical advice, therapy, or diagnose conditions - suggest consulting mental health professionals when appropriate.""",

    "progress": """You are TrackBot, an AI progress tracking assistant for the FitGen platform.
Your purpose is to help users track and analyze their fitness, nutrition, and wellness progress.
You can help users log their activities, interpret their progress data, and provide insights to help them reach their goals.
Only answer questions related to progress tracking, goal setting, and analyzing fitness/nutrition data.
If asked about topics outside of progress tracking, politely redirect the conversation back to tracking topics.
Keep responses concise (under 150 words) unless detailed explanations are requested.
Use an analytical yet encouraging tone.
Base your advice on data analysis best practices and goal-setting frameworks.
When analyzing progress, look for patterns, celebrate improvements, and suggest adjustments when needed.
Do not provide medical advice or diagnose conditions - suggest consulting healthcare professionals when appropriate."""
}

@chatbot_bp.route('/chatbot')
def chatbot_page():
    """Render the chatbot page."""
    return render_template('chatbot.html')

@chatbot_bp.route('/api/chatbot/message', methods=['POST'])
@jwt_required()
def send_message():
    """Send a message to the chatbot and get a response."""
    try:
        # Get the current user
        current_user_identity = get_jwt_identity()
        user = User.query.filter_by(email=current_user_identity['email']).first()

        if not user:
            return jsonify({"error": "User not found"}), 404

        # Get request data
        data = request.get_json()

        if 'message' not in data:
            return jsonify({"error": "Message is required"}), 400

        user_message = data['message']
        category = data.get('category', 'fitness')  # Default to fitness if not specified

        # Validate category
        if category not in SYSTEM_PROMPTS:
            return jsonify({"error": f"Invalid category. Choose from: {', '.join(SYSTEM_PROMPTS.keys())}"}), 400

        # Get conversation history
        conversation_history = get_conversation_history(user.id, category, limit=10)

        # Generate response from AI
        ai_response = generate_ai_response(user_message, conversation_history, category, user)

        # Save the user message and AI response to the database
        save_message(user.id, "user", user_message, category)
        save_message(user.id, "assistant", ai_response, category)

        return jsonify({
            "response": ai_response,
            "category": category
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@chatbot_bp.route('/api/chatbot/history', methods=['GET'])
@jwt_required()
def get_history():
    """Get the chat history for the current user."""
    try:
        # Get the current user
        current_user_identity = get_jwt_identity()
        user = User.query.filter_by(email=current_user_identity['email']).first()

        if not user:
            return jsonify({"error": "User not found"}), 404

        # Get query parameters
        category = request.args.get('category', 'fitness')  # Default to fitness if not specified
        limit = request.args.get('limit', 50, type=int)

        # Validate category
        if category not in SYSTEM_PROMPTS and category != 'all':
            return jsonify({"error": f"Invalid category. Choose from: {', '.join(SYSTEM_PROMPTS.keys())} or 'all'"}), 400

        # Get conversation history
        if category == 'all':
            messages = ChatMessage.query.filter_by(user_id=user.id).order_by(ChatMessage.timestamp.asc()).limit(limit).all()
        else:
            messages = ChatMessage.query.filter_by(user_id=user.id, category=category).order_by(ChatMessage.timestamp.asc()).limit(limit).all()

        # Format messages
        formatted_messages = []
        for message in messages:
            formatted_messages.append({
                "id": message.id,
                "role": message.role,
                "content": message.content,
                "category": message.category,
                "timestamp": message.timestamp.isoformat()
            })

        return jsonify({
            "messages": formatted_messages,
            "category": category
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@chatbot_bp.route('/api/chatbot/clear-history', methods=['POST'])
@jwt_required()
def clear_history():
    """Clear the chat history for the current user."""
    try:
        # Get the current user
        current_user_identity = get_jwt_identity()
        user = User.query.filter_by(email=current_user_identity['email']).first()

        if not user:
            return jsonify({"error": "User not found"}), 404

        # Get request data
        data = request.get_json()
        category = data.get('category', 'all')  # Default to all if not specified

        # Delete messages
        if category == 'all':
            ChatMessage.query.filter_by(user_id=user.id).delete()
        else:
            # Validate category
            if category not in SYSTEM_PROMPTS:
                return jsonify({"error": f"Invalid category. Choose from: {', '.join(SYSTEM_PROMPTS.keys())}"}), 400

            ChatMessage.query.filter_by(user_id=user.id, category=category).delete()

        db.session.commit()

        return jsonify({
            "message": f"Chat history for category '{category}' cleared successfully"
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

def get_conversation_history(user_id, category, limit=10):
    """Get the conversation history for a user in a specific category."""
    messages = ChatMessage.query.filter_by(user_id=user_id, category=category).order_by(ChatMessage.timestamp.desc()).limit(limit).all()
    messages.reverse()  # Reverse to get chronological order

    # Format messages for the AI
    formatted_messages = []
    for message in messages:
        formatted_messages.append({
            "role": message.role,
            "content": message.content
        })

    return formatted_messages

def save_message(user_id, role, content, category):
    """Save a message to the database."""
    message = ChatMessage(
        user_id=user_id,
        role=role,
        content=content,
        category=category,
        timestamp=datetime.datetime.now()
    )

    db.session.add(message)
    db.session.commit()

    return message

def generate_ai_response(user_message, conversation_history, category, user):
    """Generate a response from the AI model."""
    # Check if the message is a progress tracking command
    progress_data = extract_progress_data(user_message)
    if progress_data and category == 'progress':
        # Save the progress data
        save_progress_data(user, progress_data)
        return generate_progress_response(progress_data, user)

    # Since we don't have an OpenAI API key, we'll use a rule-based approach
    # with predefined responses for common questions in each category

    # Convert user message to lowercase for easier matching
    user_message_lower = user_message.lower()

    # Get user profile information for more personalized responses
    user_name = user.name if user and user.name else "there"
    user_weight = user.weight_kg if user and user.weight_kg else None
    user_height = user.height_cm if user and user.height_cm else None
    user_gender = user.gender if user and user.gender else None
    user_age = user.age if user and user.age else None
    user_activity = user.activity_level if user and user.activity_level else "moderate"
    user_diet_goal = user.diet_goal if user and user.diet_goal else "maintain"
    user_diet_type = user.diet_type if user and user.diet_type else "balanced"

    # Common responses for all categories
    if "hello" in user_message_lower or "hi" in user_message_lower or "hey" in user_message_lower:
        return f"Hello {user_name}! How can I help you with your {category} goals today?"

    if "thank" in user_message_lower:
        return f"You're welcome! I'm here to help with all your {category} needs. Is there anything else you'd like to know?"

    if "bye" in user_message_lower or "goodbye" in user_message_lower:
        return f"Goodbye! Remember to stay consistent with your {category} routine. Come back anytime you need advice!"

    # Category-specific responses
    if category == "fitness":
        if "beginner" in user_message_lower and ("workout" in user_message_lower or "routine" in user_message_lower):
            return """Here's a beginner workout routine you can try:

1. **Monday**: Full Body
   - Bodyweight squats: 3 sets of 12
   - Push-ups (or knee push-ups): 3 sets of 10
   - Walking lunges: 3 sets of 10 per leg
   - Plank: 3 sets, hold for 30 seconds

2. **Wednesday**: Cardio
   - 30 minutes of brisk walking or light jogging
   - 10 minutes of jumping jacks and high knees (alternate 30 seconds each)

3. **Friday**: Full Body
   - Glute bridges: 3 sets of 15
   - Dumbbell rows (or doorway rows): 3 sets of 12
   - Bicycle crunches: 3 sets of 20
   - Wall sit: 3 sets, hold for 30 seconds

Start with this for 2-3 weeks, then gradually increase intensity. Remember to warm up before and stretch after each workout!"""

        if "lose weight" in user_message_lower and "workout" in user_message_lower:
            return """For weight loss, combine these workouts with a calorie deficit diet:

1. **HIIT Workout** (3x per week):
   - 30 seconds jumping jacks
   - 30 seconds mountain climbers
   - 30 seconds burpees
   - 30 seconds high knees
   - 30 seconds rest
   - Repeat 5 times

2. **Strength Training** (2x per week):
   - Squats: 3 sets of 15
   - Push-ups: 3 sets of 10-15
   - Lunges: 3 sets of 12 per leg
   - Dumbbell rows: 3 sets of 12
   - Plank: 3 sets of 45 seconds

3. **Low-Intensity Cardio** (1-2x per week):
   - 45-60 minutes of brisk walking, swimming, or cycling

Remember, consistency is key for weight loss. Aim to be active most days of the week!"""

        if "build muscle" in user_message_lower:
            return """To build muscle, focus on progressive overload and adequate protein intake:

**4-Day Split Routine:**

1. **Day 1: Chest & Triceps**
   - Bench press: 4 sets of 8-10 reps
   - Incline dumbbell press: 3 sets of 10-12 reps
   - Chest flies: 3 sets of 12-15 reps
   - Tricep dips: 3 sets of 10-12 reps
   - Tricep pushdowns: 3 sets of 12-15 reps

2. **Day 2: Back & Biceps**
   - Pull-ups or lat pulldowns: 4 sets of 8-10 reps
   - Bent-over rows: 3 sets of 10-12 reps
   - Seated cable rows: 3 sets of 12 reps
   - Bicep curls: 3 sets of 10-12 reps
   - Hammer curls: 3 sets of 12-15 reps

3. **Day 3: Rest or Light Cardio**

4. **Day 4: Legs & Shoulders**
   - Squats: 4 sets of 8-10 reps
   - Leg press: 3 sets of 10-12 reps
   - Romanian deadlifts: 3 sets of 10-12 reps
   - Shoulder press: 3 sets of 10-12 reps
   - Lateral raises: 3 sets of 12-15 reps

5. **Day 5: Core & Arms**
   - Weighted crunches: 3 sets of 15-20 reps
   - Russian twists: 3 sets of 20 reps
   - Plank: 3 sets of 45-60 seconds
   - Skull crushers: 3 sets of 12 reps
   - Concentration curls: 3 sets of 12 reps

Ensure you're eating in a slight caloric surplus with 1.6-2g of protein per kg of bodyweight!"""

        if "how many" in user_message_lower and "calories" in user_message_lower and "burn" in user_message_lower:
            # Calculate estimated calories burned based on user profile
            if user_weight and user_height and user_gender and user_age:
                # Basic calculation for demonstration purposes
                if user_gender.lower() == "male":
                    bmr = 10 * user_weight + 6.25 * user_height - 5 * user_age + 5
                else:
                    bmr = 10 * user_weight + 6.25 * user_height - 5 * user_age - 161

                activity_multipliers = {
                    "sedentary": 1.2,
                    "light": 1.375,
                    "moderate": 1.55,
                    "active": 1.725,
                    "very_active": 1.9
                }

                multiplier = activity_multipliers.get(user_activity, 1.55)
                daily_calories = int(bmr * multiplier)

                return f"Based on your profile (weight: {user_weight}kg, height: {user_height}cm, age: {user_age}, gender: {user_gender}, activity level: {user_activity}), you burn approximately {daily_calories} calories per day. To lose weight, aim for a deficit of 500 calories per day through diet and exercise."
            else:
                return "The number of calories you burn depends on your weight, height, age, gender, and activity level. A moderately active adult typically burns between 1,800 and 2,400 calories per day. For a personalized estimate, please update your profile with your weight, height, age, and gender."

    elif category == "diet":
        if "meal plan" in user_message_lower or "diet plan" in user_message_lower:
            if user_diet_goal == "lose":
                calorie_target = "lower-calorie"
                focus = "weight loss"
            elif user_diet_goal == "gain":
                calorie_target = "higher-calorie"
                focus = "muscle gain"
            else:
                calorie_target = "balanced"
                focus = "maintenance"

            diet_type_desc = user_diet_type.capitalize()

            return f"""Here's a sample {diet_type_desc} meal plan for {focus}:

**Breakfast:**
- Overnight oats with berries and nuts
- Greek yogurt with honey
- Green tea or black coffee

**Mid-morning Snack:**
- Apple with 1 tablespoon almond butter
- Small handful of mixed nuts

**Lunch:**
- Grilled chicken or tofu salad with mixed greens
- Quinoa or brown rice (½ cup)
- Olive oil and lemon dressing
- Water with lemon

**Afternoon Snack:**
- Protein smoothie with banana and spinach
- Carrot sticks with hummus

**Dinner:**
- Baked salmon or lentils
- Roasted vegetables (broccoli, bell peppers, zucchini)
- Sweet potato (medium)
- Herbal tea

This is a {calorie_target} plan that follows {diet_type_desc} principles. Adjust portion sizes based on your specific calorie needs and preferences."""

        if "protein" in user_message_lower and ("how much" in user_message_lower or "how many" in user_message_lower):
            if user_weight:
                if user_diet_goal == "gain":
                    protein_g = round(user_weight * 1.8)
                    return f"For muscle building, you should aim for approximately {protein_g}g of protein daily (about 1.8g per kg of body weight). With your weight of {user_weight}kg, this is your target. Spread your protein intake throughout the day for optimal muscle protein synthesis."
                else:
                    protein_g = round(user_weight * 1.4)
                    return f"Based on your weight of {user_weight}kg, you should aim for approximately {protein_g}g of protein daily (about 1.4g per kg of body weight). This will help maintain muscle mass while supporting your overall health."
            else:
                return "The recommended protein intake is typically 1.2-2.0g per kg of body weight, depending on your goals. For general health, aim for at least 0.8g/kg. For muscle building, aim for 1.6-2.0g/kg. For weight loss while preserving muscle, aim for 1.4-1.8g/kg. Update your profile with your weight for a more personalized recommendation."

        if "breakfast" in user_message_lower and ("idea" in user_message_lower or "suggestion" in user_message_lower):
            return """Here are some healthy breakfast ideas:

1. **Greek Yogurt Parfait**
   - Greek yogurt, mixed berries, granola, and a drizzle of honey

2. **Avocado Toast**
   - Whole grain toast, mashed avocado, poached egg, and a sprinkle of red pepper flakes

3. **Protein Smoothie**
   - Blend protein powder, banana, spinach, almond milk, and a tablespoon of nut butter

4. **Overnight Oats**
   - Oats soaked in milk or yogurt with chia seeds, cinnamon, and topped with fruit and nuts

5. **Veggie Omelette**
   - Eggs with spinach, bell peppers, onions, and a small amount of cheese

6. **Breakfast Burrito**
   - Whole grain wrap with scrambled eggs, black beans, salsa, and avocado

Choose options that align with your dietary preferences and goals!"""

    elif category == "wellness":
        if "stress" in user_message_lower and ("reduce" in user_message_lower or "manage" in user_message_lower):
            return """Here are effective stress management techniques:

1. **Deep Breathing**
   - Practice 4-7-8 breathing: Inhale for 4 seconds, hold for 7, exhale for 8
   - Do this for 5 minutes whenever you feel stressed

2. **Progressive Muscle Relaxation**
   - Tense and then release each muscle group from toes to head
   - This helps identify and release physical tension

3. **Mindfulness Meditation**
   - Start with just 5 minutes daily
   - Focus on your breath and gently return attention when your mind wanders

4. **Physical Activity**
   - Even a 10-minute walk can reduce stress hormones
   - Find movement you enjoy rather than forcing yourself to exercise

5. **Nature Time**
   - Spend 20 minutes outdoors daily
   - "Forest bathing" has been shown to lower cortisol levels

6. **Digital Detox**
   - Set boundaries for technology use
   - Try a 1-hour phone-free period before bed

Remember, stress management is personal - experiment to find what works best for you!"""

        if "sleep" in user_message_lower and ("better" in user_message_lower or "improve" in user_message_lower):
            return """To improve your sleep quality:

1. **Consistent Schedule**
   - Go to bed and wake up at the same time daily, even on weekends
   - This regulates your body's internal clock

2. **Bedtime Routine**
   - Create a 30-minute wind-down ritual
   - Try reading, gentle stretching, or meditation

3. **Optimize Your Environment**
   - Keep your bedroom cool (65-68°F/18-20°C)
   - Ensure it's dark and quiet (use blackout curtains and white noise if needed)
   - Invest in a comfortable mattress and pillows

4. **Limit Screen Time**
   - Avoid screens 1 hour before bed (blue light blocks melatonin)
   - Use night mode on devices if you must use them

5. **Watch What You Consume**
   - Avoid caffeine after 2pm
   - Limit alcohol (it disrupts REM sleep)
   - Don't eat heavy meals within 3 hours of bedtime

6. **Daytime Habits**
   - Get natural sunlight exposure during the day
   - Exercise regularly, but not too close to bedtime
   - Limit naps to 20 minutes early in the day

If sleep problems persist for more than a month, consider consulting a healthcare provider."""

        if "meditat" in user_message_lower and ("how" in user_message_lower or "beginner" in user_message_lower):
            return """**Beginner's Guide to Meditation:**

1. **Start Small**
   - Begin with just 5 minutes daily
   - Gradually increase to 15-20 minutes as you become comfortable

2. **Find a Quiet Space**
   - Choose a spot with minimal distractions
   - You don't need a special setup - just a comfortable place to sit

3. **Get Comfortable**
   - Sit on a chair, cushion, or mat with your back straight but not rigid
   - You can also lie down if sitting is uncomfortable (but you might fall asleep!)

4. **Basic Technique**
   - Focus on your breath - the sensation of air entering and leaving your nostrils
   - When your mind wanders (it will!), gently bring attention back to your breath
   - No need to clear your mind completely - just practice returning to your focus

5. **Try Guided Meditation**
   - Apps like Headspace, Calm, or Insight Timer offer free guided sessions
   - These are helpful for beginners who benefit from instructions

6. **Be Consistent**
   - Meditate at the same time each day to build a habit
   - Morning works well for many people before the day gets busy

7. **Be Kind to Yourself**
   - Don't judge yourself when your mind wanders
   - Each time you notice and return focus is a success, not a failure

Remember, meditation is a practice - benefits come with consistency rather than perfection."""

    elif category == "progress":
        if "track" in user_message_lower and ("progress" in user_message_lower or "fitness" in user_message_lower):
            return """Here's how to effectively track your fitness progress:

1. **Body Measurements**
   - Weight: Weigh yourself at the same time of day (morning is best)
   - Measurements: Track waist, hips, chest, arms, and thighs monthly
   - Body fat percentage: Consider using calipers or a smart scale

2. **Performance Metrics**
   - Strength: Record weights, sets, and reps for key exercises
   - Endurance: Track distance, time, or pace for cardio activities
   - Flexibility: Note how far you can stretch in specific positions

3. **Daily Habits**
   - Steps: Aim for 7,000-10,000 steps daily
   - Water intake: Track ounces or glasses consumed
   - Sleep: Record hours and quality

4. **Photo Documentation**
   - Take progress photos monthly in the same lighting, poses, and clothing
   - These can reveal changes that numbers don't show

5. **Subjective Measures**
   - Energy levels: Rate on a scale of 1-10
   - Mood: Note how exercise affects your mental state
   - Recovery: Track soreness and recovery time

6. **Digital Tools**
   - Use our chat feature to log data (e.g., "Weight: 75kg" or "Ran 5km in 30 minutes")
   - Connect fitness trackers or apps for automated tracking

Remember to track consistently but don't become obsessive. The goal is to gather useful data to guide your journey, not to create another source of stress."""

        if "goal" in user_message_lower and ("set" in user_message_lower or "setting" in user_message_lower):
            return """**SMART Goal Setting for Fitness Success:**

1. **Specific**
   - Instead of "get fit," try "be able to run 5km without stopping"
   - Define exactly what you want to accomplish

2. **Measurable**
   - Include metrics to track progress
   - Example: "Increase squat weight from 50kg to 70kg"

3. **Achievable**
   - Set challenging but realistic goals based on your starting point
   - Consider your schedule, resources, and current fitness level

4. **Relevant**
   - Choose goals that align with your values and long-term vision
   - Ask: "Why does this matter to me personally?"

5. **Time-bound**
   - Set a deadline to create urgency
   - Example: "Complete a pull-up by December 31st"

**Types of Goals to Consider:**
- **Process goals:** Daily actions (exercise 4x/week)
- **Performance goals:** Specific achievements (run 5km in under 30 minutes)
- **Outcome goals:** End results (lose 5kg of fat)

**Pro Tips:**
- Write your goals down and review them regularly
- Share goals with someone for accountability
- Break big goals into smaller milestones
- Celebrate progress along the way
- Adjust goals as needed - flexibility is key

Would you like help setting a specific SMART goal based on your current situation?"""

    # Default response if no specific match is found
    return f"Thank you for your question about {category}. I'm currently operating in offline mode with limited responses. Could you try asking something more specific about {category} routines, best practices, or recommendations? I have information about common topics in this area."

def extract_progress_data(message):
    """Extract progress data from a user message."""
    # Check for common progress tracking patterns
    weight_match = re.search(r'weight[:\s]+(\d+\.?\d*)\s*(?:kg|kilograms?|pounds?|lbs?)', message, re.IGNORECASE)
    steps_match = re.search(r'steps[:\s]+(\d+)', message, re.IGNORECASE)
    calories_match = re.search(r'calories[:\s]+(\d+)', message, re.IGNORECASE)
    workout_match = re.search(r'workout[:\s]+(.*?)(?:for|duration|time|minutes|hours|$)', message, re.IGNORECASE)
    sleep_match = re.search(r'sleep[:\s]+(\d+\.?\d*)\s*(?:hours?|hrs?)', message, re.IGNORECASE)

    progress_data = {}

    if weight_match:
        progress_data['weight'] = float(weight_match.group(1))

    if steps_match:
        progress_data['steps'] = int(steps_match.group(1))

    if calories_match:
        progress_data['calories'] = int(calories_match.group(1))

    if workout_match:
        progress_data['workout'] = workout_match.group(1).strip()

    if sleep_match:
        progress_data['sleep'] = float(sleep_match.group(1))

    return progress_data if progress_data else None

def save_progress_data(user, progress_data):
    """Save progress data to the user's health stats."""
    # Check if there's a health stat for today
    today = datetime.datetime.now().date()
    health_stat = user.health_stats.filter_by(date=today).first()

    if not health_stat:
        # Create a new health stat for today
        health_stat = HealthStat(
            user_id=user.id,
            date=today
        )
        db.session.add(health_stat)

    # Update the health stat with the progress data
    if 'weight' in progress_data:
        health_stat.weight_kg = progress_data['weight']

    if 'steps' in progress_data:
        health_stat.steps = progress_data['steps']

    if 'calories' in progress_data:
        health_stat.calories_consumed = progress_data['calories']

    if 'sleep' in progress_data:
        health_stat.sleep_hours = progress_data['sleep']

    if 'workout' in progress_data:
        # Append to notes
        if health_stat.notes:
            health_stat.notes += f"\nWorkout: {progress_data['workout']}"
        else:
            health_stat.notes = f"Workout: {progress_data['workout']}"

    db.session.commit()

def generate_progress_response(progress_data, user):
    """Generate a response for progress tracking."""
    response_parts = ["I've recorded your progress:"]

    if 'weight' in progress_data:
        response_parts.append(f"✓ Weight: {progress_data['weight']} kg")

    if 'steps' in progress_data:
        response_parts.append(f"✓ Steps: {progress_data['steps']}")

    if 'calories' in progress_data:
        response_parts.append(f"✓ Calories: {progress_data['calories']}")

    if 'workout' in progress_data:
        response_parts.append(f"✓ Workout: {progress_data['workout']}")

    if 'sleep' in progress_data:
        response_parts.append(f"✓ Sleep: {progress_data['sleep']} hours")

    # Add some analysis if we have historical data
    today = datetime.datetime.now().date()
    yesterday = today - datetime.timedelta(days=1)
    yesterday_stat = user.health_stats.filter_by(date=yesterday).first()

    if yesterday_stat:
        if 'weight' in progress_data and yesterday_stat.weight_kg:
            weight_diff = progress_data['weight'] - yesterday_stat.weight_kg
            if abs(weight_diff) > 0.1:
                if weight_diff > 0:
                    response_parts.append(f"Your weight increased by {weight_diff:.1f} kg since yesterday.")
                else:
                    response_parts.append(f"Your weight decreased by {abs(weight_diff):.1f} kg since yesterday.")

        if 'steps' in progress_data and yesterday_stat.steps:
            steps_diff = progress_data['steps'] - yesterday_stat.steps
            if steps_diff > 1000:
                response_parts.append(f"Great job! You've taken {steps_diff} more steps than yesterday.")
            elif steps_diff < -1000:
                response_parts.append(f"You've taken {abs(steps_diff)} fewer steps than yesterday. Try to stay active!")

    response_parts.append("\nIs there anything specific about your progress you'd like to know?")

    return "\n".join(response_parts)

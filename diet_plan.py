"""
Diet Plan Generator Module
This module provides functionality to generate personalized diet plans based on user preferences and goals.
"""

import random
import json
import os
from datetime import datetime, timedelta

# Food database - In a real application, this would be stored in a database
FOOD_DATABASE = {
    "breakfast": [
        {
            "name": "Scrambled Eggs with Whole Grain Toast",
            "ingredients": ["2 eggs", "2 slices whole grain bread", "1 tsp olive oil", "Salt and pepper to taste"],
            "calories": 350,
            "protein": 20,
            "carbs": 30,
            "fat": 15,
            "preparation": "Whisk eggs, cook in olive oil, serve with toast.",
            "diet_types": ["balanced", "high_protein", "low_carb"],
            "image": "scrambled_eggs.jpg",
            "budget_friendly": True,
            "price_range": "30-50"
        },
        {
            "name": "Greek Yogurt with Berries and Honey",
            "ingredients": ["1 cup Greek yogurt", "1/2 cup mixed berries", "1 tbsp honey", "1 tbsp chia seeds"],
            "calories": 300,
            "protein": 18,
            "carbs": 35,
            "fat": 8,
            "preparation": "Mix yogurt with berries, drizzle with honey, sprinkle chia seeds.",
            "diet_types": ["balanced", "vegetarian", "high_protein"],
            "image": "greek_yogurt.jpg"
        },
        {
            "name": "Avocado Toast with Poached Egg",
            "ingredients": ["1 slice whole grain bread", "1/2 avocado", "1 egg", "Red pepper flakes", "Salt to taste"],
            "calories": 320,
            "protein": 15,
            "carbs": 25,
            "fat": 18,
            "preparation": "Toast bread, spread mashed avocado, top with poached egg.",
            "diet_types": ["balanced", "vegetarian", "high_protein"],
            "image": "avocado_toast.jpg"
        },
        {
            "name": "Oatmeal with Banana and Almond Butter",
            "ingredients": ["1/2 cup rolled oats", "1 cup almond milk", "1 banana", "1 tbsp almond butter", "1 tsp cinnamon"],
            "calories": 380,
            "protein": 12,
            "carbs": 60,
            "fat": 10,
            "preparation": "Cook oats with almond milk, top with sliced banana and almond butter.",
            "diet_types": ["balanced", "vegetarian", "vegan", "high_carb"],
            "image": "oatmeal.jpg",
            "budget_friendly": True,
            "price_range": "30-50"
        },
        {
            "name": "Protein Smoothie Bowl",
            "ingredients": ["1 scoop protein powder", "1 banana", "1/2 cup berries", "1 cup almond milk", "1 tbsp granola"],
            "calories": 340,
            "protein": 25,
            "carbs": 45,
            "fat": 5,
            "preparation": "Blend protein powder, banana, berries, and milk. Top with granola.",
            "diet_types": ["balanced", "vegetarian", "high_protein", "high_carb"],
            "image": "smoothie_bowl.jpg"
        }
    ],
    "lunch": [
        {
            "name": "Grilled Chicken Salad",
            "ingredients": ["4 oz grilled chicken breast", "2 cups mixed greens", "1/4 cup cherry tomatoes", "1/4 cucumber", "2 tbsp olive oil dressing"],
            "calories": 350,
            "protein": 30,
            "carbs": 10,
            "fat": 20,
            "preparation": "Grill chicken, mix with greens and vegetables, dress with olive oil.",
            "diet_types": ["balanced", "high_protein", "low_carb"],
            "image": "chicken_salad.jpg"
        },
        {
            "name": "Quinoa Bowl with Roasted Vegetables",
            "ingredients": ["1/2 cup quinoa", "1 cup roasted vegetables", "1/4 avocado", "2 tbsp tahini dressing"],
            "calories": 400,
            "protein": 12,
            "carbs": 50,
            "fat": 18,
            "preparation": "Cook quinoa, top with roasted vegetables and avocado, drizzle with tahini.",
            "diet_types": ["balanced", "vegetarian", "vegan", "high_carb"],
            "image": "quinoa_bowl.jpg"
        },
        {
            "name": "Turkey and Avocado Wrap",
            "ingredients": ["1 whole grain wrap", "3 oz turkey slices", "1/4 avocado", "Lettuce", "Tomato", "1 tbsp hummus"],
            "calories": 380,
            "protein": 25,
            "carbs": 35,
            "fat": 15,
            "preparation": "Spread hummus on wrap, layer with turkey, avocado, lettuce, and tomato.",
            "diet_types": ["balanced", "high_protein"],
            "image": "turkey_wrap.jpg"
        },
        {
            "name": "Lentil Soup with Whole Grain Bread",
            "ingredients": ["1 cup lentil soup", "1 slice whole grain bread", "1 tsp olive oil"],
            "calories": 320,
            "protein": 15,
            "carbs": 45,
            "fat": 8,
            "preparation": "Heat soup, serve with bread drizzled with olive oil.",
            "diet_types": ["balanced", "vegetarian", "vegan", "high_carb"],
            "image": "lentil_soup.jpg",
            "budget_friendly": True,
            "price_range": "30-50"
        },
        {
            "name": "Tuna Salad Stuffed Avocado",
            "ingredients": ["1 can tuna", "1 avocado", "1 tbsp Greek yogurt", "1 tbsp lemon juice", "Diced celery", "Salt and pepper"],
            "calories": 350,
            "protein": 30,
            "carbs": 10,
            "fat": 22,
            "preparation": "Mix tuna with yogurt, lemon juice, and celery. Stuff into avocado halves.",
            "diet_types": ["high_protein", "low_carb"],
            "image": "tuna_avocado.jpg"
        }
    ],
    "dinner": [
        {
            "name": "Grilled Salmon with Roasted Vegetables",
            "ingredients": ["5 oz salmon fillet", "1 cup mixed vegetables", "1 tbsp olive oil", "Lemon juice", "Herbs"],
            "calories": 420,
            "protein": 35,
            "carbs": 15,
            "fat": 25,
            "preparation": "Grill salmon, roast vegetables with olive oil and herbs.",
            "diet_types": ["balanced", "high_protein", "low_carb"],
            "image": "grilled_salmon.jpg"
        },
        {
            "name": "Chicken Stir-Fry with Brown Rice",
            "ingredients": ["4 oz chicken breast", "1 cup mixed vegetables", "1/2 cup brown rice", "1 tbsp soy sauce", "1 tsp sesame oil"],
            "calories": 400,
            "protein": 30,
            "carbs": 40,
            "fat": 12,
            "preparation": "Stir-fry chicken and vegetables, serve over brown rice.",
            "diet_types": ["balanced", "high_protein"],
            "image": "chicken_stir_fry.jpg"
        },
        {
            "name": "Vegetable and Chickpea Curry",
            "ingredients": ["1/2 cup chickpeas", "1 cup mixed vegetables", "1/4 cup coconut milk", "1 tbsp curry paste", "1/2 cup brown rice"],
            "calories": 380,
            "protein": 12,
            "carbs": 55,
            "fat": 14,
            "preparation": "Simmer vegetables and chickpeas in coconut milk and curry paste, serve with rice.",
            "diet_types": ["balanced", "vegetarian", "vegan", "high_carb"],
            "image": "vegetable_curry.jpg",
            "budget_friendly": True,
            "price_range": "30-50"
        },
        {
            "name": "Baked Cod with Quinoa and Asparagus",
            "ingredients": ["5 oz cod fillet", "1/2 cup quinoa", "8 asparagus spears", "1 tbsp olive oil", "Lemon juice", "Herbs"],
            "calories": 350,
            "protein": 32,
            "carbs": 30,
            "fat": 10,
            "preparation": "Bake cod with lemon and herbs, serve with quinoa and steamed asparagus.",
            "diet_types": ["balanced", "high_protein"],
            "image": "baked_cod.jpg"
        },
        {
            "name": "Turkey Meatballs with Zucchini Noodles",
            "ingredients": ["4 oz ground turkey", "1 egg", "2 tbsp breadcrumbs", "2 zucchini (spiralized)", "1/2 cup tomato sauce", "Herbs"],
            "calories": 370,
            "protein": 35,
            "carbs": 15,
            "fat": 18,
            "preparation": "Form and bake meatballs, serve over zucchini noodles with tomato sauce.",
            "diet_types": ["high_protein", "low_carb"],
            "image": "turkey_meatballs.jpg"
        }
    ],
    "snacks": [
        {
            "name": "Apple with Almond Butter",
            "ingredients": ["1 apple", "1 tbsp almond butter"],
            "calories": 180,
            "protein": 4,
            "carbs": 25,
            "fat": 8,
            "preparation": "Slice apple, serve with almond butter for dipping.",
            "diet_types": ["balanced", "vegetarian", "vegan"],
            "image": "apple_almond.jpg"
        },
        {
            "name": "Greek Yogurt with Honey",
            "ingredients": ["1/2 cup Greek yogurt", "1 tsp honey", "1 tbsp walnuts"],
            "calories": 150,
            "protein": 12,
            "carbs": 10,
            "fat": 6,
            "preparation": "Top yogurt with honey and crushed walnuts.",
            "diet_types": ["balanced", "vegetarian", "high_protein"],
            "image": "yogurt_honey.jpg"
        },
        {
            "name": "Protein Shake",
            "ingredients": ["1 scoop protein powder", "1 cup almond milk", "1/2 banana", "Ice"],
            "calories": 200,
            "protein": 20,
            "carbs": 15,
            "fat": 5,
            "preparation": "Blend all ingredients until smooth.",
            "diet_types": ["balanced", "vegetarian", "high_protein"],
            "image": "protein_shake.jpg"
        },
        {
            "name": "Hummus with Vegetable Sticks",
            "ingredients": ["1/4 cup hummus", "1 cup mixed vegetable sticks (carrots, celery, bell peppers)"],
            "calories": 170,
            "protein": 6,
            "carbs": 20,
            "fat": 8,
            "preparation": "Serve hummus with vegetable sticks for dipping.",
            "diet_types": ["balanced", "vegetarian", "vegan"],
            "image": "hummus_veggies.jpg",
            "budget_friendly": True,
            "price_range": "30-50"
        },
        {
            "name": "Hard-Boiled Eggs",
            "ingredients": ["2 hard-boiled eggs", "Salt and pepper to taste"],
            "calories": 140,
            "protein": 12,
            "carbs": 0,
            "fat": 10,
            "preparation": "Boil eggs, peel and season with salt and pepper.",
            "diet_types": ["high_protein", "low_carb"],
            "image": "boiled_eggs.jpg"
        }
    ]
}

# Diet types and their macronutrient distributions
DIET_TYPES = {
    "balanced": {"protein": 0.25, "carbs": 0.5, "fat": 0.25},
    "high_protein": {"protein": 0.4, "carbs": 0.4, "fat": 0.2},
    "low_carb": {"protein": 0.35, "carbs": 0.25, "fat": 0.4},
    "high_carb": {"protein": 0.2, "carbs": 0.6, "fat": 0.2},
    "vegetarian": {"protein": 0.2, "carbs": 0.55, "fat": 0.25},
    "vegan": {"protein": 0.2, "carbs": 0.6, "fat": 0.2}
}

def save_food_database():
    """Save the food database to a JSON file."""
    with open(os.path.join(os.path.dirname(__file__), 'food_database.json'), 'w') as f:
        json.dump(FOOD_DATABASE, f, indent=4)

def load_food_database():
    """Load the food database from a JSON file."""
    try:
        with open(os.path.join(os.path.dirname(__file__), 'food_database.json'), 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # If the file doesn't exist, create it with the default database
        save_food_database()
        return FOOD_DATABASE

def calculate_daily_calories(weight_kg, height_cm, age, gender, activity_level, goal):
    """
    Calculate daily calorie needs using the Mifflin-St Jeor equation.

    Activity levels:
    - sedentary: 1.2
    - light: 1.375
    - moderate: 1.55
    - active: 1.725
    - very_active: 1.9

    Goals:
    - maintain: 0
    - lose: -500
    - gain: +500
    """
    # Convert activity level to multiplier
    activity_multipliers = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very_active": 1.9
    }

    activity_multiplier = activity_multipliers.get(activity_level, 1.2)

    # Calculate BMR (Basal Metabolic Rate)
    if gender.lower() == "male":
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161

    # Calculate TDEE (Total Daily Energy Expenditure)
    tdee = bmr * activity_multiplier

    # Adjust based on goal
    goal_adjustments = {
        "maintain": 0,
        "lose": -500,
        "gain": 500
    }

    daily_calories = tdee + goal_adjustments.get(goal, 0)

    # Ensure minimum healthy calories
    min_calories = 1200 if gender.lower() == "female" else 1500
    return max(daily_calories, min_calories)

def generate_diet_plan(user_preferences):
    """
    Generate a personalized diet plan based on user preferences.

    Args:
        user_preferences (dict): User preferences including:
            - weight_kg: User's weight in kg
            - height_cm: User's height in cm
            - age: User's age
            - gender: User's gender ('male' or 'female')
            - activity_level: User's activity level
            - goal: User's goal ('maintain', 'lose', or 'gain')
            - diet_type: User's preferred diet type
            - allergies: List of food allergies
            - num_days: Number of days to generate the plan for
            - budget_friendly: Whether to include only budget-friendly options

    Returns:
        dict: A personalized diet plan
    """
    # Load the food database
    food_db = load_food_database()

    # Extract user preferences
    weight_kg = user_preferences.get('weight_kg', 70)
    height_cm = user_preferences.get('height_cm', 170)
    age = user_preferences.get('age', 30)
    gender = user_preferences.get('gender', 'male')
    activity_level = user_preferences.get('activity_level', 'moderate')
    goal = user_preferences.get('goal', 'maintain')
    diet_type = user_preferences.get('diet_type', 'balanced')
    allergies = user_preferences.get('allergies', [])
    num_days = user_preferences.get('num_days', 7)
    budget_friendly = user_preferences.get('budget_friendly', False)

    # Calculate daily calorie needs
    daily_calories = calculate_daily_calories(weight_kg, height_cm, age, gender, activity_level, goal)

    # Get macronutrient distribution based on diet type
    macro_distribution = DIET_TYPES.get(diet_type, DIET_TYPES['balanced'])

    # Calculate macronutrient targets in grams
    protein_target = (daily_calories * macro_distribution['protein']) / 4  # 4 calories per gram of protein
    carbs_target = (daily_calories * macro_distribution['carbs']) / 4  # 4 calories per gram of carbs
    fat_target = (daily_calories * macro_distribution['fat']) / 9  # 9 calories per gram of fat

    # Filter out foods with allergens (in a real app, this would be more sophisticated)
    filtered_food_db = {}
    for meal_type, meals in food_db.items():
        filtered_food_db[meal_type] = []
        for meal in meals:
            # Check if any allergen is in the ingredients
            allergen_found = False
            for allergen in allergies:
                if any(allergen.lower() in ingredient.lower() for ingredient in meal['ingredients']):
                    allergen_found = True
                    break

            # Check if meal should be included based on diet type, allergens, and budget preference
            include_meal = (
                not allergen_found and
                diet_type in meal['diet_types'] and
                (not budget_friendly or meal.get('budget_friendly', False))
            )

            if include_meal:
                filtered_food_db[meal_type].append(meal)

    # Generate the diet plan
    diet_plan = {
        'user_info': {
            'daily_calories': round(daily_calories),
            'protein_target': round(protein_target),
            'carbs_target': round(carbs_target),
            'fat_target': round(fat_target),
            'diet_type': diet_type,
            'budget_friendly': budget_friendly
        },
        'days': []
    }

    # Generate meal plan for each day
    today = datetime.now()
    for day_num in range(num_days):
        day_date = today + timedelta(days=day_num)
        day_plan = {
            'date': day_date.strftime('%Y-%m-%d'),
            'day_of_week': day_date.strftime('%A'),
            'meals': {}
        }

        # Note: In a more sophisticated system, we would distribute calories across meals
        # based on the following percentages:
        # breakfast: 25%, lunch: 35%, dinner: 30%, snacks: 10%

        # Select meals for each meal type
        for meal_type in ['breakfast', 'lunch', 'dinner', 'snacks']:
            if filtered_food_db.get(meal_type) and len(filtered_food_db[meal_type]) > 0:
                # In a more sophisticated system, we would optimize meal selection
                # based on calorie and macronutrient targets
                selected_meal = random.choice(filtered_food_db[meal_type])
                day_plan['meals'][meal_type] = selected_meal

        # Calculate daily totals
        daily_totals = {
            'calories': sum(meal.get('calories', 0) for meal in day_plan['meals'].values()),
            'protein': sum(meal.get('protein', 0) for meal in day_plan['meals'].values()),
            'carbs': sum(meal.get('carbs', 0) for meal in day_plan['meals'].values()),
            'fat': sum(meal.get('fat', 0) for meal in day_plan['meals'].values())
        }

        day_plan['totals'] = daily_totals
        diet_plan['days'].append(day_plan)

    return diet_plan

def get_meal_suggestion(meal_type, diet_type=None, exclude_ingredients=None):
    """
    Get a meal suggestion for a specific meal type and diet type.

    Args:
        meal_type (str): Type of meal ('breakfast', 'lunch', 'dinner', 'snacks')
        diet_type (str, optional): Type of diet. Defaults to None.
        exclude_ingredients (list, optional): Ingredients to exclude. Defaults to None.

    Returns:
        dict: A meal suggestion
    """
    # Load the food database
    food_db = load_food_database()

    if meal_type not in food_db:
        return None

    meals = food_db[meal_type]

    # Filter by diet type if specified
    if diet_type:
        meals = [meal for meal in meals if diet_type in meal.get('diet_types', [])]

    # Filter out meals with excluded ingredients
    if exclude_ingredients:
        filtered_meals = []
        for meal in meals:
            exclude = False
            for ingredient in exclude_ingredients:
                if any(ingredient.lower() in meal_ingredient.lower() for meal_ingredient in meal['ingredients']):
                    exclude = True
                    break
            if not exclude:
                filtered_meals.append(meal)
        meals = filtered_meals

    # Return a random meal suggestion
    if meals:
        return random.choice(meals)

    return None

# Initialize the food database if it doesn't exist
if not os.path.exists(os.path.join(os.path.dirname(__file__), 'food_database.json')):
    save_food_database()

const { Configuration, OpenAIApi } = require('openai');
const User = require('../models/userModel');
const WorkoutLog = require('../models/workoutLogModel');
const Meal = require('../models/mealModel');
const WaterIntake = require('../models/waterIntakeModel');
const SleepLog = require('../models/sleepLogModel');
const AppError = require('../utils/appError');
const config = require('../config/config');

// Initialize OpenAI API
const configuration = new Configuration({
  apiKey: config.openaiApiKey
});
const openai = new OpenAIApi(configuration);

// Send message to AI chatbot
exports.sendMessage = async (req, res, next) => {
  try {
    const { message } = req.body;
    
    if (!message) {
      return next(new AppError('Please provide a message', 400));
    }
    
    // Get user data for context
    const user = await User.findById(req.user.id);
    
    // Get user's recent workout logs
    const recentWorkouts = await WorkoutLog.find({ user: req.user.id })
      .sort('-date')
      .limit(5);
    
    // Get user's recent meal logs
    const recentMeals = await Meal.find({ user: req.user.id })
      .sort('-date')
      .limit(5);
    
    // Get user's water intake
    const waterIntake = await WaterIntake.getDailyTotal(req.user.id, new Date());
    
    // Get user's sleep logs
    const sleepLogs = await SleepLog.find({ user: req.user.id })
      .sort('-date')
      .limit(3);
    
    // Create system message with user context
    const systemMessage = {
      role: 'system',
      content: `You are FitGent AI, a fitness and wellness assistant. You help users with workout plans, nutrition advice, and general wellness tips.
      
Current user information:
- Name: ${user.firstName} ${user.lastName}
- Age: ${user.age || 'Not specified'}
- Gender: ${user.gender || 'Not specified'}
- Height: ${user.height ? `${user.height} cm` : 'Not specified'}
- Weight: ${user.weight ? `${user.weight} kg` : 'Not specified'}
- Fitness Goal: ${user.fitnessGoal || 'Not specified'}
- Activity Level: ${user.activityLevel || 'Not specified'}

Recent Workouts: ${recentWorkouts.length > 0 
  ? recentWorkouts.map(w => `${new Date(w.date).toLocaleDateString()}: ${w.workout ? w.workout.name : 'Custom workout'} (${w.duration} minutes, ${w.caloriesBurned} calories burned)`).join(', ')
  : 'No recent workouts'}

Recent Meals: ${recentMeals.length > 0
  ? recentMeals.map(m => `${new Date(m.date).toLocaleDateString()}: ${m.type} - ${m.name} (${m.totalCalories} calories)`).join(', ')
  : 'No recent meals'}

Today's Water Intake: ${waterIntake.total || 0} ml

Recent Sleep: ${sleepLogs.length > 0
  ? sleepLogs.map(s => `${new Date(s.date).toLocaleDateString()}: ${s.duration / 60} hours (Quality: ${s.quality}/5)`).join(', ')
  : 'No recent sleep logs'}

Provide helpful, personalized advice based on this information. Be encouraging and motivational. If the user asks about specific workouts, nutrition plans, or wellness strategies, provide detailed, evidence-based information. If the user's question is outside your expertise, acknowledge your limitations and suggest consulting with a healthcare professional.`
    };
    
    // Create user message
    const userMessage = {
      role: 'user',
      content: message
    };
    
    // Call OpenAI API
    const response = await openai.createChatCompletion({
      model: 'gpt-3.5-turbo',
      messages: [systemMessage, userMessage],
      max_tokens: 500,
      temperature: 0.7
    });
    
    // Extract assistant's response
    const assistantResponse = response.data.choices[0].message.content;
    
    res.status(200).json({
      status: 'success',
      data: {
        message: assistantResponse
      }
    });
  } catch (error) {
    console.error('OpenAI API Error:', error.response?.data || error.message);
    
    // Handle OpenAI API errors
    if (error.response?.status === 429) {
      return next(new AppError('Too many requests to the AI service. Please try again later.', 429));
    }
    
    next(new AppError('Error processing your request. Please try again later.', 500));
  }
};

// Get workout recommendation
exports.getWorkoutRecommendation = async (req, res, next) => {
  try {
    const { goal, duration, equipment, difficulty } = req.body;
    
    // Get user data for context
    const user = await User.findById(req.user.id);
    
    // Create system message with user context
    const systemMessage = {
      role: 'system',
      content: `You are FitGent AI, a fitness assistant specializing in creating personalized workout plans. Generate a detailed workout plan based on the user's specifications and profile.
      
Current user information:
- Name: ${user.firstName} ${user.lastName}
- Age: ${user.age || 'Not specified'}
- Gender: ${user.gender || 'Not specified'}
- Height: ${user.height ? `${user.height} cm` : 'Not specified'}
- Weight: ${user.weight ? `${user.weight} kg` : 'Not specified'}
- Fitness Goal: ${user.fitnessGoal || 'Not specified'}
- Activity Level: ${user.activityLevel || 'Not specified'}

Format the workout plan as follows:
1. Start with a brief introduction and overview of the workout
2. List each exercise with sets, reps, and rest periods
3. Include proper form tips for key exercises
4. End with cool-down suggestions

The response should be detailed but concise, focusing on practical information the user can immediately apply.`
    };
    
    // Create user message
    const userMessage = {
      role: 'user',
      content: `Please create a workout plan with the following specifications:
- Goal: ${goal || user.fitnessGoal || 'General fitness'}
- Duration: ${duration || '30-45 minutes'}
- Available Equipment: ${equipment || 'Minimal equipment'}
- Difficulty Level: ${difficulty || 'Intermediate'}`
    };
    
    // Call OpenAI API
    const response = await openai.createChatCompletion({
      model: 'gpt-3.5-turbo',
      messages: [systemMessage, userMessage],
      max_tokens: 1000,
      temperature: 0.7
    });
    
    // Extract assistant's response
    const assistantResponse = response.data.choices[0].message.content;
    
    res.status(200).json({
      status: 'success',
      data: {
        workout: assistantResponse
      }
    });
  } catch (error) {
    console.error('OpenAI API Error:', error.response?.data || error.message);
    next(new AppError('Error generating workout recommendation. Please try again later.', 500));
  }
};

// Get meal recommendation
exports.getMealRecommendation = async (req, res, next) => {
  try {
    const { mealType, dietaryRestrictions, calories } = req.body;
    
    // Get user data for context
    const user = await User.findById(req.user.id);
    
    // Create system message with user context
    const systemMessage = {
      role: 'system',
      content: `You are FitGent AI, a nutrition assistant specializing in creating personalized meal recommendations. Generate a detailed meal recommendation based on the user's specifications and profile.
      
Current user information:
- Name: ${user.firstName} ${user.lastName}
- Age: ${user.age || 'Not specified'}
- Gender: ${user.gender || 'Not specified'}
- Height: ${user.height ? `${user.height} cm` : 'Not specified'}
- Weight: ${user.weight ? `${user.weight} kg` : 'Not specified'}
- Fitness Goal: ${user.fitnessGoal || 'Not specified'}
- Activity Level: ${user.activityLevel || 'Not specified'}

Format the meal recommendation as follows:
1. Start with a brief introduction
2. Provide a complete recipe with ingredients and quantities
3. Include cooking instructions
4. List nutritional information (calories, protein, carbs, fat)
5. Suggest variations or substitutions

The response should be detailed but concise, focusing on practical information the user can immediately apply.`
    };
    
    // Create user message
    const userMessage = {
      role: 'user',
      content: `Please create a meal recommendation with the following specifications:
- Meal Type: ${mealType || 'Any'}
- Dietary Restrictions: ${dietaryRestrictions || 'None'}
- Target Calories: ${calories || 'Appropriate for my fitness goal'}`
    };
    
    // Call OpenAI API
    const response = await openai.createChatCompletion({
      model: 'gpt-3.5-turbo',
      messages: [systemMessage, userMessage],
      max_tokens: 1000,
      temperature: 0.7
    });
    
    // Extract assistant's response
    const assistantResponse = response.data.choices[0].message.content;
    
    res.status(200).json({
      status: 'success',
      data: {
        meal: assistantResponse
      }
    });
  } catch (error) {
    console.error('OpenAI API Error:', error.response?.data || error.message);
    next(new AppError('Error generating meal recommendation. Please try again later.', 500));
  }
};

const Workout = require('../models/workoutModel');
const WorkoutLog = require('../models/workoutLogModel');
const User = require('../models/userModel');
const AppError = require('../utils/appError');
const cloudinary = require('../utils/cloudinary');

// Get all workouts
exports.getAllWorkouts = async (req, res, next) => {
  try {
    // Build query
    const queryObj = { ...req.query };
    const excludedFields = ['page', 'sort', 'limit', 'fields'];
    excludedFields.forEach(el => delete queryObj[el]);
    
    // Advanced filtering
    let queryStr = JSON.stringify(queryObj);
    queryStr = queryStr.replace(/\b(gte|gt|lte|lt)\b/g, match => `$${match}`);
    
    // Find workouts
    let query = Workout.find(JSON.parse(queryStr));
    
    // Sorting
    if (req.query.sort) {
      const sortBy = req.query.sort.split(',').join(' ');
      query = query.sort(sortBy);
    } else {
      query = query.sort('-createdAt');
    }
    
    // Field limiting
    if (req.query.fields) {
      const fields = req.query.fields.split(',').join(' ');
      query = query.select(fields);
    } else {
      query = query.select('-__v');
    }
    
    // Pagination
    const page = parseInt(req.query.page, 10) || 1;
    const limit = parseInt(req.query.limit, 10) || 10;
    const skip = (page - 1) * limit;
    
    query = query.skip(skip).limit(limit);
    
    // Execute query
    const workouts = await query;
    
    // Send response
    res.status(200).json({
      status: 'success',
      results: workouts.length,
      data: {
        workouts
      }
    });
  } catch (error) {
    next(error);
  }
};

// Get workout by ID
exports.getWorkout = async (req, res, next) => {
  try {
    const workout = await Workout.findById(req.params.id);
    
    if (!workout) {
      return next(new AppError('No workout found with that ID', 404));
    }
    
    res.status(200).json({
      status: 'success',
      data: {
        workout
      }
    });
  } catch (error) {
    next(error);
  }
};

// Create workout
exports.createWorkout = async (req, res, next) => {
  try {
    // Add creator to body
    req.body.creator = req.user.id;
    
    // Create workout
    const newWorkout = await Workout.create(req.body);
    
    res.status(201).json({
      status: 'success',
      data: {
        workout: newWorkout
      }
    });
  } catch (error) {
    next(error);
  }
};

// Update workout
exports.updateWorkout = async (req, res, next) => {
  try {
    const workout = await Workout.findById(req.params.id);
    
    if (!workout) {
      return next(new AppError('No workout found with that ID', 404));
    }
    
    // Check if user is creator or admin
    if (workout.creator.id !== req.user.id && req.user.role !== 'admin' && req.user.role !== 'trainer') {
      return next(new AppError('You do not have permission to update this workout', 403));
    }
    
    // Update workout
    const updatedWorkout = await Workout.findByIdAndUpdate(req.params.id, req.body, {
      new: true,
      runValidators: true
    });
    
    res.status(200).json({
      status: 'success',
      data: {
        workout: updatedWorkout
      }
    });
  } catch (error) {
    next(error);
  }
};

// Delete workout
exports.deleteWorkout = async (req, res, next) => {
  try {
    const workout = await Workout.findById(req.params.id);
    
    if (!workout) {
      return next(new AppError('No workout found with that ID', 404));
    }
    
    // Check if user is creator or admin
    if (workout.creator.id !== req.user.id && req.user.role !== 'admin') {
      return next(new AppError('You do not have permission to delete this workout', 403));
    }
    
    await Workout.findByIdAndDelete(req.params.id);
    
    res.status(204).json({
      status: 'success',
      data: null
    });
  } catch (error) {
    next(error);
  }
};

// Upload workout image
exports.uploadWorkoutImage = async (req, res, next) => {
  try {
    // Check if file exists
    if (!req.file) {
      return next(new AppError('Please upload an image', 400));
    }
    
    const workout = await Workout.findById(req.params.id);
    
    if (!workout) {
      return next(new AppError('No workout found with that ID', 404));
    }
    
    // Check if user is creator or admin
    if (workout.creator.id !== req.user.id && req.user.role !== 'admin' && req.user.role !== 'trainer') {
      return next(new AppError('You do not have permission to update this workout', 403));
    }
    
    // Upload to cloudinary
    const result = await cloudinary.uploader.upload(req.file.path, {
      folder: 'fitgent/workouts',
      width: 800,
      height: 600,
      crop: 'fill'
    });
    
    // Update workout image
    const updatedWorkout = await Workout.findByIdAndUpdate(
      req.params.id,
      { image: result.secure_url },
      { new: true }
    );
    
    res.status(200).json({
      status: 'success',
      data: {
        workout: updatedWorkout
      }
    });
  } catch (error) {
    next(error);
  }
};

// Get recommended workouts
exports.getRecommendedWorkouts = async (req, res, next) => {
  try {
    const user = await User.findById(req.user.id);
    
    if (!user) {
      return next(new AppError('User not found', 404));
    }
    
    // Get user's fitness goal and activity level
    const { fitnessGoal, activityLevel } = user;
    
    // Get user's completed workouts
    const completedWorkouts = await WorkoutLog.find({ 
      user: req.user.id,
      completed: true
    }).select('workout');
    
    const completedWorkoutIds = completedWorkouts.map(log => log.workout);
    
    // Find workouts based on user's goal and activity level
    let difficultyLevel;
    
    switch (activityLevel) {
      case 'sedentary':
        difficultyLevel = 'beginner';
        break;
      case 'lightly_active':
        difficultyLevel = 'beginner';
        break;
      case 'moderately_active':
        difficultyLevel = 'intermediate';
        break;
      case 'very_active':
        difficultyLevel = 'advanced';
        break;
      case 'extremely_active':
        difficultyLevel = 'expert';
        break;
      default:
        difficultyLevel = 'beginner';
    }
    
    // Find workouts that match user's goal and difficulty
    let categoryFilter;
    
    switch (fitnessGoal) {
      case 'lose_weight':
        categoryFilter = ['cardio', 'hiit'];
        break;
      case 'gain_muscle':
        categoryFilter = ['strength', 'bodyweight'];
        break;
      case 'improve_fitness':
        categoryFilter = ['cardio', 'strength', 'hiit'];
        break;
      case 'maintain':
        categoryFilter = ['cardio', 'strength', 'flexibility'];
        break;
      default:
        categoryFilter = ['cardio', 'strength', 'flexibility', 'balance', 'hiit'];
    }
    
    // Find recommended workouts
    const recommendedWorkouts = await Workout.find({
      difficulty: difficultyLevel,
      category: { $in: categoryFilter },
      _id: { $nin: completedWorkoutIds },
      isPublic: true
    }).limit(5);
    
    // If not enough recommendations, add some popular workouts
    if (recommendedWorkouts.length < 5) {
      const popularWorkouts = await Workout.find({
        _id: { $nin: [...completedWorkoutIds, ...recommendedWorkouts.map(w => w._id)] },
        isPublic: true
      }).sort('-rating').limit(5 - recommendedWorkouts.length);
      
      recommendedWorkouts.push(...popularWorkouts);
    }
    
    res.status(200).json({
      status: 'success',
      results: recommendedWorkouts.length,
      data: {
        workouts: recommendedWorkouts
      }
    });
  } catch (error) {
    next(error);
  }
};

// Add review to workout
exports.addWorkoutReview = async (req, res, next) => {
  try {
    const { rating, comment } = req.body;
    
    if (!rating) {
      return next(new AppError('Please provide a rating', 400));
    }
    
    const workout = await Workout.findById(req.params.id);
    
    if (!workout) {
      return next(new AppError('No workout found with that ID', 404));
    }
    
    // Check if user has already reviewed this workout
    const existingReviewIndex = workout.reviews.findIndex(
      review => review.user.toString() === req.user.id
    );
    
    if (existingReviewIndex >= 0) {
      // Update existing review
      workout.reviews[existingReviewIndex].rating = rating;
      workout.reviews[existingReviewIndex].comment = comment;
    } else {
      // Add new review
      workout.reviews.push({
        user: req.user.id,
        rating,
        comment
      });
    }
    
    await workout.save();
    
    res.status(200).json({
      status: 'success',
      data: {
        workout
      }
    });
  } catch (error) {
    next(error);
  }
};

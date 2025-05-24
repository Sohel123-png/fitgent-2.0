const User = require('../models/userModel');
const AppError = require('../utils/appError');
const cloudinary = require('../utils/cloudinary');

// Filter object to only allowed fields
const filterObj = (obj, ...allowedFields) => {
  const newObj = {};
  Object.keys(obj).forEach(el => {
    if (allowedFields.includes(el)) newObj[el] = obj[el];
  });
  return newObj;
};

// Get all users (admin only)
exports.getAllUsers = async (req, res, next) => {
  try {
    const users = await User.find();
    
    res.status(200).json({
      status: 'success',
      results: users.length,
      data: {
        users
      }
    });
  } catch (error) {
    next(error);
  }
};

// Get user by ID
exports.getUser = async (req, res, next) => {
  try {
    const user = await User.findById(req.params.id);
    
    if (!user) {
      return next(new AppError('No user found with that ID', 404));
    }
    
    res.status(200).json({
      status: 'success',
      data: {
        user
      }
    });
  } catch (error) {
    next(error);
  }
};

// Update user
exports.updateUser = async (req, res, next) => {
  try {
    // Check if user is trying to update password
    if (req.body.password || req.body.passwordConfirm) {
      return next(new AppError('This route is not for password updates. Please use /update-password.', 400));
    }
    
    // Filter out unwanted fields that are not allowed to be updated
    const filteredBody = filterObj(
      req.body,
      'firstName',
      'lastName',
      'bio',
      'age',
      'gender',
      'height',
      'weight',
      'fitnessGoal',
      'activityLevel'
    );
    
    // Update user document
    const updatedUser = await User.findByIdAndUpdate(req.params.id, filteredBody, {
      new: true,
      runValidators: true
    });
    
    if (!updatedUser) {
      return next(new AppError('No user found with that ID', 404));
    }
    
    res.status(200).json({
      status: 'success',
      data: {
        user: updatedUser
      }
    });
  } catch (error) {
    next(error);
  }
};

// Delete user (admin only or self)
exports.deleteUser = async (req, res, next) => {
  try {
    // Check if user is trying to delete themselves or is admin
    if (req.user.role !== 'admin' && req.user.id !== req.params.id) {
      return next(new AppError('You do not have permission to delete this user', 403));
    }
    
    const user = await User.findByIdAndUpdate(req.params.id, { active: false });
    
    if (!user) {
      return next(new AppError('No user found with that ID', 404));
    }
    
    res.status(204).json({
      status: 'success',
      data: null
    });
  } catch (error) {
    next(error);
  }
};

// Update user avatar
exports.updateAvatar = async (req, res, next) => {
  try {
    // Check if file exists
    if (!req.file) {
      return next(new AppError('Please upload an image', 400));
    }
    
    // Upload to cloudinary
    const result = await cloudinary.uploader.upload(req.file.path, {
      folder: 'fitgent/avatars',
      width: 500,
      height: 500,
      crop: 'fill',
      gravity: 'face'
    });
    
    // Update user avatar
    const updatedUser = await User.findByIdAndUpdate(
      req.params.id,
      { avatar: result.secure_url },
      { new: true }
    );
    
    if (!updatedUser) {
      return next(new AppError('No user found with that ID', 404));
    }
    
    res.status(200).json({
      status: 'success',
      data: {
        user: updatedUser
      }
    });
  } catch (error) {
    next(error);
  }
};

// Get user progress
exports.getUserProgress = async (req, res, next) => {
  try {
    const userId = req.params.id;
    
    // Get user
    const user = await User.findById(userId);
    
    if (!user) {
      return next(new AppError('No user found with that ID', 404));
    }
    
    // Get workout logs
    const WorkoutLog = require('../models/workoutLogModel');
    const workoutLogs = await WorkoutLog.find({ user: userId })
      .sort('-date')
      .limit(30);
    
    // Get meal logs
    const Meal = require('../models/mealModel');
    const mealLogs = await Meal.find({ user: userId })
      .sort('-date')
      .limit(30);
    
    // Get water intake
    const WaterIntake = require('../models/waterIntakeModel');
    const waterIntake = await WaterIntake.getWeeklySummary(userId);
    
    // Get sleep logs
    const SleepLog = require('../models/sleepLogModel');
    const sleepLogs = await SleepLog.getWeeklySummary(userId);
    
    res.status(200).json({
      status: 'success',
      data: {
        workoutLogs,
        mealLogs,
        waterIntake,
        sleepLogs
      }
    });
  } catch (error) {
    next(error);
  }
};

// Get user stats
exports.getUserStats = async (req, res, next) => {
  try {
    const userId = req.params.id;
    
    // Get user
    const user = await User.findById(userId);
    
    if (!user) {
      return next(new AppError('No user found with that ID', 404));
    }
    
    // Get workout count
    const WorkoutLog = require('../models/workoutLogModel');
    const workoutCount = await WorkoutLog.countDocuments({ user: userId });
    
    // Get total workout duration
    const workoutStats = await WorkoutLog.aggregate([
      { $match: { user: mongoose.Types.ObjectId(userId) } },
      { $group: { _id: null, totalDuration: { $sum: '$duration' }, totalCalories: { $sum: '$caloriesBurned' } } }
    ]);
    
    // Get meal stats
    const Meal = require('../models/mealModel');
    const mealStats = await Meal.aggregate([
      { $match: { user: mongoose.Types.ObjectId(userId) } },
      { $group: { _id: null, totalCalories: { $sum: '$totalCalories' }, totalProtein: { $sum: '$totalProtein' } } }
    ]);
    
    // Get water intake stats
    const WaterIntake = require('../models/waterIntakeModel');
    const waterStats = await WaterIntake.aggregate([
      { $match: { user: mongoose.Types.ObjectId(userId) } },
      { $group: { _id: null, totalAmount: { $sum: '$amount' } } }
    ]);
    
    // Get sleep stats
    const SleepLog = require('../models/sleepLogModel');
    const sleepStats = await SleepLog.aggregate([
      { $match: { user: mongoose.Types.ObjectId(userId) } },
      { $group: { _id: null, avgDuration: { $avg: '$duration' }, avgQuality: { $avg: '$quality' } } }
    ]);
    
    res.status(200).json({
      status: 'success',
      data: {
        workoutCount,
        workoutStats: workoutStats[0] || { totalDuration: 0, totalCalories: 0 },
        mealStats: mealStats[0] || { totalCalories: 0, totalProtein: 0 },
        waterStats: waterStats[0] || { totalAmount: 0 },
        sleepStats: sleepStats[0] || { avgDuration: 0, avgQuality: 0 }
      }
    });
  } catch (error) {
    next(error);
  }
};

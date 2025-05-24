const User = require('../models/userModel');
const Trainer = require('../models/trainerModel');
const Post = require('../models/postModel');
const Workout = require('../models/workoutModel');
const WorkoutPlan = require('../models/workoutPlanModel');
const Notification = require('../models/notificationModel');
const AppError = require('../utils/appError');

// Get platform stats
exports.getPlatformStats = async (req, res, next) => {
  try {
    // Get user stats
    const totalUsers = await User.countDocuments();
    const newUsersToday = await User.countDocuments({
      createdAt: { $gte: new Date(new Date().setHours(0, 0, 0, 0)) }
    });
    
    // Get trainer stats
    const totalTrainers = await Trainer.countDocuments({ isApproved: true });
    const pendingTrainerApplications = await Trainer.countDocuments({ isApproved: false });
    
    // Get content stats
    const totalWorkouts = await Workout.countDocuments();
    const totalWorkoutPlans = await WorkoutPlan.countDocuments();
    const totalPosts = await Post.countDocuments();
    
    // Get user role distribution
    const userRoles = await User.aggregate([
      {
        $group: {
          _id: '$role',
          count: { $sum: 1 }
        }
      }
    ]);
    
    // Get user activity
    const activeUsers = await User.countDocuments({
      updatedAt: { $gte: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000) }
    });
    
    res.status(200).json({
      status: 'success',
      data: {
        users: {
          total: totalUsers,
          newToday: newUsersToday,
          active: activeUsers,
          roles: userRoles
        },
        trainers: {
          total: totalTrainers,
          pendingApplications: pendingTrainerApplications
        },
        content: {
          workouts: totalWorkouts,
          workoutPlans: totalWorkoutPlans,
          posts: totalPosts
        }
      }
    });
  } catch (error) {
    next(error);
  }
};

// Get trainer applications
exports.getTrainerApplications = async (req, res, next) => {
  try {
    const applications = await Trainer.find({ isApproved: false });
    
    res.status(200).json({
      status: 'success',
      results: applications.length,
      data: {
        applications
      }
    });
  } catch (error) {
    next(error);
  }
};

// Approve/reject trainer application
exports.processTrainerApplication = async (req, res, next) => {
  try {
    const { approve } = req.body;
    
    if (approve === undefined) {
      return next(new AppError('Please specify whether to approve or reject the application', 400));
    }
    
    const trainer = await Trainer.findById(req.params.id);
    
    if (!trainer) {
      return next(new AppError('No trainer application found with that ID', 404));
    }
    
    // Update trainer approval status
    trainer.isApproved = approve;
    await trainer.save();
    
    // Get user
    const user = await User.findById(trainer.user);
    
    if (!user) {
      return next(new AppError('User not found', 404));
    }
    
    // Update user role if approved
    if (approve) {
      user.role = 'trainer';
    } else {
      user.role = 'user';
    }
    
    await user.save({ validateBeforeSave: false });
    
    // Create notification for user
    await Notification.createNotification({
      user: trainer.user,
      type: 'system',
      title: approve ? 'Trainer Application Approved' : 'Trainer Application Rejected',
      message: approve
        ? 'Your application to become a trainer has been approved!'
        : 'Your application to become a trainer has been rejected.',
      priority: 'high'
    });
    
    res.status(200).json({
      status: 'success',
      data: {
        trainer
      }
    });
  } catch (error) {
    next(error);
  }
};

// Get content for moderation
exports.getContentForModeration = async (req, res, next) => {
  try {
    // Get content type
    const { type = 'posts' } = req.query;
    
    let content;
    
    if (type === 'posts') {
      // Get posts pending moderation
      content = await Post.find({
        moderationStatus: 'pending'
      }).sort('-createdAt');
    } else if (type === 'workouts') {
      // Get workouts
      content = await Workout.find().sort('-createdAt');
    } else if (type === 'workout-plans') {
      // Get workout plans
      content = await WorkoutPlan.find().sort('-createdAt');
    } else {
      return next(new AppError('Invalid content type', 400));
    }
    
    res.status(200).json({
      status: 'success',
      results: content.length,
      data: {
        content
      }
    });
  } catch (error) {
    next(error);
  }
};

// Moderate content
exports.moderateContent = async (req, res, next) => {
  try {
    const { type, status, reason } = req.body;
    
    if (!type || !status) {
      return next(new AppError('Please provide content type and moderation status', 400));
    }
    
    if (status === 'rejected' && !reason) {
      return next(new AppError('Please provide a reason for rejection', 400));
    }
    
    let content;
    
    if (type === 'post') {
      // Moderate post
      content = await Post.findById(req.params.id);
      
      if (!content) {
        return next(new AppError('No post found with that ID', 404));
      }
      
      content.moderationStatus = status;
      content.moderationReason = reason;
      content.isModerated = true;
      
      await content.save();
      
      // Create notification for post owner
      await Notification.createNotification({
        user: content.user,
        type: 'system',
        title: status === 'approved' ? 'Post Approved' : 'Post Rejected',
        message: status === 'approved'
          ? 'Your post has been approved and is now visible to the community.'
          : `Your post has been rejected. Reason: ${reason}`,
        relatedModel: 'Post',
        relatedId: content._id
      });
    } else if (type === 'workout') {
      // Moderate workout
      content = await Workout.findById(req.params.id);
      
      if (!content) {
        return next(new AppError('No workout found with that ID', 404));
      }
      
      content.isPublic = status === 'approved';
      await content.save();
      
      // Create notification for workout creator
      await Notification.createNotification({
        user: content.creator,
        type: 'system',
        title: status === 'approved' ? 'Workout Approved' : 'Workout Rejected',
        message: status === 'approved'
          ? 'Your workout has been approved and is now public.'
          : `Your workout has been rejected. Reason: ${reason}`,
        relatedModel: 'Workout',
        relatedId: content._id
      });
    } else if (type === 'workout-plan') {
      // Moderate workout plan
      content = await WorkoutPlan.findById(req.params.id);
      
      if (!content) {
        return next(new AppError('No workout plan found with that ID', 404));
      }
      
      content.isPublic = status === 'approved';
      await content.save();
      
      // Create notification for workout plan creator
      await Notification.createNotification({
        user: content.creator,
        type: 'system',
        title: status === 'approved' ? 'Workout Plan Approved' : 'Workout Plan Rejected',
        message: status === 'approved'
          ? 'Your workout plan has been approved and is now public.'
          : `Your workout plan has been rejected. Reason: ${reason}`,
        relatedModel: 'WorkoutPlan',
        relatedId: content._id
      });
    } else {
      return next(new AppError('Invalid content type', 400));
    }
    
    res.status(200).json({
      status: 'success',
      data: {
        content
      }
    });
  } catch (error) {
    next(error);
  }
};

// Manage user roles
exports.manageUserRole = async (req, res, next) => {
  try {
    const { role } = req.body;
    
    if (!role || !['user', 'trainer', 'admin'].includes(role)) {
      return next(new AppError('Please provide a valid role', 400));
    }
    
    const user = await User.findById(req.params.id);
    
    if (!user) {
      return next(new AppError('No user found with that ID', 404));
    }
    
    // Update user role
    user.role = role;
    await user.save({ validateBeforeSave: false });
    
    // If changing to trainer, create trainer profile if it doesn't exist
    if (role === 'trainer') {
      const existingTrainer = await Trainer.findOne({ user: user._id });
      
      if (!existingTrainer) {
        await Trainer.create({
          user: user._id,
          specialization: [],
          experience: 0,
          certification: [],
          isApproved: true
        });
      } else if (!existingTrainer.isApproved) {
        existingTrainer.isApproved = true;
        await existingTrainer.save();
      }
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

// Get user activity logs
exports.getUserActivityLogs = async (req, res, next) => {
  try {
    const userId = req.params.id;
    
    // Get user
    const user = await User.findById(userId);
    
    if (!user) {
      return next(new AppError('No user found with that ID', 404));
    }
    
    // Get user's posts
    const posts = await Post.find({ user: userId }).sort('-createdAt').limit(10);
    
    // Get user's workouts
    const WorkoutLog = require('../models/workoutLogModel');
    const workouts = await WorkoutLog.find({ user: userId }).sort('-date').limit(10);
    
    // Get user's meal logs
    const Meal = require('../models/mealModel');
    const meals = await Meal.find({ user: userId }).sort('-date').limit(10);
    
    res.status(200).json({
      status: 'success',
      data: {
        user,
        activity: {
          posts,
          workouts,
          meals
        }
      }
    });
  } catch (error) {
    next(error);
  }
};

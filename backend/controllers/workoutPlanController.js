const WorkoutPlan = require('../models/workoutPlanModel');
const User = require('../models/userModel');
const Notification = require('../models/notificationModel');
const AppError = require('../utils/appError');
const cloudinary = require('../utils/cloudinary');

// Get all workout plans
exports.getAllWorkoutPlans = async (req, res, next) => {
  try {
    // Build query
    const queryObj = { ...req.query };
    const excludedFields = ['page', 'sort', 'limit', 'fields'];
    excludedFields.forEach(el => delete queryObj[el]);
    
    // Advanced filtering
    let queryStr = JSON.stringify(queryObj);
    queryStr = queryStr.replace(/\b(gte|gt|lte|lt)\b/g, match => `$${match}`);
    
    // Find workout plans
    let query = WorkoutPlan.find(JSON.parse(queryStr));
    
    // If user is not admin or trainer, only show public plans or plans assigned to them
    if (req.user.role !== 'admin' && req.user.role !== 'trainer') {
      query = query.find({
        $or: [
          { isPublic: true },
          { 'assignedUsers.user': req.user.id }
        ]
      });
    }
    
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
    const workoutPlans = await query;
    
    // Send response
    res.status(200).json({
      status: 'success',
      results: workoutPlans.length,
      data: {
        workoutPlans
      }
    });
  } catch (error) {
    next(error);
  }
};

// Get workout plan by ID
exports.getWorkoutPlan = async (req, res, next) => {
  try {
    const workoutPlan = await WorkoutPlan.findById(req.params.id);
    
    if (!workoutPlan) {
      return next(new AppError('No workout plan found with that ID', 404));
    }
    
    // Check if user has access to this plan
    if (
      !workoutPlan.isPublic &&
      workoutPlan.creator.id !== req.user.id &&
      req.user.role !== 'admin' &&
      req.user.role !== 'trainer' &&
      !workoutPlan.assignedUsers.some(assignment => assignment.user.toString() === req.user.id)
    ) {
      return next(new AppError('You do not have permission to view this workout plan', 403));
    }
    
    res.status(200).json({
      status: 'success',
      data: {
        workoutPlan
      }
    });
  } catch (error) {
    next(error);
  }
};

// Create workout plan
exports.createWorkoutPlan = async (req, res, next) => {
  try {
    // Add creator to body
    req.body.creator = req.user.id;
    
    // Create workout plan
    const newWorkoutPlan = await WorkoutPlan.create(req.body);
    
    res.status(201).json({
      status: 'success',
      data: {
        workoutPlan: newWorkoutPlan
      }
    });
  } catch (error) {
    next(error);
  }
};

// Update workout plan
exports.updateWorkoutPlan = async (req, res, next) => {
  try {
    const workoutPlan = await WorkoutPlan.findById(req.params.id);
    
    if (!workoutPlan) {
      return next(new AppError('No workout plan found with that ID', 404));
    }
    
    // Check if user is creator or admin
    if (workoutPlan.creator.id !== req.user.id && req.user.role !== 'admin' && req.user.role !== 'trainer') {
      return next(new AppError('You do not have permission to update this workout plan', 403));
    }
    
    // Update workout plan
    const updatedWorkoutPlan = await WorkoutPlan.findByIdAndUpdate(req.params.id, req.body, {
      new: true,
      runValidators: true
    });
    
    res.status(200).json({
      status: 'success',
      data: {
        workoutPlan: updatedWorkoutPlan
      }
    });
  } catch (error) {
    next(error);
  }
};

// Delete workout plan
exports.deleteWorkoutPlan = async (req, res, next) => {
  try {
    const workoutPlan = await WorkoutPlan.findById(req.params.id);
    
    if (!workoutPlan) {
      return next(new AppError('No workout plan found with that ID', 404));
    }
    
    // Check if user is creator or admin
    if (workoutPlan.creator.id !== req.user.id && req.user.role !== 'admin') {
      return next(new AppError('You do not have permission to delete this workout plan', 403));
    }
    
    await WorkoutPlan.findByIdAndDelete(req.params.id);
    
    res.status(204).json({
      status: 'success',
      data: null
    });
  } catch (error) {
    next(error);
  }
};

// Upload workout plan image
exports.uploadWorkoutPlanImage = async (req, res, next) => {
  try {
    // Check if file exists
    if (!req.file) {
      return next(new AppError('Please upload an image', 400));
    }
    
    const workoutPlan = await WorkoutPlan.findById(req.params.id);
    
    if (!workoutPlan) {
      return next(new AppError('No workout plan found with that ID', 404));
    }
    
    // Check if user is creator or admin
    if (workoutPlan.creator.id !== req.user.id && req.user.role !== 'admin' && req.user.role !== 'trainer') {
      return next(new AppError('You do not have permission to update this workout plan', 403));
    }
    
    // Upload to cloudinary
    const result = await cloudinary.uploader.upload(req.file.path, {
      folder: 'fitgent/workout-plans',
      width: 800,
      height: 600,
      crop: 'fill'
    });
    
    // Update workout plan image
    const updatedWorkoutPlan = await WorkoutPlan.findByIdAndUpdate(
      req.params.id,
      { image: result.secure_url },
      { new: true }
    );
    
    res.status(200).json({
      status: 'success',
      data: {
        workoutPlan: updatedWorkoutPlan
      }
    });
  } catch (error) {
    next(error);
  }
};

// Assign workout plan to users
exports.assignWorkoutPlan = async (req, res, next) => {
  try {
    const { users, startDate } = req.body;
    
    if (!users || !Array.isArray(users) || users.length === 0) {
      return next(new AppError('Please provide at least one user ID', 400));
    }
    
    const workoutPlan = await WorkoutPlan.findById(req.params.id);
    
    if (!workoutPlan) {
      return next(new AppError('No workout plan found with that ID', 404));
    }
    
    // Check if user is creator or admin or trainer
    if (workoutPlan.creator.id !== req.user.id && req.user.role !== 'admin' && req.user.role !== 'trainer') {
      return next(new AppError('You do not have permission to assign this workout plan', 403));
    }
    
    // Validate users
    const validUsers = await User.find({ _id: { $in: users } });
    
    if (validUsers.length !== users.length) {
      return next(new AppError('One or more user IDs are invalid', 400));
    }
    
    // Calculate end date
    const start = startDate ? new Date(startDate) : new Date();
    const end = new Date(start);
    end.setDate(end.getDate() + workoutPlan.duration);
    
    // Prepare assignments
    const assignments = users.map(userId => {
      // Check if user is already assigned
      const existingAssignment = workoutPlan.assignedUsers.find(
        assignment => assignment.user.toString() === userId
      );
      
      if (existingAssignment) {
        // Update existing assignment
        existingAssignment.startDate = start;
        existingAssignment.endDate = end;
        existingAssignment.progress = 0;
        existingAssignment.status = 'not_started';
        return null;
      } else {
        // Create new assignment
        return {
          user: userId,
          assignedAt: new Date(),
          startDate: start,
          endDate: end,
          progress: 0,
          status: 'not_started'
        };
      }
    }).filter(assignment => assignment !== null);
    
    // Add new assignments
    workoutPlan.assignedUsers.push(...assignments);
    
    await workoutPlan.save();
    
    // Create notifications for assigned users
    const notifications = users.map(userId => ({
      user: userId,
      type: 'plan_assigned',
      title: 'New Workout Plan Assigned',
      message: `You have been assigned to the workout plan: ${workoutPlan.name}`,
      sender: req.user.id,
      relatedModel: 'WorkoutPlan',
      relatedId: workoutPlan._id,
      data: {
        workoutPlanId: workoutPlan._id,
        workoutPlanName: workoutPlan.name,
        startDate: start,
        endDate: end
      }
    }));
    
    await Notification.insertMany(notifications);
    
    res.status(200).json({
      status: 'success',
      data: {
        workoutPlan
      }
    });
  } catch (error) {
    next(error);
  }
};

// Get workout plans assigned to user
exports.getAssignedWorkoutPlans = async (req, res, next) => {
  try {
    const userId = req.params.userId || req.user.id;
    
    // Find workout plans assigned to user
    const workoutPlans = await WorkoutPlan.find({
      'assignedUsers.user': userId
    });
    
    res.status(200).json({
      status: 'success',
      results: workoutPlans.length,
      data: {
        workoutPlans
      }
    });
  } catch (error) {
    next(error);
  }
};

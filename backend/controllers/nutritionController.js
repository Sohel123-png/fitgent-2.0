const Meal = require('../models/mealModel');
const AppError = require('../utils/appError');
const cloudinary = require('../utils/cloudinary');

// Get user meals
exports.getUserMeals = async (req, res, next) => {
  try {
    // Build query
    const queryObj = { ...req.query };
    queryObj.user = req.user.id; // Only get meals for current user
    
    const excludedFields = ['page', 'sort', 'limit', 'fields'];
    excludedFields.forEach(el => delete queryObj[el]);
    
    // Date filtering
    if (queryObj.date) {
      const date = new Date(queryObj.date);
      const nextDay = new Date(date);
      nextDay.setDate(date.getDate() + 1);
      
      queryObj.date = {
        $gte: date,
        $lt: nextDay
      };
    }
    
    // Advanced filtering
    let queryStr = JSON.stringify(queryObj);
    queryStr = queryStr.replace(/\b(gte|gt|lte|lt)\b/g, match => `$${match}`);
    
    // Find meals
    let query = Meal.find(JSON.parse(queryStr));
    
    // Sorting
    if (req.query.sort) {
      const sortBy = req.query.sort.split(',').join(' ');
      query = query.sort(sortBy);
    } else {
      query = query.sort('-date');
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
    const meals = await query;
    
    // Send response
    res.status(200).json({
      status: 'success',
      results: meals.length,
      data: {
        meals
      }
    });
  } catch (error) {
    next(error);
  }
};

// Get meal by ID
exports.getMeal = async (req, res, next) => {
  try {
    const meal = await Meal.findById(req.params.id);
    
    if (!meal) {
      return next(new AppError('No meal found with that ID', 404));
    }
    
    // Check if meal belongs to user
    if (meal.user.id !== req.user.id && req.user.role !== 'admin') {
      return next(new AppError('You do not have permission to view this meal', 403));
    }
    
    res.status(200).json({
      status: 'success',
      data: {
        meal
      }
    });
  } catch (error) {
    next(error);
  }
};

// Create meal
exports.createMeal = async (req, res, next) => {
  try {
    // Add user to body
    req.body.user = req.user.id;
    
    // Create meal
    const newMeal = await Meal.create(req.body);
    
    res.status(201).json({
      status: 'success',
      data: {
        meal: newMeal
      }
    });
  } catch (error) {
    next(error);
  }
};

// Update meal
exports.updateMeal = async (req, res, next) => {
  try {
    const meal = await Meal.findById(req.params.id);
    
    if (!meal) {
      return next(new AppError('No meal found with that ID', 404));
    }
    
    // Check if meal belongs to user
    if (meal.user.id !== req.user.id && req.user.role !== 'admin') {
      return next(new AppError('You do not have permission to update this meal', 403));
    }
    
    // Update meal
    const updatedMeal = await Meal.findByIdAndUpdate(req.params.id, req.body, {
      new: true,
      runValidators: true
    });
    
    res.status(200).json({
      status: 'success',
      data: {
        meal: updatedMeal
      }
    });
  } catch (error) {
    next(error);
  }
};

// Delete meal
exports.deleteMeal = async (req, res, next) => {
  try {
    const meal = await Meal.findById(req.params.id);
    
    if (!meal) {
      return next(new AppError('No meal found with that ID', 404));
    }
    
    // Check if meal belongs to user
    if (meal.user.id !== req.user.id && req.user.role !== 'admin') {
      return next(new AppError('You do not have permission to delete this meal', 403));
    }
    
    await Meal.findByIdAndDelete(req.params.id);
    
    res.status(204).json({
      status: 'success',
      data: null
    });
  } catch (error) {
    next(error);
  }
};

// Upload meal image
exports.uploadMealImage = async (req, res, next) => {
  try {
    // Check if file exists
    if (!req.file) {
      return next(new AppError('Please upload an image', 400));
    }
    
    const meal = await Meal.findById(req.params.id);
    
    if (!meal) {
      return next(new AppError('No meal found with that ID', 404));
    }
    
    // Check if meal belongs to user
    if (meal.user.id !== req.user.id && req.user.role !== 'admin') {
      return next(new AppError('You do not have permission to update this meal', 403));
    }
    
    // Upload to cloudinary
    const result = await cloudinary.uploader.upload(req.file.path, {
      folder: 'fitgent/meals',
      width: 800,
      height: 600,
      crop: 'fill'
    });
    
    // Update meal image
    const updatedMeal = await Meal.findByIdAndUpdate(
      req.params.id,
      { image: result.secure_url },
      { new: true }
    );
    
    res.status(200).json({
      status: 'success',
      data: {
        meal: updatedMeal
      }
    });
  } catch (error) {
    next(error);
  }
};

// Get nutrition stats
exports.getNutritionStats = async (req, res, next) => {
  try {
    // Get date range
    const { startDate, endDate } = req.query;
    
    let dateFilter = { user: req.user.id };
    
    if (startDate && endDate) {
      dateFilter.date = {
        $gte: new Date(startDate),
        $lte: new Date(endDate)
      };
    } else if (startDate) {
      dateFilter.date = { $gte: new Date(startDate) };
    } else if (endDate) {
      dateFilter.date = { $lte: new Date(endDate) };
    }
    
    // Get daily totals
    const dailyTotals = await Meal.aggregate([
      { $match: dateFilter },
      {
        $group: {
          _id: { $dateToString: { format: '%Y-%m-%d', date: '$date' } },
          totalCalories: { $sum: '$totalCalories' },
          totalProtein: { $sum: '$totalProtein' },
          totalCarbs: { $sum: '$totalCarbs' },
          totalFat: { $sum: '$totalFat' },
          totalFiber: { $sum: '$totalFiber' },
          mealCount: { $sum: 1 }
        }
      },
      { $sort: { _id: 1 } }
    ]);
    
    // Get meal type breakdown
    const mealTypeBreakdown = await Meal.aggregate([
      { $match: dateFilter },
      {
        $group: {
          _id: '$type',
          totalCalories: { $sum: '$totalCalories' },
          count: { $sum: 1 }
        }
      }
    ]);
    
    // Get overall stats
    const overallStats = await Meal.aggregate([
      { $match: dateFilter },
      {
        $group: {
          _id: null,
          totalCalories: { $sum: '$totalCalories' },
          totalProtein: { $sum: '$totalProtein' },
          totalCarbs: { $sum: '$totalCarbs' },
          totalFat: { $sum: '$totalFat' },
          totalFiber: { $sum: '$totalFiber' },
          avgCaloriesPerDay: { $avg: '$totalCalories' },
          mealCount: { $sum: 1 }
        }
      }
    ]);
    
    res.status(200).json({
      status: 'success',
      data: {
        dailyTotals,
        mealTypeBreakdown,
        overallStats: overallStats[0] || {
          totalCalories: 0,
          totalProtein: 0,
          totalCarbs: 0,
          totalFat: 0,
          totalFiber: 0,
          avgCaloriesPerDay: 0,
          mealCount: 0
        }
      }
    });
  } catch (error) {
    next(error);
  }
};

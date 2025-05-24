const WaterIntake = require('../models/waterIntakeModel');
const SleepLog = require('../models/sleepLogModel');
const AppError = require('../utils/appError');

// Water Intake Controllers
// -----------------------

// Get water intake
exports.getWaterIntake = async (req, res, next) => {
  try {
    // Build query
    const queryObj = { ...req.query };
    queryObj.user = req.user.id; // Only get water intake for current user
    
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
    
    // Find water intake
    let query = WaterIntake.find(JSON.parse(queryStr));
    
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
    const waterIntake = await query;
    
    // Send response
    res.status(200).json({
      status: 'success',
      results: waterIntake.length,
      data: {
        waterIntake
      }
    });
  } catch (error) {
    next(error);
  }
};

// Add water intake
exports.addWaterIntake = async (req, res, next) => {
  try {
    // Add user to body
    req.body.user = req.user.id;
    
    // Create water intake
    const newWaterIntake = await WaterIntake.create(req.body);
    
    // Get daily total
    const today = new Date();
    const dailyTotal = await WaterIntake.getDailyTotal(req.user.id, today);
    
    res.status(201).json({
      status: 'success',
      data: {
        waterIntake: newWaterIntake,
        dailyTotal
      }
    });
  } catch (error) {
    next(error);
  }
};

// Get water intake stats
exports.getWaterIntakeStats = async (req, res, next) => {
  try {
    // Get weekly summary
    const weeklySummary = await WaterIntake.getWeeklySummary(req.user.id);
    
    // Get daily total for today
    const today = new Date();
    const dailyTotal = await WaterIntake.getDailyTotal(req.user.id, today);
    
    // Get monthly total
    const startOfMonth = new Date(today.getFullYear(), today.getMonth(), 1);
    const endOfMonth = new Date(today.getFullYear(), today.getMonth() + 1, 0);
    
    const monthlyTotal = await WaterIntake.aggregate([
      {
        $match: {
          user: req.user._id,
          date: {
            $gte: startOfMonth,
            $lte: endOfMonth
          }
        }
      },
      {
        $group: {
          _id: null,
          total: { $sum: '$amount' },
          count: { $sum: 1 },
          avgPerDay: { $avg: { $sum: '$amount' } }
        }
      }
    ]);
    
    res.status(200).json({
      status: 'success',
      data: {
        weeklySummary,
        dailyTotal,
        monthlyTotal: monthlyTotal[0] || { total: 0, count: 0, avgPerDay: 0 }
      }
    });
  } catch (error) {
    next(error);
  }
};

// Sleep Log Controllers
// --------------------

// Get sleep logs
exports.getSleepLogs = async (req, res, next) => {
  try {
    // Build query
    const queryObj = { ...req.query };
    queryObj.user = req.user.id; // Only get sleep logs for current user
    
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
    
    // Find sleep logs
    let query = SleepLog.find(JSON.parse(queryStr));
    
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
    const sleepLogs = await query;
    
    // Send response
    res.status(200).json({
      status: 'success',
      results: sleepLogs.length,
      data: {
        sleepLogs
      }
    });
  } catch (error) {
    next(error);
  }
};

// Add sleep log
exports.addSleepLog = async (req, res, next) => {
  try {
    // Add user to body
    req.body.user = req.user.id;
    
    // Create sleep log
    const newSleepLog = await SleepLog.create(req.body);
    
    res.status(201).json({
      status: 'success',
      data: {
        sleepLog: newSleepLog
      }
    });
  } catch (error) {
    next(error);
  }
};

// Get sleep stats
exports.getSleepStats = async (req, res, next) => {
  try {
    // Get weekly summary
    const weeklySummary = await SleepLog.getWeeklySummary(req.user.id);
    
    // Get monthly average
    const today = new Date();
    const monthlyAverage = await SleepLog.getMonthlyAverage(
      req.user.id,
      today.getFullYear(),
      today.getMonth() + 1
    );
    
    // Get overall stats
    const overallStats = await SleepLog.aggregate([
      {
        $match: { user: req.user._id }
      },
      {
        $group: {
          _id: null,
          avgDuration: { $avg: '$duration' },
          avgQuality: { $avg: '$quality' },
          totalSleep: { $sum: '$duration' },
          count: { $sum: 1 }
        }
      }
    ]);
    
    res.status(200).json({
      status: 'success',
      data: {
        weeklySummary,
        monthlyAverage,
        overallStats: overallStats[0] || { avgDuration: 0, avgQuality: 0, totalSleep: 0, count: 0 }
      }
    });
  } catch (error) {
    next(error);
  }
};

// Get tracking stats (combined)
exports.getTrackingStats = async (req, res, next) => {
  try {
    // Get water intake stats
    const waterWeeklySummary = await WaterIntake.getWeeklySummary(req.user.id);
    const today = new Date();
    const waterDailyTotal = await WaterIntake.getDailyTotal(req.user.id, today);
    
    // Get sleep stats
    const sleepWeeklySummary = await SleepLog.getWeeklySummary(req.user.id);
    const sleepMonthlyAverage = await SleepLog.getMonthlyAverage(
      req.user.id,
      today.getFullYear(),
      today.getMonth() + 1
    );
    
    res.status(200).json({
      status: 'success',
      data: {
        water: {
          weeklySummary: waterWeeklySummary,
          dailyTotal: waterDailyTotal
        },
        sleep: {
          weeklySummary: sleepWeeklySummary,
          monthlyAverage: sleepMonthlyAverage
        }
      }
    });
  } catch (error) {
    next(error);
  }
};

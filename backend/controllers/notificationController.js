const Notification = require('../models/notificationModel');
const AppError = require('../utils/appError');

// Get user notifications
exports.getUserNotifications = async (req, res, next) => {
  try {
    // Build query
    const queryObj = { ...req.query };
    queryObj.user = req.user.id; // Only get notifications for current user
    
    const excludedFields = ['page', 'sort', 'limit', 'fields'];
    excludedFields.forEach(el => delete queryObj[el]);
    
    // Advanced filtering
    let queryStr = JSON.stringify(queryObj);
    queryStr = queryStr.replace(/\b(gte|gt|lte|lt)\b/g, match => `$${match}`);
    
    // Find notifications
    let query = Notification.find(JSON.parse(queryStr));
    
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
    const limit = parseInt(req.query.limit, 10) || 20;
    const skip = (page - 1) * limit;
    
    query = query.skip(skip).limit(limit);
    
    // Execute query
    const notifications = await query;
    
    // Get unread count
    const unreadCount = await Notification.countDocuments({
      user: req.user.id,
      isRead: false
    });
    
    // Send response
    res.status(200).json({
      status: 'success',
      results: notifications.length,
      unreadCount,
      data: {
        notifications
      }
    });
  } catch (error) {
    next(error);
  }
};

// Mark notification as read
exports.markNotificationAsRead = async (req, res, next) => {
  try {
    const notification = await Notification.findById(req.params.id);
    
    if (!notification) {
      return next(new AppError('No notification found with that ID', 404));
    }
    
    // Check if notification belongs to user
    if (notification.user.toString() !== req.user.id) {
      return next(new AppError('You do not have permission to update this notification', 403));
    }
    
    // Update notification
    notification.isRead = true;
    await notification.save();
    
    res.status(200).json({
      status: 'success',
      data: {
        notification
      }
    });
  } catch (error) {
    next(error);
  }
};

// Mark all notifications as read
exports.markAllNotificationsAsRead = async (req, res, next) => {
  try {
    // Update all unread notifications for user
    const result = await Notification.updateMany(
      { user: req.user.id, isRead: false },
      { isRead: true }
    );
    
    res.status(200).json({
      status: 'success',
      data: {
        markedCount: result.nModified
      }
    });
  } catch (error) {
    next(error);
  }
};

// Delete notification
exports.deleteNotification = async (req, res, next) => {
  try {
    const notification = await Notification.findById(req.params.id);
    
    if (!notification) {
      return next(new AppError('No notification found with that ID', 404));
    }
    
    // Check if notification belongs to user
    if (notification.user.toString() !== req.user.id && req.user.role !== 'admin') {
      return next(new AppError('You do not have permission to delete this notification', 403));
    }
    
    await Notification.findByIdAndDelete(req.params.id);
    
    res.status(204).json({
      status: 'success',
      data: null
    });
  } catch (error) {
    next(error);
  }
};

// Delete all read notifications
exports.deleteAllReadNotifications = async (req, res, next) => {
  try {
    // Delete all read notifications for user
    const result = await Notification.deleteMany({
      user: req.user.id,
      isRead: true
    });
    
    res.status(200).json({
      status: 'success',
      data: {
        deletedCount: result.deletedCount
      }
    });
  } catch (error) {
    next(error);
  }
};

// Create notification (for testing)
exports.createNotification = async (req, res, next) => {
  try {
    // Only allow admins to create notifications for other users
    if (req.body.user && req.body.user !== req.user.id && req.user.role !== 'admin') {
      return next(new AppError('You do not have permission to create notifications for other users', 403));
    }
    
    // Set user to current user if not specified
    if (!req.body.user) {
      req.body.user = req.user.id;
    }
    
    // Create notification
    const newNotification = await Notification.create(req.body);
    
    res.status(201).json({
      status: 'success',
      data: {
        notification: newNotification
      }
    });
  } catch (error) {
    next(error);
  }
};

// Get notification count
exports.getNotificationCount = async (req, res, next) => {
  try {
    // Get unread count
    const unreadCount = await Notification.countDocuments({
      user: req.user.id,
      isRead: false
    });
    
    // Get total count
    const totalCount = await Notification.countDocuments({
      user: req.user.id
    });
    
    res.status(200).json({
      status: 'success',
      data: {
        unreadCount,
        totalCount
      }
    });
  } catch (error) {
    next(error);
  }
};

const mongoose = require('mongoose');

const notificationSchema = new mongoose.Schema({
  user: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: [true, 'Notification must belong to a user']
  },
  type: {
    type: String,
    required: [true, 'Notification must have a type'],
    enum: [
      'workout',
      'water',
      'meal',
      'achievement',
      'message',
      'comment',
      'like',
      'follow',
      'plan_assigned',
      'reminder',
      'system'
    ]
  },
  title: {
    type: String,
    required: [true, 'Notification must have a title'],
    trim: true,
    maxlength: [100, 'Title cannot be more than 100 characters']
  },
  message: {
    type: String,
    required: [true, 'Notification must have a message'],
    trim: true,
    maxlength: [500, 'Message cannot be more than 500 characters']
  },
  isRead: {
    type: Boolean,
    default: false
  },
  data: {
    type: mongoose.Schema.Types.Mixed, // Additional data related to the notification
    default: {}
  },
  sender: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User'
  },
  relatedModel: {
    type: String,
    enum: ['Workout', 'WorkoutPlan', 'Meal', 'Post', 'Comment', 'Message', 'Conversation', null]
  },
  relatedId: {
    type: mongoose.Schema.Types.ObjectId
  },
  priority: {
    type: String,
    enum: ['low', 'medium', 'high'],
    default: 'medium'
  },
  icon: {
    type: String,
    default: 'notification'
  },
  color: {
    type: String,
    default: 'primary'
  },
  expiresAt: {
    type: Date
  },
  createdAt: {
    type: Date,
    default: Date.now
  }
}, {
  toJSON: { virtuals: true },
  toObject: { virtuals: true }
});

// Index for faster queries
notificationSchema.index({ user: 1, createdAt: -1 });
notificationSchema.index({ user: 1, isRead: 1 });
notificationSchema.index({ expiresAt: 1 }, { expireAfterSeconds: 0 }); // TTL index for auto-deletion

// Populate sender field when querying
notificationSchema.pre(/^find/, function(next) {
  this.populate({
    path: 'sender',
    select: 'firstName lastName avatar'
  });
  next();
});

// Static method to create a notification
notificationSchema.statics.createNotification = async function(data) {
  try {
    const notification = await this.create(data);
    return notification;
  } catch (error) {
    console.error('Error creating notification:', error);
    throw error;
  }
};

// Static method to mark all notifications as read for a user
notificationSchema.statics.markAllAsRead = async function(userId) {
  try {
    const result = await this.updateMany(
      { user: userId, isRead: false },
      { isRead: true }
    );
    return result.nModified;
  } catch (error) {
    console.error('Error marking all notifications as read:', error);
    throw error;
  }
};

// Static method to get unread count for a user
notificationSchema.statics.getUnreadCount = async function(userId) {
  try {
    const count = await this.countDocuments({ user: userId, isRead: false });
    return count;
  } catch (error) {
    console.error('Error getting unread notification count:', error);
    throw error;
  }
};

// Static method to delete old notifications
notificationSchema.statics.deleteOldNotifications = async function(userId, days = 30) {
  try {
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - days);
    
    const result = await this.deleteMany({
      user: userId,
      isRead: true,
      createdAt: { $lt: cutoffDate }
    });
    
    return result.deletedCount;
  } catch (error) {
    console.error('Error deleting old notifications:', error);
    throw error;
  }
};

const Notification = mongoose.model('Notification', notificationSchema);

module.exports = Notification;

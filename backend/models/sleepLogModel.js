const mongoose = require('mongoose');

const sleepLogSchema = new mongoose.Schema({
  user: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: [true, 'Sleep log must belong to a user']
  },
  date: {
    type: Date,
    default: Date.now
  },
  startTime: {
    type: Date,
    required: [true, 'Sleep log must have a start time']
  },
  endTime: {
    type: Date,
    required: [true, 'Sleep log must have an end time'],
    validate: {
      validator: function(value) {
        return value > this.startTime;
      },
      message: 'End time must be after start time'
    }
  },
  duration: {
    type: Number, // in minutes
    min: [0, 'Duration cannot be negative']
  },
  quality: {
    type: Number,
    min: [1, 'Quality must be at least 1'],
    max: [5, 'Quality cannot exceed 5']
  },
  interruptions: {
    type: Number,
    default: 0,
    min: [0, 'Interruptions cannot be negative']
  },
  notes: {
    type: String,
    trim: true,
    maxlength: [500, 'Notes cannot be more than 500 characters']
  },
  createdAt: {
    type: Date,
    default: Date.now
  },
  updatedAt: {
    type: Date,
    default: Date.now
  }
}, {
  toJSON: { virtuals: true },
  toObject: { virtuals: true }
});

// Index for faster queries
sleepLogSchema.index({ user: 1, date: -1 });

// Calculate duration before saving
sleepLogSchema.pre('save', function(next) {
  if (this.startTime && this.endTime) {
    // Calculate duration in minutes
    this.duration = Math.round((this.endTime - this.startTime) / (1000 * 60));
  }
  this.updatedAt = Date.now();
  next();
});

// Static method to get weekly summary
sleepLogSchema.statics.getWeeklySummary = async function(userId, endDate = new Date()) {
  // Create start date (7 days before end date)
  const startDate = new Date(endDate);
  startDate.setDate(startDate.getDate() - 6);
  startDate.setHours(0, 0, 0, 0);
  
  const endOfDay = new Date(endDate);
  endOfDay.setHours(23, 59, 59, 999);
  
  const result = await this.aggregate([
    {
      $match: {
        user: mongoose.Types.ObjectId(userId),
        date: {
          $gte: startDate,
          $lte: endOfDay
        }
      }
    },
    {
      $group: {
        _id: { $dateToString: { format: '%Y-%m-%d', date: '$date' } },
        avgDuration: { $avg: '$duration' },
        avgQuality: { $avg: '$quality' },
        count: { $sum: 1 }
      }
    },
    {
      $sort: { _id: 1 }
    }
  ]);
  
  return result;
};

// Static method to get monthly average
sleepLogSchema.statics.getMonthlyAverage = async function(userId, year, month) {
  // Create start and end date for the month
  const startDate = new Date(year, month - 1, 1);
  const endDate = new Date(year, month, 0);
  endDate.setHours(23, 59, 59, 999);
  
  const result = await this.aggregate([
    {
      $match: {
        user: mongoose.Types.ObjectId(userId),
        date: {
          $gte: startDate,
          $lte: endDate
        }
      }
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
  
  return result.length > 0 ? result[0] : { avgDuration: 0, avgQuality: 0, totalSleep: 0, count: 0 };
};

// Populate user field when querying
sleepLogSchema.pre(/^find/, function(next) {
  this.populate({
    path: 'user',
    select: 'firstName lastName'
  });
  next();
});

const SleepLog = mongoose.model('SleepLog', sleepLogSchema);

module.exports = SleepLog;

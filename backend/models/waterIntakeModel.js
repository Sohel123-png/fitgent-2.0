const mongoose = require('mongoose');

const waterIntakeSchema = new mongoose.Schema({
  user: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: [true, 'Water intake must belong to a user']
  },
  date: {
    type: Date,
    default: Date.now
  },
  amount: {
    type: Number, // in ml
    required: [true, 'Water intake must have an amount'],
    min: [0, 'Amount cannot be negative'],
    max: [5000, 'Amount cannot exceed 5000ml at once']
  },
  time: {
    type: Date,
    default: Date.now
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
waterIntakeSchema.index({ user: 1, date: -1 });

// Static method to calculate daily total
waterIntakeSchema.statics.getDailyTotal = async function(userId, date) {
  // Create start and end of the day for the given date
  const startOfDay = new Date(date);
  startOfDay.setHours(0, 0, 0, 0);
  
  const endOfDay = new Date(date);
  endOfDay.setHours(23, 59, 59, 999);
  
  const result = await this.aggregate([
    {
      $match: {
        user: mongoose.Types.ObjectId(userId),
        date: {
          $gte: startOfDay,
          $lte: endOfDay
        }
      }
    },
    {
      $group: {
        _id: null,
        total: { $sum: '$amount' },
        count: { $sum: 1 }
      }
    }
  ]);
  
  return result.length > 0 ? result[0] : { total: 0, count: 0 };
};

// Static method to get weekly summary
waterIntakeSchema.statics.getWeeklySummary = async function(userId, endDate = new Date()) {
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
        total: { $sum: '$amount' },
        count: { $sum: 1 }
      }
    },
    {
      $sort: { _id: 1 }
    }
  ]);
  
  return result;
};

// Populate user field when querying
waterIntakeSchema.pre(/^find/, function(next) {
  this.populate({
    path: 'user',
    select: 'firstName lastName'
  });
  next();
});

const WaterIntake = mongoose.model('WaterIntake', waterIntakeSchema);

module.exports = WaterIntake;

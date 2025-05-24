const mongoose = require('mongoose');

const workoutPlanSchema = new mongoose.Schema({
  name: {
    type: String,
    required: [true, 'A workout plan must have a name'],
    trim: true,
    maxlength: [100, 'A workout plan name cannot be more than 100 characters']
  },
  description: {
    type: String,
    trim: true,
    maxlength: [1000, 'A workout plan description cannot be more than 1000 characters']
  },
  creator: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: [true, 'A workout plan must have a creator']
  },
  duration: {
    type: Number, // in days
    required: [true, 'A workout plan must have a duration'],
    min: [1, 'Duration must be at least 1 day'],
    max: [365, 'Duration cannot exceed 365 days']
  },
  difficulty: {
    type: String,
    required: [true, 'A workout plan must have a difficulty level'],
    enum: {
      values: ['beginner', 'intermediate', 'advanced', 'expert'],
      message: 'Difficulty must be: beginner, intermediate, advanced, or expert'
    }
  },
  goal: {
    type: String,
    required: [true, 'A workout plan must have a goal'],
    enum: {
      values: ['lose_weight', 'gain_muscle', 'improve_fitness', 'maintain', 'other'],
      message: 'Goal must be one of the predefined values'
    }
  },
  schedule: [{
    day: {
      type: Number, // 1-7 for days of the week (1 = Monday)
      required: [true, 'Schedule must have a day'],
      min: [1, 'Day must be at least 1 (Monday)'],
      max: [7, 'Day cannot exceed 7 (Sunday)']
    },
    workouts: [{
      workout: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'Workout',
        required: [true, 'Schedule must include a workout']
      },
      order: {
        type: Number,
        default: 0
      }
    }],
    notes: {
      type: String,
      trim: true
    },
    restDay: {
      type: Boolean,
      default: false
    }
  }],
  tags: [{
    type: String,
    trim: true
  }],
  image: {
    type: String, // URL to workout plan image
    default: 'default-workout-plan.jpg'
  },
  isPublic: {
    type: Boolean,
    default: false
  },
  assignedUsers: [{
    user: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User'
    },
    assignedAt: {
      type: Date,
      default: Date.now
    },
    startDate: {
      type: Date
    },
    endDate: {
      type: Date
    },
    progress: {
      type: Number, // percentage
      default: 0,
      min: [0, 'Progress cannot be negative'],
      max: [100, 'Progress cannot exceed 100%']
    },
    status: {
      type: String,
      enum: ['not_started', 'in_progress', 'completed', 'abandoned'],
      default: 'not_started'
    }
  }],
  rating: {
    type: Number,
    default: 0,
    min: [0, 'Rating must be at least 0'],
    max: [5, 'Rating cannot exceed 5'],
    set: val => Math.round(val * 10) / 10 // Round to 1 decimal place
  },
  reviews: [{
    user: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User'
    },
    rating: {
      type: Number,
      required: [true, 'Review must have a rating'],
      min: [1, 'Rating must be at least 1'],
      max: [5, 'Rating cannot exceed 5']
    },
    comment: {
      type: String,
      trim: true
    },
    createdAt: {
      type: Date,
      default: Date.now
    }
  }],
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
workoutPlanSchema.index({ name: 1 });
workoutPlanSchema.index({ difficulty: 1 });
workoutPlanSchema.index({ goal: 1 });
workoutPlanSchema.index({ creator: 1 });
workoutPlanSchema.index({ isPublic: 1 });

// Update the updatedAt field on save
workoutPlanSchema.pre('save', function(next) {
  this.updatedAt = Date.now();
  next();
});

// Populate creator field when querying
workoutPlanSchema.pre(/^find/, function(next) {
  this.populate({
    path: 'creator',
    select: 'firstName lastName avatar'
  });
  next();
});

// Populate workouts in schedule when querying
workoutPlanSchema.pre(/^find/, function(next) {
  this.populate({
    path: 'schedule.workouts.workout',
    select: 'name duration difficulty category'
  });
  next();
});

// Calculate average rating when a review is added or updated
workoutPlanSchema.statics.calcAverageRating = async function(planId) {
  const stats = await this.aggregate([
    {
      $match: { _id: planId }
    },
    {
      $unwind: '$reviews'
    },
    {
      $group: {
        _id: '$_id',
        nRating: { $sum: 1 },
        avgRating: { $avg: '$reviews.rating' }
      }
    }
  ]);

  if (stats.length > 0) {
    await this.findByIdAndUpdate(planId, {
      rating: stats[0].avgRating
    });
  } else {
    await this.findByIdAndUpdate(planId, {
      rating: 0
    });
  }
};

// Call calcAverageRating after save
workoutPlanSchema.post('save', function() {
  this.constructor.calcAverageRating(this._id);
});

// Call calcAverageRating before findByIdAndUpdate and findByIdAndDelete
workoutPlanSchema.pre(/^findOneAnd/, async function(next) {
  this.r = await this.findOne();
  next();
});

workoutPlanSchema.post(/^findOneAnd/, async function() {
  if (this.r) await this.r.constructor.calcAverageRating(this.r._id);
});

const WorkoutPlan = mongoose.model('WorkoutPlan', workoutPlanSchema);

module.exports = WorkoutPlan;

const mongoose = require('mongoose');

const workoutSchema = new mongoose.Schema({
  name: {
    type: String,
    required: [true, 'A workout must have a name'],
    trim: true,
    maxlength: [100, 'A workout name cannot be more than 100 characters']
  },
  description: {
    type: String,
    trim: true,
    maxlength: [1000, 'A workout description cannot be more than 1000 characters']
  },
  difficulty: {
    type: String,
    required: [true, 'A workout must have a difficulty level'],
    enum: {
      values: ['beginner', 'intermediate', 'advanced', 'expert'],
      message: 'Difficulty must be: beginner, intermediate, advanced, or expert'
    }
  },
  category: {
    type: String,
    required: [true, 'A workout must have a category'],
    enum: {
      values: ['strength', 'cardio', 'flexibility', 'balance', 'hiit', 'yoga', 'pilates', 'crossfit', 'bodyweight', 'other'],
      message: 'Category must be one of the predefined values'
    }
  },
  duration: {
    type: Number, // in minutes
    required: [true, 'A workout must have a duration'],
    min: [1, 'Duration must be at least 1 minute'],
    max: [300, 'Duration cannot exceed 300 minutes']
  },
  caloriesBurn: {
    type: Number, // estimated calories
    min: [0, 'Calories burn cannot be negative']
  },
  creator: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: [true, 'A workout must have a creator']
  },
  exercises: [{
    name: {
      type: String,
      required: [true, 'An exercise must have a name'],
      trim: true
    },
    sets: {
      type: Number,
      min: [1, 'Sets must be at least 1']
    },
    reps: {
      type: Number,
      min: [1, 'Reps must be at least 1']
    },
    duration: {
      type: Number, // in seconds
      min: [0, 'Duration cannot be negative']
    },
    restTime: {
      type: Number, // in seconds
      min: [0, 'Rest time cannot be negative']
    },
    videoUrl: {
      type: String,
      validate: {
        validator: function(v) {
          // Simple URL validation
          return /^(https?:\/\/)?([\da-z.-]+)\.([a-z.]{2,6})([/\w .-]*)*\/?$/.test(v);
        },
        message: props => `${props.value} is not a valid URL!`
      }
    },
    instructions: {
      type: String,
      trim: true
    },
    equipment: {
      type: String,
      enum: ['none', 'dumbbells', 'barbell', 'kettlebell', 'resistance_bands', 'machine', 'bodyweight', 'other']
    },
    targetMuscle: {
      type: String,
      enum: ['chest', 'back', 'shoulders', 'biceps', 'triceps', 'legs', 'core', 'full_body', 'other']
    }
  }],
  tags: [{
    type: String,
    trim: true
  }],
  equipment: [{
    type: String,
    enum: ['none', 'dumbbells', 'barbell', 'kettlebell', 'resistance_bands', 'machine', 'bodyweight', 'other']
  }],
  targetMuscles: [{
    type: String,
    enum: ['chest', 'back', 'shoulders', 'biceps', 'triceps', 'legs', 'core', 'full_body', 'other']
  }],
  image: {
    type: String, // URL to workout image
    default: 'default-workout.jpg'
  },
  isPublic: {
    type: Boolean,
    default: true
  },
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
workoutSchema.index({ name: 1 });
workoutSchema.index({ difficulty: 1 });
workoutSchema.index({ category: 1 });
workoutSchema.index({ creator: 1 });
workoutSchema.index({ isPublic: 1 });

// Update the updatedAt field on save
workoutSchema.pre('save', function(next) {
  this.updatedAt = Date.now();
  next();
});

// Populate creator field when querying
workoutSchema.pre(/^find/, function(next) {
  this.populate({
    path: 'creator',
    select: 'firstName lastName avatar'
  });
  next();
});

// Calculate average rating when a review is added or updated
workoutSchema.statics.calcAverageRating = async function(workoutId) {
  const stats = await this.aggregate([
    {
      $match: { _id: workoutId }
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
    await this.findByIdAndUpdate(workoutId, {
      rating: stats[0].avgRating
    });
  } else {
    await this.findByIdAndUpdate(workoutId, {
      rating: 0
    });
  }
};

// Call calcAverageRating after save
workoutSchema.post('save', function() {
  this.constructor.calcAverageRating(this._id);
});

// Call calcAverageRating before findByIdAndUpdate and findByIdAndDelete
workoutSchema.pre(/^findOneAnd/, async function(next) {
  this.r = await this.findOne();
  next();
});

workoutSchema.post(/^findOneAnd/, async function() {
  if (this.r) await this.r.constructor.calcAverageRating(this.r._id);
});

const Workout = mongoose.model('Workout', workoutSchema);

module.exports = Workout;

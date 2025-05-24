const mongoose = require('mongoose');

const trainerSchema = new mongoose.Schema({
  user: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: [true, 'Trainer must be associated with a user']
  },
  specialization: [{
    type: String,
    enum: [
      'weight_loss',
      'muscle_gain',
      'strength_training',
      'cardio',
      'yoga',
      'pilates',
      'crossfit',
      'bodybuilding',
      'functional_training',
      'sports_specific',
      'rehabilitation',
      'nutrition',
      'senior_fitness',
      'prenatal_fitness',
      'other'
    ]
  }],
  experience: {
    type: Number, // in years
    required: [true, 'Please provide years of experience'],
    min: [0, 'Experience cannot be negative'],
    max: [70, 'Experience cannot exceed 70 years']
  },
  certification: [{
    name: {
      type: String,
      required: [true, 'Please provide certification name']
    },
    issuer: {
      type: String,
      required: [true, 'Please provide certification issuer']
    },
    year: {
      type: Number,
      required: [true, 'Please provide certification year']
    },
    document: {
      type: String // URL to certification document
    },
    verified: {
      type: Boolean,
      default: false
    }
  }],
  isApproved: {
    type: Boolean,
    default: false
  },
  clients: [{
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User'
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
      trim: true,
      maxlength: [500, 'Review cannot be more than 500 characters']
    },
    createdAt: {
      type: Date,
      default: Date.now
    }
  }],
  bio: {
    type: String,
    trim: true,
    maxlength: [1000, 'Bio cannot be more than 1000 characters']
  },
  hourlyRate: {
    type: Number,
    min: [0, 'Hourly rate cannot be negative']
  },
  availability: [{
    day: {
      type: Number, // 0-6 for days of the week (0 = Sunday)
      required: [true, 'Please provide day of the week']
    },
    startTime: {
      type: String, // Format: "HH:MM" in 24-hour format
      required: [true, 'Please provide start time']
    },
    endTime: {
      type: String, // Format: "HH:MM" in 24-hour format
      required: [true, 'Please provide end time']
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

// Update the updatedAt field on save
trainerSchema.pre('save', function(next) {
  this.updatedAt = Date.now();
  next();
});

// Populate user field when querying
trainerSchema.pre(/^find/, function(next) {
  this.populate({
    path: 'user',
    select: 'firstName lastName email avatar'
  });
  next();
});

// Calculate average rating when a review is added or updated
trainerSchema.statics.calcAverageRating = async function(trainerId) {
  const stats = await this.aggregate([
    {
      $match: { _id: trainerId }
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
    await this.findByIdAndUpdate(trainerId, {
      rating: stats[0].avgRating
    });
  } else {
    await this.findByIdAndUpdate(trainerId, {
      rating: 0
    });
  }
};

// Call calcAverageRating after save
trainerSchema.post('save', function() {
  this.constructor.calcAverageRating(this._id);
});

// Call calcAverageRating before findByIdAndUpdate and findByIdAndDelete
trainerSchema.pre(/^findOneAnd/, async function(next) {
  this.r = await this.findOne();
  next();
});

trainerSchema.post(/^findOneAnd/, async function() {
  if (this.r) await this.r.constructor.calcAverageRating(this.r._id);
});

const Trainer = mongoose.model('Trainer', trainerSchema);

module.exports = Trainer;

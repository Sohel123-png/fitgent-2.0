const mongoose = require('mongoose');

const postSchema = new mongoose.Schema({
  user: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: [true, 'Post must belong to a user']
  },
  content: {
    type: String,
    required: [true, 'Post must have content'],
    trim: true,
    maxlength: [2000, 'Post content cannot be more than 2000 characters']
  },
  images: [{
    type: String // URLs to images
  }],
  likes: [{
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User'
  }],
  comments: [{
    user: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User',
      required: [true, 'Comment must belong to a user']
    },
    content: {
      type: String,
      required: [true, 'Comment must have content'],
      trim: true,
      maxlength: [500, 'Comment cannot be more than 500 characters']
    },
    createdAt: {
      type: Date,
      default: Date.now
    }
  }],
  tags: [{
    type: String,
    trim: true
  }],
  workout: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Workout'
  },
  meal: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Meal'
  },
  achievement: {
    type: String,
    enum: [
      'weight_goal',
      'workout_streak',
      'first_workout',
      'nutrition_goal',
      'water_goal',
      'sleep_goal',
      'steps_goal',
      'custom'
    ]
  },
  isModerated: {
    type: Boolean,
    default: false
  },
  moderationStatus: {
    type: String,
    enum: ['pending', 'approved', 'rejected'],
    default: 'pending'
  },
  moderationReason: {
    type: String,
    trim: true
  },
  visibility: {
    type: String,
    enum: ['public', 'friends', 'private'],
    default: 'public'
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
postSchema.index({ user: 1, createdAt: -1 });
postSchema.index({ tags: 1 });
postSchema.index({ visibility: 1 });

// Virtual property for like count
postSchema.virtual('likeCount').get(function() {
  return this.likes ? this.likes.length : 0;
});

// Virtual property for comment count
postSchema.virtual('commentCount').get(function() {
  return this.comments ? this.comments.length : 0;
});

// Update the updatedAt field on save
postSchema.pre('save', function(next) {
  this.updatedAt = Date.now();
  next();
});

// Populate user field when querying
postSchema.pre(/^find/, function(next) {
  this.populate({
    path: 'user',
    select: 'firstName lastName avatar'
  });
  next();
});

// Populate workout field when querying if it exists
postSchema.pre(/^find/, function(next) {
  this.populate({
    path: 'workout',
    select: 'name difficulty duration'
  });
  next();
});

// Populate meal field when querying if it exists
postSchema.pre(/^find/, function(next) {
  this.populate({
    path: 'meal',
    select: 'name type totalCalories'
  });
  next();
});

// Populate comment user fields when querying
postSchema.pre(/^find/, function(next) {
  this.populate({
    path: 'comments.user',
    select: 'firstName lastName avatar'
  });
  next();
});

const Post = mongoose.model('Post', postSchema);

module.exports = Post;

const mongoose = require('mongoose');

const mealSchema = new mongoose.Schema({
  user: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: [true, 'A meal must belong to a user']
  },
  date: {
    type: Date,
    default: Date.now
  },
  type: {
    type: String,
    required: [true, 'A meal must have a type'],
    enum: {
      values: ['breakfast', 'lunch', 'dinner', 'snack'],
      message: 'Meal type must be: breakfast, lunch, dinner, or snack'
    }
  },
  name: {
    type: String,
    required: [true, 'A meal must have a name'],
    trim: true,
    maxlength: [100, 'A meal name cannot be more than 100 characters']
  },
  foods: [{
    name: {
      type: String,
      required: [true, 'A food must have a name'],
      trim: true
    },
    quantity: {
      type: Number,
      required: [true, 'A food must have a quantity'],
      min: [0, 'Quantity cannot be negative']
    },
    unit: {
      type: String,
      required: [true, 'A food must have a unit'],
      enum: {
        values: ['g', 'ml', 'oz', 'lb', 'cup', 'tbsp', 'tsp', 'piece', 'serving'],
        message: 'Unit must be one of the predefined values'
      }
    },
    calories: {
      type: Number,
      min: [0, 'Calories cannot be negative']
    },
    protein: {
      type: Number, // in grams
      min: [0, 'Protein cannot be negative']
    },
    carbs: {
      type: Number, // in grams
      min: [0, 'Carbs cannot be negative']
    },
    fat: {
      type: Number, // in grams
      min: [0, 'Fat cannot be negative']
    },
    fiber: {
      type: Number, // in grams
      min: [0, 'Fiber cannot be negative']
    },
    sugar: {
      type: Number, // in grams
      min: [0, 'Sugar cannot be negative']
    },
    sodium: {
      type: Number, // in mg
      min: [0, 'Sodium cannot be negative']
    }
  }],
  totalCalories: {
    type: Number,
    min: [0, 'Total calories cannot be negative']
  },
  totalProtein: {
    type: Number,
    min: [0, 'Total protein cannot be negative']
  },
  totalCarbs: {
    type: Number,
    min: [0, 'Total carbs cannot be negative']
  },
  totalFat: {
    type: Number,
    min: [0, 'Total fat cannot be negative']
  },
  totalFiber: {
    type: Number,
    min: [0, 'Total fiber cannot be negative']
  },
  totalSugar: {
    type: Number,
    min: [0, 'Total sugar cannot be negative']
  },
  totalSodium: {
    type: Number,
    min: [0, 'Total sodium cannot be negative']
  },
  image: {
    type: String // URL to meal image
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
mealSchema.index({ user: 1, date: -1 });
mealSchema.index({ user: 1, type: 1 });

// Update the updatedAt field on save
mealSchema.pre('save', function(next) {
  this.updatedAt = Date.now();
  next();
});

// Calculate total nutrition values before saving
mealSchema.pre('save', function(next) {
  if (this.foods && this.foods.length > 0) {
    this.totalCalories = this.foods.reduce((sum, food) => sum + (food.calories || 0), 0);
    this.totalProtein = this.foods.reduce((sum, food) => sum + (food.protein || 0), 0);
    this.totalCarbs = this.foods.reduce((sum, food) => sum + (food.carbs || 0), 0);
    this.totalFat = this.foods.reduce((sum, food) => sum + (food.fat || 0), 0);
    this.totalFiber = this.foods.reduce((sum, food) => sum + (food.fiber || 0), 0);
    this.totalSugar = this.foods.reduce((sum, food) => sum + (food.sugar || 0), 0);
    this.totalSodium = this.foods.reduce((sum, food) => sum + (food.sodium || 0), 0);
  }
  next();
});

// Populate user field when querying
mealSchema.pre(/^find/, function(next) {
  this.populate({
    path: 'user',
    select: 'firstName lastName'
  });
  next();
});

const Meal = mongoose.model('Meal', mealSchema);

module.exports = Meal;

const express = require('express');
const workoutController = require('../controllers/workoutController');
const { protect, restrictTo } = require('../middleware/authMiddleware');
const upload = require('../middleware/uploadMiddleware');

const router = express.Router();

// Protect all routes
router.use(protect);

// Get recommended workouts
router.get('/recommended', workoutController.getRecommendedWorkouts);

// Get all workouts
router.get('/', workoutController.getAllWorkouts);

// Create workout (trainer/admin only)
router.post(
  '/',
  restrictTo('trainer', 'admin'),
  workoutController.createWorkout
);

// Get workout by ID
router.get('/:id', workoutController.getWorkout);

// Update workout (trainer/admin only)
router.put(
  '/:id',
  restrictTo('trainer', 'admin'),
  workoutController.updateWorkout
);

// Delete workout (trainer/admin only)
router.delete(
  '/:id',
  restrictTo('trainer', 'admin'),
  workoutController.deleteWorkout
);

// Upload workout image
router.put(
  '/:id/image',
  restrictTo('trainer', 'admin'),
  upload.single('image'),
  workoutController.uploadWorkoutImage
);

// Add review to workout
router.post('/:id/review', workoutController.addWorkoutReview);

module.exports = router;

const express = require('express');
const workoutPlanController = require('../controllers/workoutPlanController');
const { protect, restrictTo } = require('../middleware/authMiddleware');
const upload = require('../middleware/uploadMiddleware');

const router = express.Router();

// Protect all routes
router.use(protect);

// Get all workout plans
router.get('/', workoutPlanController.getAllWorkoutPlans);

// Create workout plan (trainer/admin only)
router.post(
  '/',
  restrictTo('trainer', 'admin'),
  workoutPlanController.createWorkoutPlan
);

// Get workout plans assigned to user
router.get('/assigned', workoutPlanController.getAssignedWorkoutPlans);
router.get('/assigned/:userId', workoutPlanController.getAssignedWorkoutPlans);

// Get workout plan by ID
router.get('/:id', workoutPlanController.getWorkoutPlan);

// Update workout plan (trainer/admin only)
router.put(
  '/:id',
  restrictTo('trainer', 'admin'),
  workoutPlanController.updateWorkoutPlan
);

// Delete workout plan (trainer/admin only)
router.delete(
  '/:id',
  restrictTo('trainer', 'admin'),
  workoutPlanController.deleteWorkoutPlan
);

// Upload workout plan image
router.put(
  '/:id/image',
  restrictTo('trainer', 'admin'),
  upload.single('image'),
  workoutPlanController.uploadWorkoutPlanImage
);

// Assign workout plan to users
router.post(
  '/:id/assign',
  restrictTo('trainer', 'admin'),
  workoutPlanController.assignWorkoutPlan
);

module.exports = router;

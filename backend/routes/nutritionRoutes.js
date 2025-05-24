const express = require('express');
const nutritionController = require('../controllers/nutritionController');
const { protect } = require('../middleware/authMiddleware');
const upload = require('../middleware/uploadMiddleware');

const router = express.Router();

// Protect all routes
router.use(protect);

// Get nutrition stats
router.get('/stats', nutritionController.getNutritionStats);

// Get user meals
router.get('/meals', nutritionController.getUserMeals);

// Create meal
router.post('/meals', nutritionController.createMeal);

// Get meal by ID
router.get('/meals/:id', nutritionController.getMeal);

// Update meal
router.put('/meals/:id', nutritionController.updateMeal);

// Delete meal
router.delete('/meals/:id', nutritionController.deleteMeal);

// Upload meal image
router.put(
  '/meals/:id/image',
  upload.single('image'),
  nutritionController.uploadMealImage
);

module.exports = router;

const express = require('express');
const chatbotController = require('../controllers/chatbotController');
const { protect } = require('../middleware/authMiddleware');

const router = express.Router();

// Protect all routes
router.use(protect);

// Send message to AI chatbot
router.post('/message', chatbotController.sendMessage);

// Get workout recommendation
router.post('/workout-recommendation', chatbotController.getWorkoutRecommendation);

// Get meal recommendation
router.post('/meal-recommendation', chatbotController.getMealRecommendation);

module.exports = router;

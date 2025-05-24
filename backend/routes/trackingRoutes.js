const express = require('express');
const trackingController = require('../controllers/trackingController');
const { protect } = require('../middleware/authMiddleware');

const router = express.Router();

// Protect all routes
router.use(protect);

// Get tracking stats (combined)
router.get('/stats', trackingController.getTrackingStats);

// Water intake routes
router.get('/water', trackingController.getWaterIntake);
router.post('/water', trackingController.addWaterIntake);
router.get('/water/stats', trackingController.getWaterIntakeStats);

// Sleep routes
router.get('/sleep', trackingController.getSleepLogs);
router.post('/sleep', trackingController.addSleepLog);
router.get('/sleep/stats', trackingController.getSleepStats);

module.exports = router;

const express = require('express');
const adminController = require('../controllers/adminController');
const { protect, restrictTo } = require('../middleware/authMiddleware');

const router = express.Router();

// Protect all routes and restrict to admin
router.use(protect);
router.use(restrictTo('admin'));

// Get platform stats
router.get('/stats', adminController.getPlatformStats);

// Get trainer applications
router.get('/trainer-applications', adminController.getTrainerApplications);

// Approve/reject trainer application
router.put('/trainer-applications/:id', adminController.processTrainerApplication);

// Get content for moderation
router.get('/content-moderation', adminController.getContentForModeration);

// Moderate content
router.put('/content-moderation/:id', adminController.moderateContent);

// Manage user roles
router.put('/users/:id/role', adminController.manageUserRole);

// Get user activity logs
router.get('/users/:id/activity', adminController.getUserActivityLogs);

module.exports = router;

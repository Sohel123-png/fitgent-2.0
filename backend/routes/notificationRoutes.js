const express = require('express');
const notificationController = require('../controllers/notificationController');
const { protect, restrictTo } = require('../middleware/authMiddleware');

const router = express.Router();

// Protect all routes
router.use(protect);

// Get user notifications
router.get('/', notificationController.getUserNotifications);

// Get notification count
router.get('/count', notificationController.getNotificationCount);

// Mark all notifications as read
router.put('/read-all', notificationController.markAllNotificationsAsRead);

// Delete all read notifications
router.delete('/read', notificationController.deleteAllReadNotifications);

// Mark notification as read
router.put('/:id/read', notificationController.markNotificationAsRead);

// Delete notification
router.delete('/:id', notificationController.deleteNotification);

// Create notification (for testing or admin)
router.post(
  '/',
  restrictTo('admin'),
  notificationController.createNotification
);

module.exports = router;

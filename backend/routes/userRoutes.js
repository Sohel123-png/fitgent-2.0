const express = require('express');
const userController = require('../controllers/userController');
const { protect, restrictTo } = require('../middleware/authMiddleware');
const upload = require('../middleware/uploadMiddleware');

const router = express.Router();

// Protect all routes
router.use(protect);

// Get user progress
router.get('/:id/progress', userController.getUserProgress);

// Update user avatar
router.put('/:id/avatar', upload.single('avatar'), userController.updateAvatar);

// Get user by ID
router.get('/:id', userController.getUser);

// Update user
router.put('/:id', userController.updateUser);

// Admin only routes
router.use(restrictTo('admin'));

// Get all users
router.get('/', userController.getAllUsers);

// Delete user
router.delete('/:id', userController.deleteUser);

module.exports = router;

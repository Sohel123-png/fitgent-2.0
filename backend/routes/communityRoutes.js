const express = require('express');
const communityController = require('../controllers/communityController');
const { protect } = require('../middleware/authMiddleware');
const upload = require('../middleware/uploadMiddleware');

const router = express.Router();

// Protect all routes
router.use(protect);

// Get community feed
router.get('/feed', communityController.getCommunityFeed);

// Get leaderboard
router.get('/leaderboard', communityController.getLeaderboard);

// Create post
router.post('/posts', communityController.createPost);

// Get post by ID
router.get('/posts/:id', communityController.getPost);

// Update post
router.put('/posts/:id', communityController.updatePost);

// Delete post
router.delete('/posts/:id', communityController.deletePost);

// Like post
router.post('/posts/:id/like', communityController.likePost);

// Comment on post
router.post('/posts/:id/comment', communityController.commentOnPost);

// Upload post images
router.put(
  '/posts/:id/images',
  upload.array('images', 5),
  communityController.uploadPostImages
);

module.exports = router;

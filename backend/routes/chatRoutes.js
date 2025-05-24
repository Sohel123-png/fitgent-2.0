const express = require('express');
const chatController = require('../controllers/chatController');
const { protect } = require('../middleware/authMiddleware');

const router = express.Router();

// Protect all routes
router.use(protect);

// Get user conversations
router.get('/conversations', chatController.getUserConversations);

// Create a new conversation
router.post('/conversations', chatController.createConversation);

// Get conversation by ID
router.get('/conversations/:id', chatController.getConversation);

// Get messages in conversation
router.get('/conversations/:id/messages', chatController.getConversationMessages);

// Send a message
router.post('/conversations/:id/messages', chatController.sendMessage);

// Mark conversation as read
router.put('/conversations/:id/read', chatController.markConversationAsRead);

// Add participants to group conversation
router.post('/conversations/:id/participants', chatController.addParticipants);

module.exports = router;

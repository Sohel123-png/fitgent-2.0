const Conversation = require('../models/conversationModel');
const Message = require('../models/messageModel');
const User = require('../models/userModel');
const Notification = require('../models/notificationModel');
const AppError = require('../utils/appError');

// Get user conversations
exports.getUserConversations = async (req, res, next) => {
  try {
    // Find conversations where user is a participant
    const conversations = await Conversation.find({
      participants: req.user.id
    }).sort('-updatedAt');
    
    res.status(200).json({
      status: 'success',
      results: conversations.length,
      data: {
        conversations
      }
    });
  } catch (error) {
    next(error);
  }
};

// Get conversation by ID
exports.getConversation = async (req, res, next) => {
  try {
    const conversation = await Conversation.findById(req.params.id);
    
    if (!conversation) {
      return next(new AppError('No conversation found with that ID', 404));
    }
    
    // Check if user is a participant
    if (!conversation.participants.some(p => p.id === req.user.id)) {
      return next(new AppError('You are not a participant in this conversation', 403));
    }
    
    res.status(200).json({
      status: 'success',
      data: {
        conversation
      }
    });
  } catch (error) {
    next(error);
  }
};

// Create a new conversation
exports.createConversation = async (req, res, next) => {
  try {
    const { participants, type, name } = req.body;
    
    if (!participants || !Array.isArray(participants) || participants.length === 0) {
      return next(new AppError('Please provide at least one participant', 400));
    }
    
    // Add current user to participants if not already included
    if (!participants.includes(req.user.id)) {
      participants.push(req.user.id);
    }
    
    // Check if it's a private conversation between two users
    if (participants.length === 2 && (!type || type === 'private')) {
      // Check if conversation already exists
      const existingConversation = await Conversation.getOrCreatePrivateConversation(
        participants[0],
        participants[1]
      );
      
      return res.status(200).json({
        status: 'success',
        data: {
          conversation: existingConversation
        }
      });
    }
    
    // Create a new group conversation
    if (!name && type === 'group') {
      return next(new AppError('Please provide a name for the group conversation', 400));
    }
    
    // Initialize unreadCount for all participants
    const unreadCount = {};
    participants.forEach(participant => {
      unreadCount[participant] = 0;
    });
    
    // Create new conversation
    const newConversation = await Conversation.create({
      participants,
      type: type || 'private',
      name,
      admin: req.user.id,
      unreadCount
    });
    
    res.status(201).json({
      status: 'success',
      data: {
        conversation: newConversation
      }
    });
  } catch (error) {
    next(error);
  }
};

// Get messages in conversation
exports.getConversationMessages = async (req, res, next) => {
  try {
    const conversation = await Conversation.findById(req.params.id);
    
    if (!conversation) {
      return next(new AppError('No conversation found with that ID', 404));
    }
    
    // Check if user is a participant
    if (!conversation.participants.some(p => p.id === req.user.id)) {
      return next(new AppError('You are not a participant in this conversation', 403));
    }
    
    // Build query
    const queryObj = { ...req.query };
    queryObj.conversation = req.params.id;
    
    const excludedFields = ['page', 'sort', 'limit', 'fields'];
    excludedFields.forEach(el => delete queryObj[el]);
    
    // Advanced filtering
    let queryStr = JSON.stringify(queryObj);
    queryStr = queryStr.replace(/\b(gte|gt|lte|lt)\b/g, match => `$${match}`);
    
    // Find messages
    let query = Message.find(JSON.parse(queryStr));
    
    // Sorting
    if (req.query.sort) {
      const sortBy = req.query.sort.split(',').join(' ');
      query = query.sort(sortBy);
    } else {
      query = query.sort('-createdAt');
    }
    
    // Pagination
    const page = parseInt(req.query.page, 10) || 1;
    const limit = parseInt(req.query.limit, 10) || 50;
    const skip = (page - 1) * limit;
    
    query = query.skip(skip).limit(limit);
    
    // Execute query
    const messages = await query;
    
    // Mark messages as read
    await Message.markAsRead(req.params.id, req.user.id);
    
    res.status(200).json({
      status: 'success',
      results: messages.length,
      data: {
        messages
      }
    });
  } catch (error) {
    next(error);
  }
};

// Send a message
exports.sendMessage = async (req, res, next) => {
  try {
    const { content, contentType = 'text' } = req.body;
    
    if (!content) {
      return next(new AppError('Please provide message content', 400));
    }
    
    const conversation = await Conversation.findById(req.params.id);
    
    if (!conversation) {
      return next(new AppError('No conversation found with that ID', 404));
    }
    
    // Check if user is a participant
    if (!conversation.participants.some(p => p.id === req.user.id)) {
      return next(new AppError('You are not a participant in this conversation', 403));
    }
    
    // Create message
    const newMessage = await Message.create({
      conversation: req.params.id,
      sender: req.user.id,
      content,
      contentType,
      readBy: [{ user: req.user.id }]
    });
    
    // Create notifications for other participants
    const otherParticipants = conversation.participants.filter(
      p => p.id !== req.user.id
    );
    
    const notifications = otherParticipants.map(participant => ({
      user: participant._id,
      type: 'message',
      title: 'New Message',
      message: `${req.user.firstName} ${req.user.lastName}: ${content.substring(0, 50)}${content.length > 50 ? '...' : ''}`,
      sender: req.user.id,
      relatedModel: 'Conversation',
      relatedId: conversation._id,
      data: {
        conversationId: conversation._id,
        messageId: newMessage._id
      }
    }));
    
    await Notification.insertMany(notifications);
    
    res.status(201).json({
      status: 'success',
      data: {
        message: newMessage
      }
    });
  } catch (error) {
    next(error);
  }
};

// Mark conversation as read
exports.markConversationAsRead = async (req, res, next) => {
  try {
    const conversation = await Conversation.findById(req.params.id);
    
    if (!conversation) {
      return next(new AppError('No conversation found with that ID', 404));
    }
    
    // Check if user is a participant
    if (!conversation.participants.some(p => p.id === req.user.id)) {
      return next(new AppError('You are not a participant in this conversation', 403));
    }
    
    // Mark messages as read
    const markedCount = await Message.markAsRead(req.params.id, req.user.id);
    
    res.status(200).json({
      status: 'success',
      data: {
        markedCount
      }
    });
  } catch (error) {
    next(error);
  }
};

// Add participants to group conversation
exports.addParticipants = async (req, res, next) => {
  try {
    const { participants } = req.body;
    
    if (!participants || !Array.isArray(participants) || participants.length === 0) {
      return next(new AppError('Please provide at least one participant', 400));
    }
    
    const conversation = await Conversation.findById(req.params.id);
    
    if (!conversation) {
      return next(new AppError('No conversation found with that ID', 404));
    }
    
    // Check if conversation is a group
    if (conversation.type !== 'group') {
      return next(new AppError('Cannot add participants to a private conversation', 400));
    }
    
    // Check if user is admin
    if (conversation.admin.toString() !== req.user.id && req.user.role !== 'admin') {
      return next(new AppError('Only the group admin can add participants', 403));
    }
    
    // Add new participants
    for (const participantId of participants) {
      // Check if user exists
      const user = await User.findById(participantId);
      
      if (!user) {
        return next(new AppError(`No user found with ID: ${participantId}`, 404));
      }
      
      // Check if user is already a participant
      if (conversation.participants.some(p => p.id === participantId)) {
        continue;
      }
      
      // Add participant
      conversation.participants.push(participantId);
      conversation.unreadCount.set(participantId, 0);
      
      // Create notification for new participant
      await Notification.createNotification({
        user: participantId,
        type: 'system',
        title: 'Added to Group Conversation',
        message: `You have been added to the group "${conversation.name}" by ${req.user.firstName} ${req.user.lastName}`,
        sender: req.user.id,
        relatedModel: 'Conversation',
        relatedId: conversation._id
      });
    }
    
    await conversation.save();
    
    res.status(200).json({
      status: 'success',
      data: {
        conversation
      }
    });
  } catch (error) {
    next(error);
  }
};

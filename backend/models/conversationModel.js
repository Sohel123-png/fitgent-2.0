const mongoose = require('mongoose');

const conversationSchema = new mongoose.Schema({
  participants: [{
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: [true, 'Conversation must have participants']
  }],
  lastMessage: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Message'
  },
  type: {
    type: String,
    enum: ['private', 'group'],
    default: 'private'
  },
  name: {
    type: String, // Only for group conversations
    trim: true
  },
  image: {
    type: String // Only for group conversations
  },
  admin: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User'
  },
  unreadCount: {
    type: Map,
    of: Number,
    default: {}
  },
  createdAt: {
    type: Date,
    default: Date.now
  },
  updatedAt: {
    type: Date,
    default: Date.now
  }
}, {
  toJSON: { virtuals: true },
  toObject: { virtuals: true }
});

// Index for faster queries
conversationSchema.index({ participants: 1 });
conversationSchema.index({ updatedAt: -1 });

// Update the updatedAt field on save
conversationSchema.pre('save', function(next) {
  this.updatedAt = Date.now();
  next();
});

// Populate participants field when querying
conversationSchema.pre(/^find/, function(next) {
  this.populate({
    path: 'participants',
    select: 'firstName lastName avatar'
  });
  next();
});

// Populate lastMessage field when querying
conversationSchema.pre(/^find/, function(next) {
  this.populate({
    path: 'lastMessage'
  });
  next();
});

// Static method to get or create a conversation between two users
conversationSchema.statics.getOrCreatePrivateConversation = async function(userId1, userId2) {
  // Check if conversation already exists
  const existingConversation = await this.findOne({
    type: 'private',
    participants: { $all: [userId1, userId2], $size: 2 }
  });
  
  if (existingConversation) {
    return existingConversation;
  }
  
  // Create new conversation
  const newConversation = await this.create({
    participants: [userId1, userId2],
    type: 'private',
    unreadCount: {
      [userId1.toString()]: 0,
      [userId2.toString()]: 0
    }
  });
  
  return newConversation;
};

// Static method to create a group conversation
conversationSchema.statics.createGroupConversation = async function(name, admin, participants) {
  // Ensure admin is included in participants
  if (!participants.includes(admin.toString())) {
    participants.push(admin);
  }
  
  // Initialize unreadCount for all participants
  const unreadCount = {};
  participants.forEach(participant => {
    unreadCount[participant.toString()] = 0;
  });
  
  // Create new group conversation
  const newConversation = await this.create({
    name,
    admin,
    participants,
    type: 'group',
    unreadCount
  });
  
  return newConversation;
};

const Conversation = mongoose.model('Conversation', conversationSchema);

module.exports = Conversation;

const mongoose = require('mongoose');
const Conversation = require('./conversationModel');

const messageSchema = new mongoose.Schema({
  conversation: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Conversation',
    required: [true, 'Message must belong to a conversation']
  },
  sender: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: [true, 'Message must have a sender']
  },
  content: {
    type: String,
    required: [true, 'Message must have content'],
    trim: true,
    maxlength: [5000, 'Message cannot be more than 5000 characters']
  },
  contentType: {
    type: String,
    enum: ['text', 'image', 'video', 'audio', 'file'],
    default: 'text'
  },
  fileUrl: {
    type: String // URL to file if contentType is not text
  },
  fileName: {
    type: String // Original file name if contentType is not text
  },
  fileSize: {
    type: Number // File size in bytes if contentType is not text
  },
  readBy: [{
    user: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User'
    },
    readAt: {
      type: Date,
      default: Date.now
    }
  }],
  isDeleted: {
    type: Boolean,
    default: false
  },
  deletedAt: {
    type: Date
  },
  createdAt: {
    type: Date,
    default: Date.now
  }
}, {
  toJSON: { virtuals: true },
  toObject: { virtuals: true }
});

// Index for faster queries
messageSchema.index({ conversation: 1, createdAt: -1 });
messageSchema.index({ sender: 1 });

// Virtual property to check if message is read
messageSchema.virtual('isRead').get(function() {
  return this.readBy && this.readBy.length > 0;
});

// Populate sender field when querying
messageSchema.pre(/^find/, function(next) {
  this.populate({
    path: 'sender',
    select: 'firstName lastName avatar'
  });
  next();
});

// Update conversation's lastMessage and unreadCount after saving a new message
messageSchema.post('save', async function() {
  try {
    const conversation = await Conversation.findById(this.conversation);
    
    if (!conversation) return;
    
    // Update lastMessage
    conversation.lastMessage = this._id;
    
    // Update unreadCount for all participants except the sender
    conversation.participants.forEach(participant => {
      if (participant._id.toString() !== this.sender.toString()) {
        const currentCount = conversation.unreadCount.get(participant._id.toString()) || 0;
        conversation.unreadCount.set(participant._id.toString(), currentCount + 1);
      }
    });
    
    // Update conversation updatedAt
    conversation.updatedAt = Date.now();
    
    await conversation.save();
  } catch (error) {
    console.error('Error updating conversation after message save:', error);
  }
});

// Static method to mark messages as read
messageSchema.statics.markAsRead = async function(conversationId, userId) {
  try {
    // Find all unread messages in the conversation
    const messages = await this.find({
      conversation: conversationId,
      sender: { $ne: userId },
      'readBy.user': { $ne: userId }
    });
    
    // Mark each message as read
    const updatePromises = messages.map(message => {
      message.readBy.push({
        user: userId,
        readAt: Date.now()
      });
      return message.save();
    });
    
    await Promise.all(updatePromises);
    
    // Reset unread count for this user in the conversation
    await Conversation.findByIdAndUpdate(conversationId, {
      $set: { [`unreadCount.${userId}`]: 0 }
    });
    
    return messages.length;
  } catch (error) {
    console.error('Error marking messages as read:', error);
    throw error;
  }
};

const Message = mongoose.model('Message', messageSchema);

module.exports = Message;

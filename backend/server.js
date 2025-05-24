const app = require('./app');
const mongoose = require('mongoose');
const config = require('./config/config');

// Connect to MongoDB
mongoose.connect(config.mongoURI)
  .then(() => {
    console.log('Connected to MongoDB');
    
    // Start the server
    const PORT = config.port || 5000;
    const server = app.listen(PORT, () => {
      console.log(`Server running on port ${PORT}`);
    });

    // Socket.io setup
    const io = require('socket.io')(server, {
      cors: {
        origin: config.clientURL,
        methods: ['GET', 'POST'],
        credentials: true
      }
    });

    // Socket.io connection handler
    io.on('connection', (socket) => {
      console.log('New client connected');
      
      // Join a room (conversation)
      socket.on('join', (conversationId) => {
        socket.join(conversationId);
        console.log(`User joined conversation: ${conversationId}`);
      });
      
      // Leave a room
      socket.on('leave', (conversationId) => {
        socket.leave(conversationId);
        console.log(`User left conversation: ${conversationId}`);
      });
      
      // Send a message
      socket.on('message', (data) => {
        io.to(data.conversationId).emit('message', data);
      });
      
      // Typing indicator
      socket.on('typing', (data) => {
        socket.to(data.conversationId).emit('typing', data);
      });
      
      // Disconnect
      socket.on('disconnect', () => {
        console.log('Client disconnected');
      });
    });
  })
  .catch(err => {
    console.error('Failed to connect to MongoDB', err);
    process.exit(1);
  });

// Handle unhandled promise rejections
process.on('unhandledRejection', (err) => {
  console.error('Unhandled Promise Rejection:', err);
  // Close server & exit process
  process.exit(1);
});

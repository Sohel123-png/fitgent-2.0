const Trainer = require('../models/trainerModel');
const User = require('../models/userModel');
const Notification = require('../models/notificationModel');
const AppError = require('../utils/appError');
const cloudinary = require('../utils/cloudinary');

// Get all trainers
exports.getAllTrainers = async (req, res, next) => {
  try {
    // Build query
    const queryObj = { ...req.query };
    const excludedFields = ['page', 'sort', 'limit', 'fields'];
    excludedFields.forEach(el => delete queryObj[el]);
    
    // Only show approved trainers
    queryObj.isApproved = true;
    
    // Advanced filtering
    let queryStr = JSON.stringify(queryObj);
    queryStr = queryStr.replace(/\b(gte|gt|lte|lt)\b/g, match => `$${match}`);
    
    // Find trainers
    let query = Trainer.find(JSON.parse(queryStr));
    
    // Sorting
    if (req.query.sort) {
      const sortBy = req.query.sort.split(',').join(' ');
      query = query.sort(sortBy);
    } else {
      query = query.sort('-rating');
    }
    
    // Field limiting
    if (req.query.fields) {
      const fields = req.query.fields.split(',').join(' ');
      query = query.select(fields);
    } else {
      query = query.select('-__v');
    }
    
    // Pagination
    const page = parseInt(req.query.page, 10) || 1;
    const limit = parseInt(req.query.limit, 10) || 10;
    const skip = (page - 1) * limit;
    
    query = query.skip(skip).limit(limit);
    
    // Execute query
    const trainers = await query;
    
    // Send response
    res.status(200).json({
      status: 'success',
      results: trainers.length,
      data: {
        trainers
      }
    });
  } catch (error) {
    next(error);
  }
};

// Get trainer by ID
exports.getTrainer = async (req, res, next) => {
  try {
    const trainer = await Trainer.findById(req.params.id);
    
    if (!trainer) {
      return next(new AppError('No trainer found with that ID', 404));
    }
    
    // Check if trainer is approved
    if (!trainer.isApproved && req.user.role !== 'admin' && trainer.user.id !== req.user.id) {
      return next(new AppError('This trainer profile is not yet approved', 403));
    }
    
    res.status(200).json({
      status: 'success',
      data: {
        trainer
      }
    });
  } catch (error) {
    next(error);
  }
};

// Apply to be a trainer
exports.applyToBeTrainer = async (req, res, next) => {
  try {
    // Check if user already has a trainer profile
    const existingTrainer = await Trainer.findOne({ user: req.user.id });
    
    if (existingTrainer) {
      return next(new AppError('You already have a trainer profile', 400));
    }
    
    // Create trainer profile
    const newTrainer = await Trainer.create({
      user: req.user.id,
      ...req.body,
      isApproved: false
    });
    
    // Create notification for admins
    const admins = await User.find({ role: 'admin' });
    
    const notifications = admins.map(admin => ({
      user: admin._id,
      type: 'system',
      title: 'New Trainer Application',
      message: `${req.user.firstName} ${req.user.lastName} has applied to be a trainer`,
      sender: req.user.id,
      relatedModel: 'Trainer',
      relatedId: newTrainer._id,
      priority: 'high'
    }));
    
    await Notification.insertMany(notifications);
    
    // Update user role to trainer (pending approval)
    await User.findByIdAndUpdate(req.user.id, { role: 'trainer' });
    
    res.status(201).json({
      status: 'success',
      data: {
        trainer: newTrainer
      }
    });
  } catch (error) {
    next(error);
  }
};

// Update trainer profile
exports.updateTrainerProfile = async (req, res, next) => {
  try {
    const trainer = await Trainer.findById(req.params.id);
    
    if (!trainer) {
      return next(new AppError('No trainer found with that ID', 404));
    }
    
    // Check if user is the trainer or admin
    if (trainer.user.id !== req.user.id && req.user.role !== 'admin') {
      return next(new AppError('You do not have permission to update this trainer profile', 403));
    }
    
    // Update trainer profile
    const updatedTrainer = await Trainer.findByIdAndUpdate(req.params.id, req.body, {
      new: true,
      runValidators: true
    });
    
    res.status(200).json({
      status: 'success',
      data: {
        trainer: updatedTrainer
      }
    });
  } catch (error) {
    next(error);
  }
};

// Upload certification document
exports.uploadCertification = async (req, res, next) => {
  try {
    // Check if file exists
    if (!req.file) {
      return next(new AppError('Please upload a certification document', 400));
    }
    
    const { name, issuer, year } = req.body;
    
    if (!name || !issuer || !year) {
      return next(new AppError('Please provide name, issuer, and year for the certification', 400));
    }
    
    const trainer = await Trainer.findOne({ user: req.user.id });
    
    if (!trainer) {
      return next(new AppError('No trainer profile found', 404));
    }
    
    // Upload to cloudinary
    const result = await cloudinary.uploader.upload(req.file.path, {
      folder: 'fitgent/certifications',
      resource_type: 'auto'
    });
    
    // Add certification
    trainer.certification.push({
      name,
      issuer,
      year,
      document: result.secure_url,
      verified: false
    });
    
    await trainer.save();
    
    res.status(200).json({
      status: 'success',
      data: {
        trainer
      }
    });
  } catch (error) {
    next(error);
  }
};

// Get trainer's clients
exports.getTrainerClients = async (req, res, next) => {
  try {
    const trainer = await Trainer.findById(req.params.id);
    
    if (!trainer) {
      return next(new AppError('No trainer found with that ID', 404));
    }
    
    // Check if user is the trainer or admin
    if (trainer.user.id !== req.user.id && req.user.role !== 'admin') {
      return next(new AppError('You do not have permission to view this trainer\'s clients', 403));
    }
    
    // Get clients
    const clients = await User.find({ _id: { $in: trainer.clients } });
    
    res.status(200).json({
      status: 'success',
      results: clients.length,
      data: {
        clients
      }
    });
  } catch (error) {
    next(error);
  }
};

// Add client to trainer
exports.addClient = async (req, res, next) => {
  try {
    const { clientId } = req.body;
    
    if (!clientId) {
      return next(new AppError('Please provide a client ID', 400));
    }
    
    const trainer = await Trainer.findOne({ user: req.user.id });
    
    if (!trainer) {
      return next(new AppError('No trainer profile found', 404));
    }
    
    // Check if client exists
    const client = await User.findById(clientId);
    
    if (!client) {
      return next(new AppError('No client found with that ID', 404));
    }
    
    // Check if client is already assigned to this trainer
    if (trainer.clients.includes(clientId)) {
      return next(new AppError('Client is already assigned to this trainer', 400));
    }
    
    // Add client to trainer
    trainer.clients.push(clientId);
    await trainer.save();
    
    // Create notification for client
    await Notification.createNotification({
      user: clientId,
      type: 'system',
      title: 'New Trainer Assignment',
      message: `${req.user.firstName} ${req.user.lastName} is now your trainer`,
      sender: req.user.id,
      relatedModel: 'Trainer',
      relatedId: trainer._id
    });
    
    res.status(200).json({
      status: 'success',
      data: {
        trainer
      }
    });
  } catch (error) {
    next(error);
  }
};

// Remove client from trainer
exports.removeClient = async (req, res, next) => {
  try {
    const { clientId } = req.params;
    
    const trainer = await Trainer.findOne({ user: req.user.id });
    
    if (!trainer) {
      return next(new AppError('No trainer profile found', 404));
    }
    
    // Check if client is assigned to this trainer
    if (!trainer.clients.includes(clientId)) {
      return next(new AppError('Client is not assigned to this trainer', 400));
    }
    
    // Remove client from trainer
    trainer.clients = trainer.clients.filter(
      client => client.toString() !== clientId
    );
    
    await trainer.save();
    
    // Create notification for client
    await Notification.createNotification({
      user: clientId,
      type: 'system',
      title: 'Trainer Assignment Ended',
      message: `${req.user.firstName} ${req.user.lastName} is no longer your trainer`,
      sender: req.user.id,
      relatedModel: 'Trainer',
      relatedId: trainer._id
    });
    
    res.status(200).json({
      status: 'success',
      data: {
        trainer
      }
    });
  } catch (error) {
    next(error);
  }
};

// Add review to trainer
exports.addTrainerReview = async (req, res, next) => {
  try {
    const { rating, comment } = req.body;
    
    if (!rating) {
      return next(new AppError('Please provide a rating', 400));
    }
    
    const trainer = await Trainer.findById(req.params.id);
    
    if (!trainer) {
      return next(new AppError('No trainer found with that ID', 404));
    }
    
    // Check if user has already reviewed this trainer
    const existingReviewIndex = trainer.reviews.findIndex(
      review => review.user.toString() === req.user.id
    );
    
    if (existingReviewIndex >= 0) {
      // Update existing review
      trainer.reviews[existingReviewIndex].rating = rating;
      trainer.reviews[existingReviewIndex].comment = comment;
    } else {
      // Add new review
      trainer.reviews.push({
        user: req.user.id,
        rating,
        comment
      });
    }
    
    await trainer.save();
    
    res.status(200).json({
      status: 'success',
      data: {
        trainer
      }
    });
  } catch (error) {
    next(error);
  }
};

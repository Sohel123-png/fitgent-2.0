const Post = require('../models/postModel');
const User = require('../models/userModel');
const WorkoutLog = require('../models/workoutLogModel');
const Notification = require('../models/notificationModel');
const AppError = require('../utils/appError');
const cloudinary = require('../utils/cloudinary');

// Get community feed
exports.getCommunityFeed = async (req, res, next) => {
  try {
    // Build query
    const queryObj = { ...req.query };
    const excludedFields = ['page', 'sort', 'limit', 'fields'];
    excludedFields.forEach(el => delete queryObj[el]);
    
    // Only show public posts or posts from friends
    queryObj.visibility = 'public';
    
    // Advanced filtering
    let queryStr = JSON.stringify(queryObj);
    queryStr = queryStr.replace(/\b(gte|gt|lte|lt)\b/g, match => `$${match}`);
    
    // Find posts
    let query = Post.find(JSON.parse(queryStr));
    
    // Sorting
    if (req.query.sort) {
      const sortBy = req.query.sort.split(',').join(' ');
      query = query.sort(sortBy);
    } else {
      query = query.sort('-createdAt');
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
    const posts = await query;
    
    // Send response
    res.status(200).json({
      status: 'success',
      results: posts.length,
      data: {
        posts
      }
    });
  } catch (error) {
    next(error);
  }
};

// Create post
exports.createPost = async (req, res, next) => {
  try {
    // Add user to body
    req.body.user = req.user.id;
    
    // Create post
    const newPost = await Post.create(req.body);
    
    res.status(201).json({
      status: 'success',
      data: {
        post: newPost
      }
    });
  } catch (error) {
    next(error);
  }
};

// Get post by ID
exports.getPost = async (req, res, next) => {
  try {
    const post = await Post.findById(req.params.id);
    
    if (!post) {
      return next(new AppError('No post found with that ID', 404));
    }
    
    // Check if user has access to this post
    if (
      post.visibility !== 'public' &&
      post.user.id !== req.user.id &&
      req.user.role !== 'admin'
    ) {
      return next(new AppError('You do not have permission to view this post', 403));
    }
    
    res.status(200).json({
      status: 'success',
      data: {
        post
      }
    });
  } catch (error) {
    next(error);
  }
};

// Update post
exports.updatePost = async (req, res, next) => {
  try {
    const post = await Post.findById(req.params.id);
    
    if (!post) {
      return next(new AppError('No post found with that ID', 404));
    }
    
    // Check if user is the post creator or admin
    if (post.user.id !== req.user.id && req.user.role !== 'admin') {
      return next(new AppError('You do not have permission to update this post', 403));
    }
    
    // Update post
    const updatedPost = await Post.findByIdAndUpdate(req.params.id, req.body, {
      new: true,
      runValidators: true
    });
    
    res.status(200).json({
      status: 'success',
      data: {
        post: updatedPost
      }
    });
  } catch (error) {
    next(error);
  }
};

// Delete post
exports.deletePost = async (req, res, next) => {
  try {
    const post = await Post.findById(req.params.id);
    
    if (!post) {
      return next(new AppError('No post found with that ID', 404));
    }
    
    // Check if user is the post creator or admin
    if (post.user.id !== req.user.id && req.user.role !== 'admin') {
      return next(new AppError('You do not have permission to delete this post', 403));
    }
    
    await Post.findByIdAndDelete(req.params.id);
    
    res.status(204).json({
      status: 'success',
      data: null
    });
  } catch (error) {
    next(error);
  }
};

// Like post
exports.likePost = async (req, res, next) => {
  try {
    const post = await Post.findById(req.params.id);
    
    if (!post) {
      return next(new AppError('No post found with that ID', 404));
    }
    
    // Check if user has already liked the post
    const alreadyLiked = post.likes.includes(req.user.id);
    
    if (alreadyLiked) {
      // Unlike the post
      post.likes = post.likes.filter(
        userId => userId.toString() !== req.user.id
      );
    } else {
      // Like the post
      post.likes.push(req.user.id);
      
      // Create notification for post owner (if not the same user)
      if (post.user.id !== req.user.id) {
        await Notification.createNotification({
          user: post.user,
          type: 'like',
          title: 'New Like',
          message: `${req.user.firstName} ${req.user.lastName} liked your post`,
          sender: req.user.id,
          relatedModel: 'Post',
          relatedId: post._id
        });
      }
    }
    
    await post.save();
    
    res.status(200).json({
      status: 'success',
      data: {
        post
      }
    });
  } catch (error) {
    next(error);
  }
};

// Comment on post
exports.commentOnPost = async (req, res, next) => {
  try {
    const { content } = req.body;
    
    if (!content) {
      return next(new AppError('Comment content is required', 400));
    }
    
    const post = await Post.findById(req.params.id);
    
    if (!post) {
      return next(new AppError('No post found with that ID', 404));
    }
    
    // Add comment
    post.comments.push({
      user: req.user.id,
      content,
      createdAt: Date.now()
    });
    
    await post.save();
    
    // Create notification for post owner (if not the same user)
    if (post.user.id !== req.user.id) {
      await Notification.createNotification({
        user: post.user,
        type: 'comment',
        title: 'New Comment',
        message: `${req.user.firstName} ${req.user.lastName} commented on your post`,
        sender: req.user.id,
        relatedModel: 'Post',
        relatedId: post._id
      });
    }
    
    res.status(200).json({
      status: 'success',
      data: {
        post
      }
    });
  } catch (error) {
    next(error);
  }
};

// Upload post images
exports.uploadPostImages = async (req, res, next) => {
  try {
    // Check if files exist
    if (!req.files || req.files.length === 0) {
      return next(new AppError('Please upload at least one image', 400));
    }
    
    const post = await Post.findById(req.params.id);
    
    if (!post) {
      return next(new AppError('No post found with that ID', 404));
    }
    
    // Check if user is the post creator
    if (post.user.id !== req.user.id) {
      return next(new AppError('You do not have permission to update this post', 403));
    }
    
    // Upload images to cloudinary
    const uploadPromises = req.files.map(file =>
      cloudinary.uploader.upload(file.path, {
        folder: 'fitgent/posts',
        width: 1200,
        height: 900,
        crop: 'limit'
      })
    );
    
    const results = await Promise.all(uploadPromises);
    
    // Add image URLs to post
    const imageUrls = results.map(result => result.secure_url);
    post.images.push(...imageUrls);
    
    await post.save();
    
    res.status(200).json({
      status: 'success',
      data: {
        post
      }
    });
  } catch (error) {
    next(error);
  }
};

// Get leaderboard
exports.getLeaderboard = async (req, res, next) => {
  try {
    // Get leaderboard type
    const { type = 'workouts' } = req.query;
    
    let leaderboard;
    
    if (type === 'workouts') {
      // Get users with most workouts completed
      leaderboard = await WorkoutLog.aggregate([
        { $match: { completed: true } },
        {
          $group: {
            _id: '$user',
            workoutCount: { $sum: 1 },
            totalDuration: { $sum: '$duration' },
            totalCaloriesBurned: { $sum: '$caloriesBurned' }
          }
        },
        { $sort: { workoutCount: -1 } },
        { $limit: 10 }
      ]);
      
      // Populate user details
      for (const entry of leaderboard) {
        const user = await User.findById(entry._id).select('firstName lastName avatar');
        entry.user = user;
      }
    } else if (type === 'calories') {
      // Get users with most calories burned
      leaderboard = await WorkoutLog.aggregate([
        { $match: { completed: true } },
        {
          $group: {
            _id: '$user',
            totalCaloriesBurned: { $sum: '$caloriesBurned' },
            workoutCount: { $sum: 1 }
          }
        },
        { $sort: { totalCaloriesBurned: -1 } },
        { $limit: 10 }
      ]);
      
      // Populate user details
      for (const entry of leaderboard) {
        const user = await User.findById(entry._id).select('firstName lastName avatar');
        entry.user = user;
      }
    } else {
      return next(new AppError('Invalid leaderboard type', 400));
    }
    
    res.status(200).json({
      status: 'success',
      data: {
        leaderboard
      }
    });
  } catch (error) {
    next(error);
  }
};

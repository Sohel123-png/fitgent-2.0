const cloudinary = require('cloudinary').v2;
const config = require('../config/config');

// Configure cloudinary
cloudinary.config({
  cloud_name: config.cloudinaryCloudName,
  api_key: config.cloudinaryApiKey,
  api_secret: config.cloudinaryApiSecret
});

module.exports = cloudinary;

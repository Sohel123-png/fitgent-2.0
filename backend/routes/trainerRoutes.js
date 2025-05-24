const express = require('express');
const trainerController = require('../controllers/trainerController');
const { protect, restrictTo } = require('../middleware/authMiddleware');
const upload = require('../middleware/uploadMiddleware');

const router = express.Router();

// Protect all routes
router.use(protect);

// Get all trainers
router.get('/', trainerController.getAllTrainers);

// Apply to be a trainer
router.post('/apply', trainerController.applyToBeTrainer);

// Get trainer by ID
router.get('/:id', trainerController.getTrainer);

// Add review to trainer
router.post('/:id/review', trainerController.addTrainerReview);

// Trainer only routes
router.use(restrictTo('trainer', 'admin'));

// Update trainer profile
router.put('/:id', trainerController.updateTrainerProfile);

// Upload certification document
router.post(
  '/certification',
  upload.single('document'),
  trainerController.uploadCertification
);

// Get trainer's clients
router.get('/:id/clients', trainerController.getTrainerClients);

// Add client to trainer
router.post('/clients', trainerController.addClient);

// Remove client from trainer
router.delete('/clients/:clientId', trainerController.removeClient);

module.exports = router;

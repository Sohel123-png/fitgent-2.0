# 🏃‍♂️ FitGent 2.0 - AI-Powered Fitness Platform

[![Live Demo](https://img.shields.io/badge/Live-Demo-brightgreen)](https://fitgent-2.vercel.app)
[![Backend API](https://img.shields.io/badge/API-Live-blue)](https://fitgent-backend.railway.app)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **FitGent 2.0** is a comprehensive fitness platform with smartwatch integration, AI-powered health recommendations, and gamified wellness tracking. Built with React, Flask, and modern web technologies.

## 🌟 Features

### 🎮 Gaming-Style Dashboard
- **Real-time Progress Tracking**: Steps, calories, water intake, sleep
- **Interactive UI**: Anime-inspired design with smooth animations
- **Achievement System**: Badges, streaks, and leaderboards
- **Smart Meal Planner**: AI-suggested meals with nutritional info

### ⌚ Smartwatch Integration
- **Google Fit API**: Sync data from Wear OS and Android devices
- **Apple HealthKit**: Connect Apple Watch and iPhone Health app
- **Mi Band/Noise**: Support for popular fitness trackers
- **Real-time Sync**: Automatic data synchronization

### 🤖 AI Health Engine
- **Personalized Recommendations**: Movement, hydration, nutrition, sleep
- **Wellness Score**: 0-100 comprehensive health rating
- **Smart Alerts**: Stress management and study break reminders
- **Trend Analysis**: Weekly health summaries and insights

### 💬 AI Chatbot
- **Fitness Guidance**: Exercise and nutrition advice
- **Mental Wellness**: Mood tracking and stress management
- **Study Support**: Productivity tips for students
- **Voice Interaction**: Web Speech API integration

## 🚀 Live Demo

### 🌐 Frontend (React)
**URL**: [https://fitgent-2.vercel.app](https://fitgent-2.vercel.app)
- Main Dashboard with gaming UI
- Health Insights with AI recommendations
- Smartwatch connection interface

### 🔧 Backend API (Flask)
**URL**: [https://fitgent-backend.railway.app](https://fitgent-backend.railway.app)
- RESTful API endpoints
- Google Fit integration
- AI recommendation engine

## 📱 Screenshots

### Main Dashboard
![Dashboard](https://via.placeholder.com/800x400/1a1a2e/ffffff?text=Gaming+Style+Dashboard)

### Health Insights
![Health](https://via.placeholder.com/800x400/16213e/ffffff?text=AI+Health+Insights)

### Smartwatch Connect
![Connect](https://via.placeholder.com/800x400/0f3460/ffffff?text=Smartwatch+Integration)

## 🛠️ Tech Stack

### Frontend
- **React 19** with TypeScript
- **Tailwind CSS** for styling
- **Framer Motion** for animations
- **Heroicons** for icons
- **Vercel** for deployment

### Backend
- **Flask** with Python 3.9+
- **SQLAlchemy** for database
- **JWT** authentication
- **Google Fit API** integration
- **Railway** for deployment

### Database
- **PostgreSQL** (Production)
- **SQLite** (Development)

## 🚀 Quick Start

### Prerequisites
- Node.js 16+
- Python 3.9+
- Git

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/fitgent-2.0.git
cd fitgent-2.0
```

### 2. Backend Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Set environment variables
export GOOGLE_CLIENT_ID="your_google_client_id"
export GOOGLE_CLIENT_SECRET="your_google_client_secret"
export JWT_SECRET_KEY="your_jwt_secret"

# Run Flask server
python app.py
```

### 3. Frontend Setup
```bash
# Navigate to frontend directory
cd fitgen-dashboard

# Install dependencies
npm install

# Start React app
npm start
```

### 4. Access Application
- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:5000

## 🔧 Configuration

### Google Fit API Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create new project or select existing
3. Enable **Fitness API**
4. Create **OAuth 2.0 credentials**
5. Add authorized redirect URIs:
   - `http://localhost:5000/api/google-fit/callback`
   - `https://your-domain.com/api/google-fit/callback`

### Environment Variables

#### Backend (.env)
```env
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
JWT_SECRET_KEY=your_jwt_secret_key
SECRET_KEY=your_flask_secret_key
DATABASE_URL=your_database_url
```

#### Frontend (.env)
```env
REACT_APP_API_URL=http://localhost:5000
REACT_APP_GOOGLE_CLIENT_ID=your_google_client_id
```

## 📚 API Documentation

### Authentication
```bash
# Register user
POST /register
{
  "email": "user@example.com",
  "password": "password123",
  "name": "John Doe"
}

# Login
POST /login
{
  "email": "user@example.com",
  "password": "password123"
}
```

### Google Fit Integration
```bash
# Start OAuth flow
GET /api/google-fit/auth

# Get health data
GET /api/google-fit/health/comprehensive
Authorization: Bearer <jwt_token>

# Sync all sources
POST /api/google-fit/health/sync-all
Authorization: Bearer <jwt_token>
```

### AI Recommendations
```bash
# Get personalized recommendations
GET /api/health-ai/recommendations
Authorization: Bearer <jwt_token>

# Get wellness score
GET /api/health-ai/wellness-score
Authorization: Bearer <jwt_token>
```

## 🚀 Deployment

### Frontend (Vercel)
1. Connect GitHub repository to Vercel
2. Set environment variables in Vercel dashboard
3. Deploy automatically on push to main branch

### Backend (Railway)
1. Connect GitHub repository to Railway
2. Set environment variables in Railway dashboard
3. Deploy automatically on push to main branch

### Alternative Deployment Options
- **Frontend**: Netlify, GitHub Pages, AWS S3
- **Backend**: Heroku, DigitalOcean, AWS EC2

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Your Name**
- LinkedIn: [Your LinkedIn Profile](https://linkedin.com/in/yourprofile)
- GitHub: [@yourusername](https://github.com/yourusername)
- Email: your.email@example.com

## 🙏 Acknowledgments

- Google Fit API for health data integration
- Framer Motion for smooth animations
- Tailwind CSS for beautiful styling
- React community for amazing tools

## 📞 Support

For support, email your.email@example.com or create an issue on GitHub.

---

**⭐ Star this repository if you found it helpful!**

Made with ❤️ for the fitness community

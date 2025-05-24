# 📁 FitGent 2.0 - Project Structure

## 🏗️ Overall Architecture

```
fitgent-2.0/
├── 🔧 Backend (Flask API)
│   ├── app.py                 # Main Flask application
│   ├── db.py                  # Database models and configuration
│   ├── auth.py                # Authentication routes
│   ├── google_fit_api.py      # Google Fit integration
│   ├── health_ai_engine.py    # AI recommendation engine
│   ├── requirements.txt       # Python dependencies
│   └── templates/             # HTML templates
│
├── 🎨 Frontend (React)
│   ├── fitgen-dashboard/
│   │   ├── src/
│   │   │   ├── components/    # React components
│   │   │   ├── services/      # API services
│   │   │   └── types.ts       # TypeScript types
│   │   ├── package.json       # Node.js dependencies
│   │   └── tailwind.config.js # Tailwind CSS config
│
├── 📚 Documentation
│   ├── README.md              # Main project documentation
│   ├── DEPLOYMENT.md          # Deployment guide
│   ├── SMARTWATCH_INTEGRATION.md # Technical details
│   └── PROJECT_STRUCTURE.md  # This file
│
└── 🚀 Deployment
    ├── Procfile               # Heroku/Railway deployment
    ├── runtime.txt            # Python version
    └── .gitignore             # Git ignore rules
```

## 🔧 Backend Structure

### Core Files
- **`app.py`** - Main Flask application with route registration
- **`db.py`** - SQLAlchemy models (User, FitnessData, HealthStat, Notification)
- **`auth.py`** - JWT authentication and user management
- **`google_fit_api.py`** - Google Fit OAuth and data collection
- **`health_ai_engine.py`** - AI-powered health recommendations

### API Endpoints

#### Authentication
```
POST /register          # User registration
POST /login             # User login
GET  /protected         # Protected route example
GET  /admin             # Admin-only route
```

#### Google Fit Integration
```
GET  /api/google-fit/auth                    # Start OAuth flow
GET  /api/google-fit/callback                # OAuth callback
GET  /api/google-fit/status                  # Connection status
GET  /api/google-fit/data                    # Basic fitness data
POST /api/google-fit/sync                    # Sync fitness data
GET  /api/google-fit/health/comprehensive    # All health metrics
POST /api/google-fit/health/sync-all         # Sync all sources
GET  /api/google-fit/health/weekly-summary   # Weekly trends
```

#### AI Health Engine
```
GET /api/health-ai/recommendations  # Personalized recommendations
GET /api/health-ai/wellness-score   # Wellness score analysis
```

### Database Models

#### User Model
```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(100))
    role = db.Column(db.String(20), default='user')
    height_cm = db.Column(db.Float)
    weight_kg = db.Column(db.Float)
    age = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

#### FitnessData Model
```python
class FitnessData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date = db.Column(db.Date, nullable=False)
    steps = db.Column(db.Integer)
    calories_burned = db.Column(db.Integer)
    heart_rate = db.Column(db.Integer)
    sleep_hours = db.Column(db.Float)
    weight_kg = db.Column(db.Float)
    distance_km = db.Column(db.Float)
    active_minutes = db.Column(db.Integer)
    bmi = db.Column(db.Float)
    last_sync = db.Column(db.DateTime)
```

## 🎨 Frontend Structure

### Component Architecture

#### Main Components
- **`App.tsx`** - Root component with navigation
- **`Dashboard.tsx`** - Original gaming-style dashboard
- **`HealthDashboard.tsx`** - New health insights dashboard
- **`SmartwatchConnect.tsx`** - Device connection interface

#### Shared Components
- **`Navbar.tsx`** - Navigation bar
- **`DailyProgress.tsx`** - Progress tracking
- **`ChatAssistant.tsx`** - AI chatbot
- **`MealPlanner.tsx`** - Meal planning
- **`Leaderboard.tsx`** - Community features

### Services Layer
- **`healthApi.ts`** - API communication service
- **`types.ts`** - TypeScript type definitions

### Styling
- **Tailwind CSS** - Utility-first CSS framework
- **Framer Motion** - Animation library
- **Heroicons** - Icon library

## 🔄 Data Flow

### 1. User Authentication
```
User → Frontend → Backend Auth → JWT Token → Protected Routes
```

### 2. Health Data Collection
```
Smartwatch → Google Fit → Backend API → Database → Frontend Display
```

### 3. AI Recommendations
```
Health Data → AI Engine → Personalized Recommendations → User Interface
```

## 🚀 Deployment Architecture

### Production Setup
```
GitHub Repository
├── Frontend → Vercel (https://fitgent-2.vercel.app)
├── Backend → Railway (https://fitgent-backend.railway.app)
└── Database → PostgreSQL (Railway/Heroku)
```

### Development Setup
```
Local Development
├── Frontend → http://localhost:3000
├── Backend → http://localhost:5000
└── Database → SQLite (local)
```

## 📦 Dependencies

### Backend (Python)
```
Flask==2.3.3                 # Web framework
Flask-SQLAlchemy==3.0.5       # Database ORM
Flask-JWT-Extended==4.5.3     # JWT authentication
Flask-CORS==4.0.0             # Cross-origin requests
google-api-python-client      # Google Fit API
google-auth-oauthlib          # OAuth authentication
bcrypt==4.1.2                 # Password hashing
gunicorn==21.2.0              # Production server
psycopg2-binary==2.9.9        # PostgreSQL adapter
```

### Frontend (Node.js)
```
react==19.1.0                 # UI framework
typescript==4.9.5             # Type safety
@heroicons/react              # Icons
framer-motion==12.12.1        # Animations
tailwindcss==3.3.0            # CSS framework
react-icons==5.5.0            # Additional icons
uuid==11.1.0                  # Unique identifiers
```

## 🔐 Security Features

### Authentication
- JWT token-based authentication
- Password hashing with bcrypt
- Role-based access control (user/admin)

### API Security
- CORS configuration
- Environment variable protection
- OAuth 2.0 for Google Fit

### Data Protection
- Encrypted data transmission (HTTPS)
- Secure token storage
- Input validation and sanitization

## 📊 Features Overview

### 🎮 Gaming Dashboard
- Real-time progress tracking
- Achievement system
- Leaderboards
- Interactive UI with animations

### ⌚ Smartwatch Integration
- Google Fit API integration
- Apple HealthKit support (mobile app)
- Mi Band/Noise device compatibility
- Real-time data synchronization

### 🤖 AI Health Engine
- Personalized recommendations
- Wellness score calculation (0-100)
- Trend analysis and insights
- Smart notifications and alerts

### 💬 AI Chatbot
- Fitness and nutrition guidance
- Mental wellness support
- Study productivity tips
- Voice interaction capabilities

## 🔧 Configuration Files

### Backend Configuration
- **`.env`** - Environment variables
- **`requirements.txt`** - Python dependencies
- **`Procfile`** - Deployment configuration
- **`runtime.txt`** - Python version specification

### Frontend Configuration
- **`package.json`** - Node.js dependencies
- **`tailwind.config.js`** - Tailwind CSS configuration
- **`tsconfig.json`** - TypeScript configuration
- **`.env`** - Environment variables

## 📈 Scalability Considerations

### Backend Scaling
- Horizontal scaling with load balancers
- Database connection pooling
- Caching with Redis
- API rate limiting

### Frontend Optimization
- Code splitting and lazy loading
- Image optimization
- CDN for static assets
- Progressive Web App (PWA) features

## 🧪 Testing Strategy

### Backend Testing
- Unit tests for API endpoints
- Integration tests for database operations
- Mock testing for external APIs

### Frontend Testing
- Component unit tests
- Integration tests for user flows
- End-to-end testing with Cypress

---

This structure provides a comprehensive, scalable foundation for the FitGent 2.0 platform with room for future enhancements and features! 🚀

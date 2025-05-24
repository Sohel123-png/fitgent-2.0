# 🚀 FitGent 2.0 Deployment Guide

## 📋 Quick Deployment Steps

### 1. GitHub Repository Setup

```bash
# Initialize git repository
git init
git add .
git commit -m "Initial commit: FitGent 2.0 with smartwatch integration"

# Create GitHub repository and push
git remote add origin https://github.com/yourusername/fitgent-2.0.git
git branch -M main
git push -u origin main
```

### 2. Backend Deployment (Railway/Heroku)

#### Option A: Railway (Recommended)
1. Go to [Railway.app](https://railway.app)
2. Connect your GitHub account
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your `fitgent-2.0` repository
5. Set environment variables:
   ```
   GOOGLE_CLIENT_ID=your_google_client_id
   GOOGLE_CLIENT_SECRET=your_google_client_secret
   JWT_SECRET_KEY=your_jwt_secret_key
   SECRET_KEY=your_flask_secret_key
   DATABASE_URL=postgresql://...
   ```
6. Deploy automatically!

#### Option B: Heroku
```bash
# Install Heroku CLI
# Login to Heroku
heroku login

# Create Heroku app
heroku create fitgent-backend

# Set environment variables
heroku config:set GOOGLE_CLIENT_ID=your_google_client_id
heroku config:set GOOGLE_CLIENT_SECRET=your_google_client_secret
heroku config:set JWT_SECRET_KEY=your_jwt_secret_key

# Add PostgreSQL database
heroku addons:create heroku-postgresql:hobby-dev

# Deploy
git push heroku main
```

### 3. Frontend Deployment (Vercel)

1. Go to [Vercel.com](https://vercel.com)
2. Connect your GitHub account
3. Click "New Project" → Import your repository
4. Select `fitgen-dashboard` folder as root directory
5. Set environment variables:
   ```
   REACT_APP_API_URL=https://your-backend-url.railway.app
   REACT_APP_GOOGLE_CLIENT_ID=your_google_client_id
   ```
6. Deploy!

## 🔧 Environment Variables Setup

### Backend (.env)
```env
# Google Fit API
GOOGLE_CLIENT_ID=123456789-abcdefghijklmnop.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-abcdefghijklmnopqrstuvwxyz
GOOGLE_REDIRECT_URI=https://your-backend-url.railway.app/api/google-fit/callback

# JWT & Security
JWT_SECRET_KEY=your-super-secret-jwt-key-here
SECRET_KEY=your-flask-secret-key-here

# Database
DATABASE_URL=postgresql://username:password@host:port/database

# CORS
CORS_ORIGINS=https://your-frontend-url.vercel.app,http://localhost:3000
```

### Frontend (.env)
```env
REACT_APP_API_URL=https://your-backend-url.railway.app
REACT_APP_GOOGLE_CLIENT_ID=123456789-abcdefghijklmnop.apps.googleusercontent.com
```

## 🔑 Google Fit API Configuration

### 1. Google Cloud Console Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create new project: "FitGent 2.0"
3. Enable APIs:
   - Fitness API
   - People API (optional)

### 2. OAuth 2.0 Credentials
1. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
2. Application type: "Web application"
3. Authorized redirect URIs:
   ```
   https://your-backend-url.railway.app/api/google-fit/callback
   http://localhost:5000/api/google-fit/callback
   ```
4. Copy Client ID and Client Secret

### 3. OAuth Consent Screen
1. Configure OAuth consent screen
2. Add scopes:
   - `https://www.googleapis.com/auth/fitness.activity.read`
   - `https://www.googleapis.com/auth/fitness.heart_rate.read`
   - `https://www.googleapis.com/auth/fitness.sleep.read`
   - `https://www.googleapis.com/auth/fitness.body.read`

## 📱 Live URLs

After deployment, your app will be available at:

### 🌐 Frontend
- **Vercel**: `https://fitgent-2.vercel.app`
- **Netlify**: `https://fitgent-2.netlify.app`

### 🔧 Backend API
- **Railway**: `https://fitgent-backend.railway.app`
- **Heroku**: `https://fitgent-backend.herokuapp.com`

## 🧪 Testing Deployment

### 1. Test Backend API
```bash
# Health check
curl https://your-backend-url.railway.app/

# Test registration
curl -X POST https://your-backend-url.railway.app/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","name":"Test User"}'
```

### 2. Test Frontend
1. Visit your frontend URL
2. Try registration/login
3. Navigate between dashboard tabs
4. Test Google Fit connection

## 🔄 Continuous Deployment

### Automatic Deployment Setup
1. **Railway**: Automatically deploys on push to `main` branch
2. **Vercel**: Automatically deploys on push to `main` branch
3. **GitHub Actions**: Optional CI/CD pipeline

### GitHub Actions (Optional)
Create `.github/workflows/deploy.yml`:
```yaml
name: Deploy FitGent 2.0

on:
  push:
    branches: [ main ]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Deploy to Railway
      run: echo "Backend deployment handled by Railway"

  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Deploy to Vercel
      run: echo "Frontend deployment handled by Vercel"
```

## 📊 Monitoring & Analytics

### 1. Backend Monitoring
- **Railway**: Built-in metrics and logs
- **Heroku**: Heroku Metrics
- **Custom**: Add logging and error tracking

### 2. Frontend Analytics
- **Vercel Analytics**: Built-in performance monitoring
- **Google Analytics**: User behavior tracking
- **Sentry**: Error tracking

## 🐛 Troubleshooting

### Common Issues

1. **CORS Errors**
   - Update `CORS_ORIGINS` in backend environment variables
   - Include both production and development URLs

2. **Google Fit Authentication Failed**
   - Check OAuth redirect URIs in Google Cloud Console
   - Verify Client ID and Secret in environment variables

3. **Database Connection Issues**
   - Ensure DATABASE_URL is correctly set
   - Check PostgreSQL connection string format

4. **Build Failures**
   - Check Node.js version compatibility
   - Verify all dependencies are listed in package.json

### Debug Commands
```bash
# Check backend logs
railway logs

# Check frontend build
npm run build

# Test API endpoints
curl -v https://your-backend-url.railway.app/api/google-fit/status
```

## 🎯 Performance Optimization

### Backend
- Enable gzip compression
- Use Redis for caching
- Optimize database queries
- Add rate limiting

### Frontend
- Enable code splitting
- Optimize images
- Use React.memo for components
- Implement lazy loading

## 🔐 Security Checklist

- [ ] Environment variables secured
- [ ] HTTPS enabled on all endpoints
- [ ] JWT tokens properly configured
- [ ] CORS properly configured
- [ ] Google OAuth properly set up
- [ ] Database credentials secured
- [ ] API rate limiting enabled

## 📞 Support

If you encounter issues during deployment:
1. Check the troubleshooting section above
2. Review deployment logs
3. Create an issue on GitHub
4. Contact support

---

**🎉 Congratulations! Your FitGent 2.0 app is now live and ready to share with the world!**

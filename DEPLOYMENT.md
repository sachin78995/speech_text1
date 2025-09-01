# 🚀 Deployment Guide

## 📋 Pre-Deployment Checklist

### 1. **GitHub Repository Setup**
- [ ] Push code to GitHub repository
- [ ] Ensure `.gitignore` excludes sensitive files
- [ ] Create `.env` files from `.env.example` templates
- [ ] Update `README.md` with your repository URL

### 2. **Environment Configuration**
- [ ] Generate new `SECRET_KEY` for production
- [ ] Set `DEBUG=False` in production
- [ ] Configure `ALLOWED_HOSTS` with your domain
- [ ] Update `CORS_ALLOWED_ORIGINS` with frontend URL

## 🐳 Docker Deployment (Recommended)

### **Local Testing:**
```bash
# 1. Copy environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# 2. Edit environment files with your values
# 3. Start all services
docker-compose up --build

# 4. Access application
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# LanguageTool: http://localhost:8081
```

### **Production Docker:**
1. Update `docker-compose.yml` with production values
2. Use external PostgreSQL database
3. Configure domain names and SSL certificates

## ☁️ Cloud Platform Deployment

### **Railway (Easiest Option)**

#### Backend Deployment:
1. Connect GitHub repository to Railway
2. Create new service from `backend/` folder
3. Set environment variables:
   ```
   SECRET_KEY=your-secret-key
   DEBUG=False
   ALLOWED_HOSTS=your-railway-domain.railway.app
   LANGUAGETOOL_URL=https://your-languagetool-service.railway.app/v2/check
   ```
4. Railway will auto-detect Django and deploy

#### Frontend Deployment:
1. Create second Railway service from `frontend/` folder
2. Set environment variable:
   ```
   REACT_APP_API_URL=https://your-backend-service.railway.app/api
   ```
3. Railway will build and serve React app

#### LanguageTool Deployment:
1. Create third Railway service
2. Use Docker image: `erikvl87/languagetool`
3. Expose on port 8080

### **Render Platform**

#### Backend:
1. Create Web Service from GitHub
2. Build Command: `pip install -r requirements_production.txt`
3. Start Command: `gunicorn speech_to_text.wsgi:application`
4. Add PostgreSQL database

#### Frontend:
1. Create Static Site from GitHub
2. Build Command: `npm run build`
3. Publish Directory: `build`

### **DigitalOcean App Platform**

#### App Spec Configuration:
```yaml
name: speech-to-text-app
services:
- name: backend
  source_dir: /backend
  github:
    repo: your-username/your-repo
    branch: main
  run_command: gunicorn speech_to_text.wsgi:application
  
- name: frontend
  source_dir: /frontend
  github:
    repo: your-username/your-repo
    branch: main
  build_command: npm run build
```

## 🗄️ Database Migration

### **From SQLite to PostgreSQL:**
```bash
# 1. Dump existing data
python manage.py dumpdata > data.json

# 2. Update database settings
# 3. Run migrations
python manage.py migrate

# 4. Load data
python manage.py loaddata data.json
```

## 🔧 Production Optimizations

### **Backend Optimizations:**
- Use `gunicorn` instead of Django dev server
- Enable `whitenoise` for static files
- Configure proper logging
- Use environment-based settings

### **Frontend Optimizations:**
- Build optimized production bundle
- Enable gzip compression
- Use CDN for static assets
- Configure proper caching headers

### **LanguageTool Options:**
- **Self-hosted**: Include in Docker setup
- **Cloud API**: Use LanguageTool's paid service
- **Fallback**: Disable grammar correction if service unavailable

## 🌐 Domain & SSL Setup

### **Custom Domain:**
1. Purchase domain from registrar
2. Configure DNS to point to hosting platform
3. Enable SSL certificate (usually automatic)
4. Update `ALLOWED_HOSTS` and `CORS_ALLOWED_ORIGINS`

### **Subdomain Strategy:**
- `api.yourdomain.com` → Backend
- `app.yourdomain.com` → Frontend
- `languagetool.yourdomain.com` → LanguageTool

## 🔍 Monitoring & Health Checks

### **Health Check Endpoints:**
- Backend: `/api/health/`
- LanguageTool: `/v2/languages`

### **Monitoring Tools:**
- **Uptime**: UptimeRobot, Pingdom
- **Logs**: Platform-specific logging
- **Errors**: Sentry integration (optional)

## 🚨 Troubleshooting

### **Common Deployment Issues:**
1. **Whisper model download**: Ensure sufficient disk space and memory
2. **CORS errors**: Check frontend URL in backend CORS settings
3. **LanguageTool connection**: Verify service URL and port
4. **Static files**: Configure `STATIC_ROOT` and `whitenoise`
5. **Database migrations**: Run migrations after deployment

### **Performance Considerations:**
- **Whisper model size**: `tiny` for speed, `base`/`small` for accuracy
- **Memory requirements**: Minimum 2GB RAM recommended
- **Storage**: Plan for audio file storage growth

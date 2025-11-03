# Speech-to-Text Application - Docker Setup

This application can run completely in Docker containers, making it work on any system with Docker installed.

## 🐳 Complete Docker Setup (Recommended)

### Prerequisites
- Docker and Docker Compose installed
- At least 4GB free RAM
- Internet connection for downloading images

### Quick Start (Any System)

1. **Clone the repository:**
```bash
git clone https://github.com/sachin78995/speech_text1.git
cd speech_text1
```

2. **Start all services:**
```bash
docker-compose up --build
```

3. **Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api
- Admin Panel: http://localhost:8000/admin (admin/admin123)
- LanguageTool: http://localhost:8081

### What Gets Started
The Docker setup includes:
- ✅ **PostgreSQL Database** (port 5432)
- ✅ **LanguageTool Service** (port 8081) - for grammar correction
- ✅ **Django Backend** (port 8000) - API server
- ✅ **React Frontend** (port 3000) - web interface

### Common Commands

**Start in background:**
```bash
docker-compose up -d
```

**Stop all services:**
```bash
docker-compose down
```

**View logs:**
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs backend
docker-compose logs frontend
```

**Rebuild after code changes:**
```bash
docker-compose up --build
```

**Reset everything (clean start):**
```bash
docker-compose down -v
docker-compose up --build
```

## 🔧 Development Mode

The Docker setup is configured for development with:
- Hot reload for backend (code changes auto-restart)
- Volume mounts for real-time development
- Debug mode enabled
- Automatic database migrations
- Auto-created admin user (admin/admin123)

## 🚀 Production Deployment

### Option 1: Railway (Recommended)
1. Deploy backend to Railway using the fixed Dockerfile
2. Deploy frontend to Vercel
3. Configure environment variables

### Option 2: Docker in Production
1. Set environment variables for production:
```bash
export DEBUG=False
export SECRET_KEY="your-production-secret"
export ALLOWED_HOSTS="your-domain.com"
export CORS_ALLOWED_ORIGINS="https://your-frontend-domain.com"
```

2. Use production docker-compose:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 🛠 Troubleshooting

### Services won't start
```bash
# Check if ports are already in use
netstat -tulpn | grep :3000
netstat -tulpn | grep :8000

# Free up ports or change them in docker-compose.yml
```

### Database connection issues
```bash
# Reset database
docker-compose down -v
docker-compose up db
# Wait for database to start, then start other services
```

### Memory issues
```bash
# On Windows/Mac, increase Docker memory to 4GB+
# Docker Desktop → Settings → Resources → Memory
```

### Permission issues (Linux)
```bash
# Fix file permissions
sudo chown -R $USER:$USER .
```

## 📱 Features Available

Once running, you can:
- 🎤 Record audio directly in the browser
- 📝 Upload audio files for transcription  
- ✏️ View transcripts with grammar correction
- 🗑️ Delete old transcripts
- 👥 Admin panel to manage data

## 🔍 API Endpoints

- `GET /api/transcripts/` - List all transcripts
- `POST /api/transcripts/` - Create new transcript
- `DELETE /api/transcripts/{id}/` - Delete transcript
- `POST /api/transcribe/` - Upload audio for transcription
- `GET /api/health/` - Health check

## 🌍 Cross-Platform Compatibility

This Docker setup works on:
- ✅ Windows (Docker Desktop)
- ✅ macOS (Docker Desktop) 
- ✅ Linux (Docker Engine)
- ✅ Cloud platforms (AWS, GCP, Azure)
- ✅ VPS servers

## 📊 System Requirements

**Minimum:**
- 2 CPU cores
- 4GB RAM
- 10GB disk space

**Recommended:**
- 4+ CPU cores  
- 8GB+ RAM
- 20GB+ disk space
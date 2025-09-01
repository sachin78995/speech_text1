# 🎤 Offline Speech-to-Text Application

A full-stack web application that provides offline speech recognition with grammar correction using OpenAI Whisper and LanguageTool.

## 🌟 Features

- **Offline Speech Recognition** - Uses OpenAI Whisper for local transcription
- **Grammar Correction** - LanguageTool integration for text improvement
- **Audio Preprocessing** - Noise reduction and audio enhancement
- **Real-time Recording** - Browser-based audio recording
- **Transcript Management** - Save, view, and delete transcriptions
- **Modern UI** - Responsive React interface with animations

## 🏗️ Architecture

### Backend (Django REST API)
- **Framework**: Django 4.2.7 + Django REST Framework
- **AI Models**: OpenAI Whisper (configurable model size)
- **Grammar**: LanguageTool integration
- **Database**: SQLite (development) / PostgreSQL (production)
- **Audio Processing**: Noise reduction with noisereduce

### Frontend (React SPA)
- **Framework**: React 18
- **Audio**: Web Audio API for recording
- **Styling**: Modern CSS with glassmorphism effects
- **API Communication**: Axios for backend integration

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Git

### 1. Clone Repository
```bash
git clone <your-repo-url>
cd offinetext
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm start
```

### 4. LanguageTool Setup (Choose One Option)

#### Option A: Docker (Recommended)
```bash
docker run --rm -p 8081:8080 erikvl87/languagetool
```

#### Option B: Manual Installation
1. Download LanguageTool from https://languagetool.org/download/
2. Extract and run: `java -cp languagetool-server.jar org.languagetool.server.HTTPServer --port 8081`

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)
```bash
docker-compose up --build
```

This will start:
- Django backend on port 8000
- React frontend on port 3000
- LanguageTool on port 8081
- PostgreSQL database

### Manual Docker Build
```bash
# Backend
cd backend
docker build -t speech-backend .

# Frontend
cd frontend
docker build -t speech-frontend .
```

## ☁️ Cloud Deployment Options

### Option 1: Railway (Easiest)
1. Connect GitHub repository to Railway
2. Deploy backend and frontend as separate services
3. Add LanguageTool as a third service
4. Configure environment variables

### Option 2: Render
1. Create web service for Django backend
2. Create static site for React frontend
3. Use external LanguageTool service or Docker

### Option 3: DigitalOcean App Platform
1. Create app from GitHub repository
2. Configure multi-component deployment
3. Add managed PostgreSQL database

## 🔧 Environment Configuration

### Backend Environment Variables
```bash
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,localhost
DATABASE_URL=postgres://user:pass@host:port/dbname
LANGUAGETOOL_URL=http://languagetool:8081/v2/check
WHISPER_MODEL=tiny
```

### Frontend Environment Variables
```bash
REACT_APP_API_URL=https://your-backend-url.com/api
```

## 📦 Production Considerations

### Database
- **Development**: SQLite (included)
- **Production**: PostgreSQL (recommended)
- **Migration**: Use `python manage.py migrate`

### Static Files
- Configure `STATIC_ROOT` for production
- Use cloud storage (AWS S3) for media files

### Security
- Generate new `SECRET_KEY` for production
- Set `DEBUG=False`
- Configure proper `ALLOWED_HOSTS`
- Use HTTPS in production

## 🧪 Testing

### Backend Tests
```bash
cd backend
python test_enhanced_pipeline.py
python quick_test.py
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 🔍 Troubleshooting

### Common Issues
1. **LanguageTool not accessible**: Check if service is running on port 8081
2. **Whisper model download**: First run downloads model (may take time)
3. **CORS errors**: Verify frontend URL in Django CORS settings
4. **Audio recording fails**: Check browser microphone permissions

### Health Check
- Backend: `http://localhost:8000/api/health/`
- Frontend: `http://localhost:3000`

## 📝 API Documentation

### Endpoints
- `POST /api/transcribe/` - Upload audio for transcription
- `GET /api/transcripts/` - List all transcripts
- `DELETE /api/transcripts/{id}/` - Delete transcript
- `GET /api/health/` - Service health check

### Audio Format
- **Input**: WAV files (16kHz recommended)
- **Max Size**: 50MB
- **Channels**: Mono preferred

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

For issues and questions:
1. Check troubleshooting section
2. Review GitHub issues
3. Create new issue with detailed description

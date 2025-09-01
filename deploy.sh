#!/bin/bash

# Deployment script for Speech-to-Text Application
echo "🚀 Starting deployment setup..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create environment files if they don't exist
if [ ! -f backend/.env ]; then
    echo "📝 Creating backend .env file from template..."
    cp backend/.env.example backend/.env
    echo "⚠️  Please edit backend/.env with your production values!"
fi

if [ ! -f frontend/.env ]; then
    echo "📝 Creating frontend .env file from template..."
    cp frontend/.env.example frontend/.env
    echo "⚠️  Please edit frontend/.env with your production values!"
fi

# Build and start services
echo "🐳 Building and starting Docker containers..."
docker-compose up --build -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 10

# Check service health
echo "🔍 Checking service health..."
curl -f http://localhost:8000/api/health/ || echo "❌ Backend health check failed"
curl -f http://localhost:3000 || echo "❌ Frontend health check failed"
curl -f http://localhost:8081/v2/languages || echo "❌ LanguageTool health check failed"

echo "✅ Deployment completed!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000/api"
echo "📝 LanguageTool: http://localhost:8081"

FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Gunicorn for production
RUN pip install gunicorn

# Copy project
COPY . .

# Copy startup scripts
COPY start.sh /app/start.sh
COPY start-dev.sh /app/start-dev.sh
RUN chmod +x /app/start.sh /app/start-dev.sh

# Install netcat for health checks and database waiting
RUN apt-get update && apt-get install -y netcat-openbsd curl && rm -rf /var/lib/apt/lists/*

# Create media directory
RUN mkdir -p media/audio

# Expose port (Railway will set PORT env var)
EXPOSE 8000

# For development, we'll override this in docker-compose
# For production (Railway), use the startup script
CMD ["/app/start.sh"]

#!/bin/bash
set -e

# Run migrations
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput

# Start Gunicorn with PORT from environment (Railway sets this)
PORT=${PORT:-8000}
exec gunicorn speech_to_text.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120
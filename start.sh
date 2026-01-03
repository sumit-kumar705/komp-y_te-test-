#!/bin/bash
# Railway Deployment Startup Script
# This script runs database migrations before starting the application

echo "=========================================="
echo "🚀 Starting KOMPLYTE Backend Deployment"
echo "=========================================="

# Check if database URL is set
if [ -z "$MYSQL_URL" ] && [ -z "$DATABASE_URL" ] && [ -z "$MYSQLHOST" ]; then
    echo "⚠️  WARNING: No database connection found!"
    echo "Please set MYSQL_URL or DATABASE_URL in Railway environment variables"
fi

# Run database migrations
echo "📦 Running database migrations..."
flask db upgrade

# Check if migrations succeeded
if [ $? -eq 0 ]; then
    echo "✅ Database migrations completed successfully!"
else
    echo "❌ Database migrations failed!"
    echo "Attempting to initialize database..."
    flask db init || echo "Migration folder already exists"
    flask db migrate -m "Initial migration" || echo "Migration failed"
    flask db upgrade || echo "Upgrade failed"
fi

echo "=========================================="
echo "🌐 Starting Gunicorn Web Server..."
echo "=========================================="

# Start the application with Gunicorn
exec gunicorn wsgi:app \
    --workers 4 \
    --bind 0.0.0.0:$PORT \
    --timeout 120 \
    --keep-alive 5 \
    --log-level info \
    --access-logfile - \
    --error-logfile - \
    --preload

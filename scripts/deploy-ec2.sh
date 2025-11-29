#!/bin/bash
set -e

echo "🚀 Starting deployment to EC2..."

# Navigate to project directory
cd /opt/agentic_rag

# Pull latest code
echo "📥 Pulling latest code..."
git pull origin main

# Pull latest Docker images
echo "🐳 Pulling Docker images..."
docker-compose pull

# Stop services
echo "⏸️  Stopping services..."
docker-compose down

# Start services
echo "▶️  Starting services..."
docker-compose up -d

# Wait for services
echo "⏳ Waiting for services to start..."
sleep 10

# Run migrations
echo "🔄 Running migrations..."
docker-compose exec -T web python manage.py migrate

# Collect static files
echo "📁 Collecting static files..."
docker-compose exec -T web python manage.py collectstatic --noinput || true

# Check health
echo "🏥 Checking service health..."
if curl -f http://localhost:8000/api/rag/tools/ > /dev/null 2>&1; then
    echo "✅ Deployment successful!"
    docker-compose ps
else
    echo "❌ Deployment failed - service not responding"
    docker-compose logs --tail=50
    exit 1
fi

echo "🎉 Deployment complete!"

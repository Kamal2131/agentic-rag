#!/bin/bash
# EC2 Initial Setup Script
# Run this on a fresh Ubuntu EC2 instance

set -e

echo "🔧 Starting EC2 setup for Agentic RAG..."

# Update system
echo "📦 Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install Docker
echo "🐳 Installing Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
rm get-docker.sh

# Install Docker Compose
echo "📦 Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install useful tools
echo "🛠️  Installing utilities..."
sudo apt-get install -y git curl htop ncdu vim

# Create application directory
echo "📁 Creating application directory..."
sudo mkdir -p /opt/agentic_rag
sudo chown $USER:$USER /opt/agentic_rag

# Configure firewall (UFW)
echo "🔥 Configuring firewall..."
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw allow 8000/tcp # Django (temporary)
echo "y" | sudo ufw enable || true

# Install Nginx (optional)
echo "🌐 Installing Nginx..."
sudo apt-get install -y nginx

# Enable Docker service
echo "▶️  Enabling Docker..."
sudo systemctl enable docker
sudo systemctl start docker

# Verify installations
echo ""
echo "✅ Setup complete! Verifying installations..."
docker --version
docker-compose --version
nginx -v

echo ""
echo "🎉 EC2 setup complete!"
echo ""
echo "Next steps:"
echo "1. Log out and back in for Docker permissions"
echo "2. Clone your repository to /opt/agentic_rag"
echo "3. Create .env file with your configuration"
echo "4. Run: docker-compose up -d"
echo ""
echo "⚠️  IMPORTANT: Log out and back in now!"

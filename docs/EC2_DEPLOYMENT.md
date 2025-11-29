# AWS EC2 Deployment Guide

## Prerequisites

### On Your EC2 Instance
- Ubuntu 20.04+ or Amazon Linux 2
- Docker and Docker Compose installed
- SSH access configured
- Port 8000 open in Security Group

## Step 1: Prepare Your EC2 Instance

### 1.1 SSH into Your EC2
```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```


### 1.2 Install Docker & Docker Compose
```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version

# Log out and back in for group changes
exit
```

### 1.3 Configure Security Group
In AWS Console → EC2 → Security Groups:
- **Port 22**: SSH (your IP only)
- **Port 8000**: HTTP (0.0.0.0/0 or specific IPs)
- **Port 443**: HTTPS (optional, if using SSL)

## Step 2: Clone and Configure Your Project

```bash
# Create application directory
sudo mkdir -p /opt/agentic_rag
sudo chown $USER:$USER /opt/agentic_rag
cd /opt/agentic_rag

# Clone repository (replace with your repo URL)
git clone https://github.com/YOUR_USERNAME/agentic_rag.git .

# Create .env file
nano .env
```

Add to `.env`:
```bash
SECRET_KEY=your-super-secret-key-change-this
DEBUG=False
ALLOWED_HOSTS=your-ec2-ip,your-domain.com

DB_NAME=agentic_rag
DB_USER=postgres
DB_PASSWORD=strong-password-here
DB_HOST=db
DB_PORT=5432

QDRANT_HOST=qdrant
QDRANT_PORT=6333

REDIS_HOST=redis
REDIS_PORT=6379

OPENAI_API_KEY=your-openai-api-key
GROQ_API_KEY=your-groq-api-key

DEFAULT_LLM_PROVIDER=openai
DEFAULT_EMBEDDING_PROVIDER=openai
AGENT_MODEL=gpt-4-turbo-preview
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSION=1536
MAX_AGENT_STEPS=5
```

## Step 3: Start the Application

```bash
# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f

# Create superuser
docker-compose exec web python manage.py createsuperuser
```

## Step 4: Test the Deployment

```bash
# Check if services are running
docker-compose ps

# Test API
curl http://localhost:8000/api/rag/tools/

# Test from your local machine
curl http://YOUR_EC2_IP:8000/api/rag/tools/
```

## Step 5: Set Up GitHub Actions Auto-Deploy

### 5.1 Generate SSH Key for Deployment
On your **local machine**:
```bash
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/github_deploy_key
```

### 5.2 Add Public Key to EC2
On **EC2 instance**:
```bash
# Add the public key to authorized_keys
echo "YOUR_PUBLIC_KEY_CONTENT" >> ~/.ssh/authorized_keys
```

### 5.3 Add Secrets to GitHub
Go to your GitHub repo → Settings → Secrets and variables → Actions

Add these secrets:
- `EC2_HOST`: Your EC2 public IP or domain
- `EC2_USER`: `ubuntu` (or `ec2-user` for Amazon Linux)
- `EC2_SSH_KEY`: Content of your **private key** (`github_deploy_key`)

### 5.4 Enable Deployment Workflow
The deploy.yml workflow is already configured for SSH deployment!

## Step 6: Optional - Set Up Nginx Reverse Proxy

```bash
# Install Nginx
sudo apt-get install nginx -y

# Create Nginx config
sudo nano /etc/nginx/sites-available/agentic_rag
```

Add this configuration:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /ws/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

Enable and start:
```bash
sudo ln -s /etc/nginx/sites-available/agentic_rag /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Step 7: Optional - Set Up SSL with Let's Encrypt

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is configured automatically
```

## Maintenance Commands

```bash
# View logs
docker-compose logs -f web

# Restart services
docker-compose restart

# Update to latest version
cd /opt/agentic_rag
git pull
docker-compose pull
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate

# Backup database
docker-compose exec db pg_dump -U postgres agentic_rag > backup.sql
```

## Troubleshooting

### Service won't start
```bash
docker-compose down -v
docker-compose up -d
docker-compose logs
```

### Port already in use
```bash
# Check what's using port 8000
sudo lsof -i :8000
sudo kill -9 PID
```

### Out of disk space
```bash
# Clean up Docker
docker system prune -a
```

## Monitoring

```bash
# Install monitoring tools
sudo apt-get install htop ncdu -y

# Monitor resources
htop

# Check disk usage
df -h
ncdu /
```

Your Agentic RAG system is now deployed on EC2! 🚀

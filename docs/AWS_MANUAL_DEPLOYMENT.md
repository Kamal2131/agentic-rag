# AWS Manual Deployment Guide - Agentic RAG

> **Step-by-step guide to manually deploy your agentic RAG system on AWS EC2**

---

## 🎯 What We'll Deploy

- **EC2 Instance** running Docker Compose
- **PostgreSQL** (container)
- **Qdrant** (container)
- **Redis** (container)
- **Your Django App** (from ECR)
- **Public URL** to access the API

---

## 📋 Prerequisites

Before starting:
- ✅ AWS Account with admin access
- ✅ Your ECR image: `061378098762.dkr.ecr.ap-south-1.amazonaws.com/agentic-rag:latest`
- ✅ API Keys: OpenAI, Serper (for web search)
- ✅ SSH key pair for EC2 access

---

## 🚀 Step-by-Step Deployment

### **Step 1: Launch EC2 Instance**

#### **1.1 Go to EC2 Console**
- Navigate to: https://console.aws.amazon.com/ec2
- Click **"Launch Instance"**

#### **1.2 Configure Instance**

**Name**: `agentic-rag-server`

**AMI**: Ubuntu Server 22.04 LTS (Free tier eligible)

**Instance Type**: 
- Minimum: `t3.medium` (4GB RAM)
- Recommended: `t3.large` (8GB RAM) for better performance

**Key Pair**: 
- Create new or select existing
- Download `.pem` file if new

**Network Settings**:
- Create security group with these rules:
  - SSH (22) - Your IP only
  - HTTP (80) - Anywhere (0.0.0.0/0)
  - HTTPS (443) - Anywhere (0.0.0.0/0)
  - Custom TCP (8000) - Anywhere (0.0.0.0/0) - For API

**Storage**: 
- 30 GB gp3 SSD (minimum)
- 50 GB recommended for logs and data

#### **1.3 Launch Instance**
- Click **"Launch Instance"**
- Wait for instance to be running
- Note the **Public IP address**

---

### **Step 2: Connect to EC2**

#### **Windows (PowerShell)**:
```powershell
# Set permissions on key file
icacls "path\to\your-key.pem" /inheritance:r
icacls "path\to\your-key.pem" /grant:r "%username%:R"

# Connect via SSH
ssh -i "path\to\your-key.pem" ubuntu@<YOUR-EC2-PUBLIC-IP>
```

#### **Mac/Linux**:
```bash
chmod 400 your-key.pem
ssh -i your-key.pem ubuntu@<YOUR-EC2-PUBLIC-IP>
```

---

### **Step 3: Install Docker & Docker Compose**

Once connected to EC2, run these commands:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add ubuntu user to docker group
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.23.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version

# Log out and back in for group changes
exit
```

**Reconnect to EC2** after this step.

---

### **Step 4: Install AWS CLI & Configure**

```bash
# Install AWS CLI
sudo apt install -y awscli

# Configure AWS credentials
aws configure
```

Enter:
- **AWS Access Key ID**: (your access key)
- **AWS Secret Access Key**: (your secret key)
- **Default region**: `ap-south-1`
- **Default output format**: `json`

---

### **Step 5: Login to ECR**

```bash
# Login to your ECR registry
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin 061378098762.dkr.ecr.ap-south-1.amazonaws.com
```

Should see: `Login Succeeded`

---

### **Step 6: Create Project Directory**

```bash
# Create project directory
mkdir -p ~/agentic-rag
cd ~/agentic-rag

# Create .env file
nano .env
```

Paste this configuration (replace with your actual keys):

```env
# Django Settings
SECRET_KEY=your-super-secret-key-change-this-in-production
DEBUG=False
ALLOWED_HOSTS=*

# Database
DB_NAME=agentic_rag
DB_USER=postgres
DB_PASSWORD=SecurePassword123!
DB_HOST=db
DB_PORT=5432

# Qdrant
QDRANT_HOST=qdrant
QDRANT_PORT=6333

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# LLM Settings
OPENAI_API_KEY=sk-proj-your-actual-openai-key
GROQ_API_KEY=gsk_your-actual-groq-key
DEFAULT_LLM_PROVIDER=openai

# Serper API (Web Search)
SERPER_API_KEY=your-actual-serper-api-key

# Embedding
DEFAULT_EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSION=1536

# Agent
MAX_AGENT_STEPS=5
AGENT_MODEL=gpt-4-turbo-preview
```

Press `Ctrl+X`, then `Y`, then `Enter` to save.

---

### **Step 7: Create docker-compose.yml**

```bash
```

Paste this:

```yaml
version: '3.8'

services:
  # PostgreSQL database
  db:
    image: postgres:15-alpine
    container_name: agentic_rag_db
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  # Qdrant vector database
  qdrant:
    image: qdrant/qdrant:latest
    container_name: agentic_rag_qdrant
    volumes:
      - qdrant_data:/qdrant/storage
    healthcheck:
      test: timeout 10 bash -c ':> /dev/tcp/127.0.0.1/6333' || exit 1
      interval: 5s
      timeout: 10s
      retries: 5
    restart: unless-stopped

  # Redis
  redis:
    image: redis:7-alpine
    container_name: agentic_rag_redis
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  # Django application (from ECR)
  web:
    image: 061378098762.dkr.ecr.ap-south-1.amazonaws.com/agentic-rag:latest
    container_name: agentic_rag_web
    command: sh -c "python manage.py makemigrations && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      db:
        condition: service_healthy
      qdrant:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health/"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 30s
    restart: unless-stopped

volumes:
  postgres_data:
  qdrant_data:
```

Save with `Ctrl+X`, `Y`, `Enter`.

---

### **Step 8: Pull Images & Start Services**

```bash
# Pull your application image from ECR
docker pull 061378098762.dkr.ecr.ap-south-1.amazonaws.com/agentic-rag:latest

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f web
```

Wait for:
- ✅ Migrations to complete
- ✅ Server running message
- ✅ All containers healthy

Press `Ctrl+C` to stop viewing logs.

---

### **Step 9: Verify Deployment**

#### **Check Health Endpoint**:
```bash
curl http://localhost:8000/health/
```

Should return:
```json
{
  "status": "healthy",
  "services": {
    "database": "up",
    "qdrant": "up",
    "redis": "up"
  }
}
```

#### **Test from Your Local Machine**:
```bash
curl http://<EC2-PUBLIC-IP>:8000/health/
```

---

### **Step 10: Test the API**

#### **Query Endpoint**:
```bash
curl -X POST http://<EC2-PUBLIC-IP>:8000/api/rag/query/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the latest AI trends in 2024?"
  }'
```

Should return AI-generated response with web search results!

---

## 🌐 Access Your Application

### **API Documentation**:
- Swagger UI: `http://<EC2-PUBLIC-IP>:8000/api/schema/swagger-ui/`
- ReDoc: `http://<EC2-PUBLIC-IP>:8000/api/schema/redoc/`

### **Health Check**:
- `http://<EC2-PUBLIC-IP>:8000/health/`

### **WebSocket Chat**:
- `ws://<EC2-PUBLIC-IP>:8000/ws/chat/`

---

## 📤 Upload Your Frontend

To use the HTML frontend on the web:

```bash
# On EC2, install nginx
sudo apt install -y nginx

# Copy frontend file
sudo nano /var/www/html/index.html
```

Paste your `frontend-demo.html` content, but update WebSocket URL:
```javascript
const WS_URL = 'ws://<EC2-PUBLIC-IP>:8000/ws/chat/';
const API_URL = 'http://<EC2-PUBLIC-IP>:8000';
```

Save and access: `http://<EC2-PUBLIC-IP>/`

---

## 🔒 Security Improvements (Optional but Recommended)

### **1. Use HTTPS with Let's Encrypt**:
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### **2. Setup Nginx Reverse Proxy**:
```bash
sudo nano /etc/nginx/sites-available/agentic-rag
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /ws/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### **3. Restrict SSH Access**:
In EC2 Security Group, change SSH rule:
- From: `0.0.0.0/0` (anywhere)
- To: Your specific IP address

---

## 🛠️ Useful Commands

### **View Logs**:
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web
```

### **Restart Services**:
```bash
docker-compose restart web
```

### **Stop Everything**:
```bash
docker-compose down
```

### **Update Application**:
```bash
# Pull latest image
docker pull 061378098762.dkr.ecr.ap-south-1.amazonaws.com/agentic-rag:latest

# Restart with new image
docker-compose up -d web
```

---

## 📊 Monitoring

### **Check Container Status**:
```bash
docker ps
docker stats
```

### **Database Backup**:
```bash
docker exec agentic_rag_db pg_dump -U postgres agentic_rag > backup.sql
```

---

## 🎉 You're Live!

Your agentic RAG API is now accessible at:
- **API**: `http://<EC2-PUBLIC-IP>:8000/`
- **Docs**: `http://<EC2-PUBLIC-IP>:8000/api/schema/swagger-ui/`
- **Chat**: `ws://<EC2-PUBLIC-IP>:8000/ws/chat/`

### **Share with others**:
- API endpoint: `http://<EC2-PUBLIC-IP>:8000/api/rag/query/`
- Frontend (if nginx setup): `http://<EC2-PUBLIC-IP>/`

---

## 🔄 Next Steps

Once you verify everything works:
1. ✅ Test all endpoints
2. ✅ Upload some documents to knowledge base
3. ✅ Test web search functionality
4. ✅ Setup domain name (optional)
5. ✅ Enable HTTPS
6. ✅ Setup automated backups
7. ✅ Later: Migrate to ECS/Kubernetes

---

## 💡 Cost Estimate

**Monthly AWS Costs** (approximate):
- EC2 t3.medium: ~$30/month
- EC2 t3.large: ~$60/month
- EBS 50GB: ~$5/month
- Data transfer: ~$5-10/month
- **Total**: ~$40-75/month

**To reduce costs**:
- Use Reserved Instances (save 30-40%)
- Use Spot Instances (save 70%, but can be terminated)
- Stop instance when not in use

---

## 🆘 Troubleshooting

### **Services won't start**:
```bash
docker-compose down
docker-compose up -d
docker-compose logs -f
```

### **Can't connect from browser**:
- Check security group allows port 8000
- Check EC2 public IP is correct
- Try: `curl http://localhost:8000/health/` from EC2

### **Out of memory**:
- Upgrade to t3.large or larger
- Add swap space

### **Update not working**:
```bash
docker-compose pull
docker-compose up -d --force-recreate
```

---

**Ready to start? Follow these steps in order and you'll be live in ~30 minutes! 🚀**

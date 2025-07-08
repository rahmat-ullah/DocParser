# Deployment Guide - Document Parser Web Application

## Overview

This guide provides step-by-step instructions for deploying the Document Parser Web Application in various environments, from local development to production deployment.

## Prerequisites

### System Requirements
- **Node.js**: Version 18.0 or higher
- **Python**: Version 3.8 or higher
- **Memory**: Minimum 4GB RAM (8GB recommended for production)
- **Storage**: At least 2GB free space for dependencies and temporary files
- **Network**: Internet connection for API calls and package downloads

### Required Accounts and Keys
- **OpenAI API Key**: Required for image analysis and content description
- **Deployment Platform Account**: Vercel, Netlify, AWS, or similar (for production)

## Development Environment Setup

### 1. Clone and Setup Repository

```bash
# Clone the repository
git clone <your-repository-url>
cd document-parser-app

# Verify Node.js version
node --version  # Should be 18.0+

# Verify Python version
python --version  # Should be 3.8+
```

### 2. Frontend Setup (Next.js)

```bash
# Install dependencies
npm install

# Create environment file
cp .env.example .env.local

# Edit .env.local with your configuration
nano .env.local
```

**Environment Variables (.env.local):**
```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Application Configuration
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXT_PUBLIC_PROCESSOR_URL=http://localhost:8000

# File Upload Configuration
MAX_FILE_SIZE=52428800  # 50MB in bytes
UPLOAD_DIR=./temp

# Security
NEXTAUTH_SECRET=your_nextauth_secret_here
NEXTAUTH_URL=http://localhost:3000
```

### 3. Backend Setup (Python)

```bash
# Navigate to Python processor directory
cd python-processor

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env

# Edit .env with your configuration
nano .env
```

**Python Environment Variables (.env):**
```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True

# CORS Configuration
ALLOWED_ORIGINS=["http://localhost:3000"]

# File Processing Configuration
MAX_FILE_SIZE=52428800
TEMP_DIR=./temp
PROCESSING_TIMEOUT=300

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/app.log
```

### 4. Start Development Servers

```bash
# Terminal 1: Start Python backend
cd python-processor
source venv/bin/activate  # or venv\Scripts\activate on Windows
python app.py

# Terminal 2: Start Next.js frontend
cd ..  # Back to root directory
npm run dev
```

### 5. Verify Installation

1. **Frontend**: Open http://localhost:3000
2. **Backend**: Open http://localhost:8000/docs (FastAPI documentation)
3. **Health Check**: Visit http://localhost:8000/health

## Production Deployment

### Option 1: Vercel + Railway (Recommended)

#### Deploy Frontend to Vercel

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy
vercel

# Set environment variables in Vercel dashboard
# - OPENAI_API_KEY
# - NEXT_PUBLIC_PROCESSOR_URL (Railway backend URL)
```

#### Deploy Backend to Railway

1. **Create Railway Account**: Sign up at railway.app
2. **Create New Project**: Connect your GitHub repository
3. **Configure Environment Variables**:
   ```env
   OPENAI_API_KEY=your_key_here
   PORT=8000
   ALLOWED_ORIGINS=["https://your-vercel-app.vercel.app"]
   ```
4. **Deploy**: Railway will automatically deploy from your repository

### Option 2: AWS Deployment

#### Frontend (AWS Amplify)

```bash
# Install AWS CLI and Amplify CLI
npm install -g @aws-amplify/cli

# Initialize Amplify
amplify init

# Add hosting
amplify add hosting

# Deploy
amplify publish
```

#### Backend (AWS Lambda + API Gateway)

```bash
# Install Serverless Framework
npm install -g serverless

# Create serverless.yml in python-processor directory
```

**serverless.yml:**
```yaml
service: document-parser-api

provider:
  name: aws
  runtime: python3.9
  region: us-east-1
  environment:
    OPENAI_API_KEY: ${env:OPENAI_API_KEY}

functions:
  process:
    handler: app.handler
    timeout: 300
    memorySize: 1024
    events:
      - http:
          path: /{proxy+}
          method: ANY
          cors: true

plugins:
  - serverless-python-requirements
```

```bash
# Deploy
serverless deploy
```

### Option 3: Docker Deployment

#### Create Docker Files

**Frontend Dockerfile:**
```dockerfile
# Dockerfile
FROM node:18-alpine AS base

# Install dependencies only when needed
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

RUN npm run build

# Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public

COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000

CMD ["node", "server.js"]
```

**Backend Dockerfile:**
```dockerfile
# python-processor/Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create temp directory
RUN mkdir -p temp logs

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Docker Compose:**
```yaml
# docker-compose.yml
version: '3.8'

services:
  frontend:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_PROCESSOR_URL=http://backend:8000
    depends_on:
      - backend

  backend:
    build: ./python-processor
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ALLOWED_ORIGINS=["http://localhost:3000"]
    volumes:
      - ./python-processor/temp:/app/temp
      - ./python-processor/logs:/app/logs
```

```bash
# Deploy with Docker Compose
docker-compose up -d
```

### Option 4: Traditional Server Deployment

#### Setup Production Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Python
sudo apt install python3 python3-pip python3-venv -y

# Install Nginx
sudo apt install nginx -y

# Install PM2 for process management
sudo npm install -g pm2
```

#### Deploy Application

```bash
# Clone repository
git clone <your-repository-url>
cd document-parser-app

# Setup frontend
npm install
npm run build

# Setup backend
cd python-processor
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn

# Create PM2 ecosystem file
```

**ecosystem.config.js:**
```javascript
module.exports = {
  apps: [
    {
      name: 'document-parser-frontend',
      script: 'npm',
      args: 'start',
      cwd: '/path/to/document-parser-app',
      env: {
        NODE_ENV: 'production',
        PORT: 3000
      }
    },
    {
      name: 'document-parser-backend',
      script: 'gunicorn',
      args: 'app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000',
      cwd: '/path/to/document-parser-app/python-processor',
      interpreter: '/path/to/document-parser-app/python-processor/venv/bin/python'
    }
  ]
};
```

```bash
# Start applications with PM2
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

#### Configure Nginx

```nginx
# /etc/nginx/sites-available/document-parser
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api/processor/ {
        proxy_pass http://localhost:8000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Increase timeout for large file processing
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # File upload size limit
    client_max_body_size 50M;
}
```

```bash
# Enable site and restart Nginx
sudo ln -s /etc/nginx/sites-available/document-parser /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## SSL/HTTPS Setup

### Using Certbot (Let's Encrypt)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## Monitoring and Maintenance

### Health Checks

```bash
# Create health check script
cat > health_check.sh << 'EOF'
#!/bin/bash

# Check frontend
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "Frontend: OK"
else
    echo "Frontend: FAILED"
    pm2 restart document-parser-frontend
fi

# Check backend
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "Backend: OK"
else
    echo "Backend: FAILED"
    pm2 restart document-parser-backend
fi
EOF

chmod +x health_check.sh

# Add to crontab for regular checks
crontab -e
# Add: */5 * * * * /path/to/health_check.sh
```

### Log Management

```bash
# Setup log rotation
sudo nano /etc/logrotate.d/document-parser

# Add configuration:
/path/to/document-parser-app/python-processor/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        pm2 reload document-parser-backend
    endscript
}
```

### Backup Strategy

```bash
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash

BACKUP_DIR="/backups/document-parser"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup application files
tar -czf $BACKUP_DIR/app_$DATE.tar.gz /path/to/document-parser-app

# Backup logs
tar -czf $BACKUP_DIR/logs_$DATE.tar.gz /path/to/document-parser-app/python-processor/logs

# Clean old backups (keep last 30 days)
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
EOF

chmod +x backup.sh

# Schedule daily backups
crontab -e
# Add: 0 2 * * * /path/to/backup.sh
```

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Find process using port
   sudo lsof -i :3000
   sudo lsof -i :8000
   
   # Kill process
   sudo kill -9 <PID>
   ```

2. **Permission Errors**
   ```bash
   # Fix file permissions
   sudo chown -R $USER:$USER /path/to/document-parser-app
   chmod -R 755 /path/to/document-parser-app
   ```

3. **Memory Issues**
   ```bash
   # Increase swap space
   sudo fallocate -l 2G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

4. **OpenAI API Errors**
   - Verify API key is correct
   - Check API usage limits
   - Ensure proper environment variable setup

### Performance Optimization

1. **Frontend Optimization**
   ```bash
   # Enable compression in Next.js
   # Add to next.config.js:
   compress: true,
   
   # Use CDN for static assets
   # Configure in next.config.js:
   assetPrefix: 'https://your-cdn.com',
   ```

2. **Backend Optimization**
   ```bash
   # Increase worker processes
   gunicorn app:app -w 8 -k uvicorn.workers.UvicornWorker
   
   # Use Redis for caching (optional)
   pip install redis
   ```

3. **Database Optimization** (if using database)
   ```bash
   # PostgreSQL optimization
   sudo nano /etc/postgresql/13/main/postgresql.conf
   # Adjust: shared_buffers, work_mem, maintenance_work_mem
   ```

## Security Considerations

### Environment Security
- Never commit API keys to version control
- Use environment variables for all sensitive data
- Regularly rotate API keys and secrets
- Implement rate limiting for API endpoints

### Network Security
- Use HTTPS in production
- Configure proper CORS settings
- Implement firewall rules
- Regular security updates

### File Upload Security
- Validate file types and sizes
- Scan uploaded files for malware
- Use temporary storage with cleanup
- Implement user authentication for sensitive deployments

This deployment guide provides comprehensive instructions for various deployment scenarios. Choose the option that best fits your infrastructure requirements and technical expertise.


# Production Deployment Guide

Comprehensive guide for deploying the Pet Roasts backend to production.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Pre-Deployment Checklist](#pre-deployment-checklist)
3. [Server Setup](#server-setup)
4. [Application Deployment](#application-deployment)
5. [Monitoring & Logging](#monitoring--logging)
6. [Backup & Recovery](#backup--recovery)
7. [Scaling Considerations](#scaling-considerations)

## System Requirements

### Minimum Requirements

- **OS**: Ubuntu 20.04+ / Debian 11+ / CentOS 8+
- **CPU**: 4 cores (8+ recommended for FULL IndicTrans2 mode)
- **RAM**: 8GB minimum (16GB+ recommended)
- **Disk**: 20GB available (for IndicTrans2 models and logs)
- **Network**: 100Mbps+ bandwidth

### Software Stack

- **Python**: 3.12+
- **Redis**: 7.0+ (for persistent job storage)
- **Nginx**: 1.18+ (reverse proxy)
- **Systemd**: For process management
- **Certbot**: For SSL certificates (Let's Encrypt)

## Pre-Deployment Checklist

### 1. Environment Configuration

```bash
# Copy and configure .env file
cp .env.example .env

# Required changes for production:
# - Set INDICTRANS_MODE=full
# - Set USE_REDIS=true
# - Configure REVID_WEBHOOK_SECRET
# - Set proper REDIS_JOB_TTL_SECONDS
# - Update CORS origins in code if needed
```

### 2. API Keys

- [ ] Revid.ai API key configured: `e83c77db-548d-47ab-a067-21dbd72e8ad2`
- [ ] Revid webhook secret generated and set
- [ ] AI4Bharat credentials (if required)

### 3. Security

- [ ] Strong webhook secret (32+ characters)
- [ ] HTTPS enabled for all external endpoints
- [ ] Firewall configured (only expose 80/443)
- [ ] Rate limiting configured on reverse proxy
- [ ] CORS origins restricted to production domains

### 4. Dependencies

- [ ] Redis server installed and running
- [ ] IndicTrans2 models downloaded (~800MB)
- [ ] Python virtual environment created
- [ ] All pip dependencies installed

## Server Setup

### 1. Install System Dependencies

```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install required packages
sudo apt-get install -y \
    python3.12 \
    python3.12-venv \
    python3-pip \
    redis-server \
    nginx \
    git \
    curl \
    certbot \
    python3-certbot-nginx

# Verify installations
python3.12 --version
redis-cli --version
nginx -v
```

### 2. Configure Redis

```bash
# Edit Redis configuration
sudo nano /etc/redis/redis.conf

# Key settings for production:
# maxmemory 2gb
# maxmemory-policy allkeys-lru
# save 900 1
# save 300 10
# appendonly yes

# Restart Redis
sudo systemctl restart redis-server
sudo systemctl enable redis-server

# Verify Redis is running
redis-cli ping  # Should return PONG
```

### 3. Create Application User

```bash
# Create dedicated user (no sudo privileges)
sudo useradd -m -s /bin/bash petroasts
sudo su - petroasts
```

### 4. Clone Repository

```bash
# As petroasts user
cd ~
git clone https://github.com/yourusername/pet_roasts.git
cd pet_roasts

# Or copy files if deploying from local
```

## Application Deployment

### 1. Set Up Python Environment

```bash
# Create virtual environment
python3.12 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Install IndicTrans2

```bash
# Clone IndicTrans2
git clone https://github.com/AI4Bharat/IndicTrans2.git
cd IndicTrans2

# Install
pip install --editable ./

# Download models (first run in FULL mode)
cd ~/pet_roasts
INDICTRANS_MODE=full python IndicTrans2/inference_server_simple.py &

# Wait for model download (~800MB), then stop
# Models are cached in ~/.cache/huggingface/
```

### 3. Configure Environment

```bash
# Edit .env file
nano .env

# Production settings:
INDICTRANS_MODE=full
USE_REDIS=true
REDIS_URL=redis://localhost:6379/0
REDIS_JOB_TTL_SECONDS=604800
REVID_API_KEY=e83c77db-548d-47ab-a067-21dbd72e8ad2
REVID_WEBHOOK_SECRET=<generate-secure-secret>
MAX_RETRIES=3
RETRY_BACKOFF_FACTOR=1.5
```

### 4. Create Systemd Services

#### Backend Service

```bash
# Create service file
sudo nano /etc/systemd/system/petroasts-backend.service
```

```ini
[Unit]
Description=Pet Roasts FastAPI Backend
After=network.target redis-server.service
Requires=redis-server.service

[Service]
Type=simple
User=petroasts
WorkingDirectory=/home/petroasts/pet_roasts
Environment="PATH=/home/petroasts/pet_roasts/.venv/bin"
ExecStart=/home/petroasts/pet_roasts/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 4
Restart=always
RestartSec=10
StandardOutput=append:/var/log/petroasts/backend.log
StandardError=append:/var/log/petroasts/backend-error.log

[Install]
WantedBy=multi-user.target
```

#### IndicTrans2 Service

```bash
# Create service file
sudo nano /etc/systemd/system/petroasts-indictrans.service
```

```ini
[Unit]
Description=Pet Roasts IndicTrans2 Translation Server
After=network.target

[Service]
Type=simple
User=petroasts
WorkingDirectory=/home/petroasts/pet_roasts/IndicTrans2
Environment="PATH=/home/petroasts/pet_roasts/.venv/bin"
Environment="INDICTRANS_MODE=full"
ExecStart=/home/petroasts/pet_roasts/.venv/bin/python inference_server_simple.py
Restart=always
RestartSec=10
StandardOutput=append:/var/log/petroasts/indictrans.log
StandardError=append:/var/log/petroasts/indictrans-error.log

[Install]
WantedBy=multi-user.target
```

#### Create Log Directory

```bash
sudo mkdir -p /var/log/petroasts
sudo chown petroasts:petroasts /var/log/petroasts
```

#### Enable and Start Services

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable services (start on boot)
sudo systemctl enable petroasts-indictrans.service
sudo systemctl enable petroasts-backend.service

# Start services
sudo systemctl start petroasts-indictrans.service
sudo systemctl start petroasts-backend.service

# Check status
sudo systemctl status petroasts-indictrans.service
sudo systemctl status petroasts-backend.service

# View logs
sudo journalctl -u petroasts-backend.service -f
sudo journalctl -u petroasts-indictrans.service -f
```

### 5. Configure Nginx Reverse Proxy

```bash
# Create Nginx configuration
sudo nano /etc/nginx/sites-available/petroasts
```

```nginx
# Rate limiting
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

upstream backend {
    server 127.0.0.1:8000;
    keepalive 32;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Let's Encrypt challenge
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    # Redirect to HTTPS
    location / {
        return 301 https://$server_name$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL certificates (will be configured by certbot)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Logging
    access_log /var/log/nginx/petroasts-access.log;
    error_log /var/log/nginx/petroasts-error.log;

    # Rate limiting
    location /api/ {
        limit_req zone=api_limit burst=20 nodelay;

        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Health check (no rate limit)
    location /healthz {
        proxy_pass http://backend;
        access_log off;
    }

    # Static files (if any)
    location /static/ {
        alias /home/petroasts/pet_roasts/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

#### Enable Site and Configure SSL

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/petroasts /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Obtain SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Reload Nginx
sudo systemctl reload nginx

# Enable auto-renewal
sudo systemctl enable certbot.timer
```

### 6. Configure Firewall

```bash
# Install UFW (if not already installed)
sudo apt-get install -y ufw

# Allow SSH
sudo ufw allow OpenSSH

# Allow HTTP and HTTPS
sudo ufw allow 'Nginx Full'

# Deny direct access to backend
sudo ufw deny 8000
sudo ufw deny 5000

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

## Monitoring & Logging

### 1. Log Rotation

```bash
# Create logrotate configuration
sudo nano /etc/logrotate.d/petroasts
```

```
/var/log/petroasts/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 petroasts petroasts
    sharedscripts
    postrotate
        systemctl reload petroasts-backend.service > /dev/null
        systemctl reload petroasts-indictrans.service > /dev/null
    endscript
}
```

### 2. Health Monitoring Script

```bash
# Create monitoring script
nano ~/monitor.sh
```

```bash
#!/bin/bash

# Check backend health
if ! curl -f http://localhost:8000/healthz > /dev/null 2>&1; then
    echo "Backend health check failed"
    systemctl restart petroasts-backend.service
fi

# Check IndicTrans2
if ! curl -f http://localhost:5000/healthz > /dev/null 2>&1; then
    echo "IndicTrans2 health check failed"
    systemctl restart petroasts-indictrans.service
fi

# Check Redis
if ! redis-cli ping > /dev/null 2>&1; then
    echo "Redis health check failed"
    systemctl restart redis-server
fi
```

```bash
# Make executable
chmod +x ~/monitor.sh

# Add to crontab (run every 5 minutes)
crontab -e
# Add line:
*/5 * * * * /home/petroasts/monitor.sh >> /var/log/petroasts/monitor.log 2>&1
```

### 3. Resource Monitoring

```bash
# Install monitoring tools
sudo apt-get install -y htop iotop nethogs

# Monitor processes
htop

# Monitor Redis
redis-cli info stats
redis-cli info memory

# Monitor disk usage
df -h
du -sh /home/petroasts/pet_roasts/
```

## Backup & Recovery

### 1. Redis Backup

```bash
# Manual backup
redis-cli BGSAVE

# Automated daily backup
sudo nano /etc/cron.daily/redis-backup
```

```bash
#!/bin/bash
BACKUP_DIR="/home/petroasts/backups/redis"
mkdir -p "$BACKUP_DIR"
redis-cli BGSAVE
sleep 5
cp /var/lib/redis/dump.rdb "$BACKUP_DIR/dump-$(date +%Y%m%d).rdb"
find "$BACKUP_DIR" -name "dump-*.rdb" -mtime +7 -delete
```

```bash
sudo chmod +x /etc/cron.daily/redis-backup
```

### 2. Application Code Backup

```bash
# Git-based backup (recommended)
cd ~/pet_roasts
git add .
git commit -m "Production snapshot"
git push origin production

# File-based backup
tar -czf ~/backups/petroasts-$(date +%Y%m%d).tar.gz ~/pet_roasts
```

### 3. Recovery Procedures

**Restore Redis Data:**
```bash
sudo systemctl stop redis-server
sudo cp /home/petroasts/backups/redis/dump-YYYYMMDD.rdb /var/lib/redis/dump.rdb
sudo chown redis:redis /var/lib/redis/dump.rdb
sudo systemctl start redis-server
```

**Rollback Application:**
```bash
cd ~/pet_roasts
git checkout <previous-commit-hash>
sudo systemctl restart petroasts-backend.service
sudo systemctl restart petroasts-indictrans.service
```

## Scaling Considerations

### 1. Horizontal Scaling

**Load Balancer Configuration (Nginx):**
```nginx
upstream backend {
    least_conn;  # Load balancing method
    server 10.0.0.1:8000;
    server 10.0.0.2:8000;
    server 10.0.0.3:8000;
    keepalive 32;
}
```

**Shared Redis Instance:**
- All backend instances must connect to same Redis server
- Update `REDIS_URL` to point to central Redis instance
- Consider Redis Cluster for high availability

### 2. Redis Scaling

**Redis Sentinel (High Availability):**
```bash
# Configure master-slave replication
# See: https://redis.io/docs/management/sentinel/
```

**Redis Cluster (Horizontal Scaling):**
```bash
# For distributed data across multiple nodes
# See: https://redis.io/docs/management/scaling/
```

### 3. IndicTrans2 Scaling

- Deploy multiple IndicTrans2 instances on different ports (5000, 5001, 5002)
- Update backend to round-robin across instances
- Use GPU instances for faster inference

### 4. Database Optimization

**Redis Memory Optimization:**
```bash
# In redis.conf
maxmemory-policy allkeys-lru  # Evict least recently used keys
maxmemory 2gb                 # Limit memory usage
```

**Connection Pooling:**
- Already configured in `RedisJobStore` via `redis.asyncio`
- Adjust pool size in code if needed

## Performance Tuning

### 1. Uvicorn Workers

```bash
# In systemd service file
ExecStart=... --workers 4  # CPU cores * 2
```

### 2. Redis Configuration

```bash
# /etc/redis/redis.conf
tcp-backlog 511
timeout 0
tcp-keepalive 300
```

### 3. Nginx Tuning

```nginx
# /etc/nginx/nginx.conf
worker_processes auto;
worker_connections 1024;
keepalive_timeout 65;
client_max_body_size 10M;  # For image uploads
```

## Security Best Practices

1. **Secrets Management**
   - Use environment variables for secrets
   - Never commit `.env` to git
   - Rotate API keys periodically

2. **Network Security**
   - Firewall: Only expose 80/443
   - Redis: Bind to localhost only
   - IndicTrans2: Bind to localhost only

3. **Application Security**
   - Webhook signature verification enabled
   - CORS origins restricted
   - Rate limiting on API endpoints
   - HTTPS enforced for all traffic

4. **System Security**
   - Regular security updates: `sudo apt-get update && sudo apt-get upgrade`
   - SSH key-based authentication (disable password auth)
   - Fail2ban for intrusion prevention

## Troubleshooting

### Service Not Starting

```bash
# Check logs
sudo journalctl -u petroasts-backend.service -xe
sudo journalctl -u petroasts-indictrans.service -xe

# Check Redis
sudo systemctl status redis-server
redis-cli ping

# Check permissions
ls -la /home/petroasts/pet_roasts/
```

### High Memory Usage

```bash
# Check Redis memory
redis-cli info memory

# Check IndicTrans2 memory (can be high due to models)
ps aux | grep inference_server_simple

# Consider:
# - Reducing REDIS_JOB_TTL_SECONDS
# - Running IndicTrans2 on dedicated server
```

### Slow Response Times

```bash
# Check Nginx logs
tail -f /var/log/nginx/petroasts-access.log

# Check backend performance
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/healthz

# Profile with:
pip install py-spy
sudo py-spy top --pid <backend-pid>
```

## Post-Deployment Validation

```bash
# 1. Health check
curl https://yourdomain.com/healthz

# 2. Translation API
curl -X POST https://yourdomain.com/api/translate-text \
  -H "Content-Type: application/json" \
  -d '{"text": "Test", "source_language": "en", "target_language": "hi"}'

# 3. Check Redis keys
redis-cli KEYS "pet_roast:*"

# 4. Monitor logs
tail -f /var/log/petroasts/backend.log
```

## Support

For deployment issues:
1. Check logs: `/var/log/petroasts/`
2. Verify services: `sudo systemctl status petroasts-*`
3. Test endpoints: `curl` commands above
4. Review this guide's troubleshooting section

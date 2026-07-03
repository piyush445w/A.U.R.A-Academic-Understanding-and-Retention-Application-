# Deployment Guide

## Intelligent Student Risk Monitoring & Decision Support System

This guide provides comprehensive instructions for deploying the Student Risk Monitoring System to production environments.

---

## 📋 Table of Contents

1. [Server Requirements](#server-requirements)
2. [Nginx Configuration](#nginx-configuration)
3. [Gunicorn Setup](#gunicorn-setup)
4. [SSL Certificate](#ssl-certificate)
5. [Database Backup](#database-backup)
6. [Monitoring](#monitoring)
7. [Docker Deployment](#docker-deployment)
8. [Security Best Practices](#security-best-practices)
9. [Performance Optimization](#performance-optimization)

---

## Server Requirements

### Minimum Requirements

| Component | Specification |
|-----------|---------------|
| **CPU** | 2 cores (4 cores recommended) |
| **RAM** | 4GB (8GB recommended) |
| **Storage** | 20GB SSD (50GB recommended) |
| **OS** | Ubuntu 20.04 LTS or CentOS 8+ |
| **Network** | Static IP address |
| **Bandwidth** | 100 Mbps minimum |

### Recommended Cloud Providers

| Provider | Instance Type | Monthly Cost (Est.) |
|----------|---------------|---------------------|
| AWS | t3.medium | $30-40 |
| DigitalOcean | 2vCPU/4GB | $24 |
| Google Cloud | e2-medium | $25-35 |
| Azure | B2s | $30-40 |
| Linode | 2vCPU/4GB | $24 |

### Software Stack

| Software | Version | Purpose |
|----------|---------|---------|
| Ubuntu | 20.04 LTS | Operating System |
| Python | 3.8+ | Runtime |
| MySQL | 8.0+ | Database |
| Nginx | 1.18+ | Web Server |
| Gunicorn | 21.2+ | WSGI Server |
| Certbot | Latest | SSL Certificates |
| Supervisor | Latest | Process Management |

---

## Server Setup

### 1. Initial Server Configuration

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install essential packages
sudo apt install -y software-properties-common curl wget git

# Set timezone
sudo timedatectl set-timezone Asia/Kolkata

# Create deployment user
sudo adduser deploy
sudo usermod -aG sudo deploy

# Switch to deploy user
su - deploy
```

### 2. Install Required Software

```bash
# Install Python and pip
sudo apt install -y python3.8 python3.8-venv python3.8-dev python3-pip

# Install MySQL
sudo apt install -y mysql-server mysql-client

# Install Nginx
sudo apt install -y nginx

# Install Supervisor
sudo apt install -y supervisor

# Install Certbot
sudo apt install -y certbot python3-certbot-nginx
```

### 3. Configure MySQL

```bash
# Secure MySQL installation
sudo mysql_secure_installation

# Login to MySQL
sudo mysql -u root -p

# Create database and user
CREATE DATABASE student_risk_monitoring CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'deploy_user'@'localhost' IDENTIFIED BY 'strong_password_here';
GRANT ALL PRIVILEGES ON student_risk_monitoring.* TO 'deploy_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 4. Deploy Application

```bash
# Create application directory
sudo mkdir -p /var/www/student-risk-monitoring
sudo chown deploy:deploy /var/www/student-risk-monitoring

# Clone repository
cd /var/www/student-risk-monitoring
git clone <repository-url> .

# Create virtual environment
python3.8 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# Configure environment
cp .env.example .env
nano .env
```

### 5. Configure Environment Variables

```env
# Production Environment Configuration
FLASK_APP=main.py
FLASK_ENV=production
SECRET_KEY=your-production-secret-key-very-long-and-secure

# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_NAME=student_risk_monitoring
DB_USER=deploy_user
DB_PASSWORD=strong_password_here

# ML Model Configuration
MODEL_PATH=/var/www/student-risk-monitoring/models/risk_model_v1.pkl
MODEL_VERSION=1.0

# Application Settings
DEBUG=False
TESTING=False
LOG_LEVEL=WARNING

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### 6. Initialize Application

```bash
# Setup database
python setup_database.py

# Seed initial data
python seed_data.py

# Train ML model
python train_initial_model.py

# Collect static files (if applicable)
# Flask serves static files automatically in development
```

---

## Nginx Configuration

### 1. Create Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/student-risk-monitoring
```

### 2. Nginx Configuration File

```nginx
# /etc/nginx/sites-available/student-risk-monitoring

upstream student_risk_app {
    server 127.0.0.1:8000;
    # Add more servers for load balancing if needed
    # server 127.0.0.1:8001;
    # server 127.0.0.1:8002;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Root directory
    root /var/www/student-risk-monitoring;

    # Logging
    access_log /var/log/nginx/student-risk-monitoring.access.log;
    error_log /var/log/nginx/student-risk-monitoring.error.log;

    # Static files
    location /static/ {
        alias /var/www/student-risk-monitoring/app/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files (if any)
    location /media/ {
        alias /var/www/student-risk-monitoring/media/;
        expires 30d;
    }

    # Favicon
    location /favicon.ico {
        alias /var/www/student-risk-monitoring/app/static/favicon.ico;
        access_log off;
        log_not_found off;
    }

    # Robots.txt
    location /robots.txt {
        alias /var/www/student-risk-monitoring/app/static/robots.txt;
        access_log off;
        log_not_found off;
    }

    # Proxy to Gunicorn
    location / {
        proxy_pass http://student_risk_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;

        # Buffer settings
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }

    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }

    # Deny access to sensitive files
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }

    location ~ \.(env|git|gitignore|md)$ {
        deny all;
        access_log off;
        log_not_found off;
    }

    # File upload size
    client_max_body_size 10M;
}
```

### 3. Enable Nginx Configuration

```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/student-risk-monitoring /etc/nginx/sites-enabled/

# Remove default configuration
sudo rm /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx

# Enable Nginx to start on boot
sudo systemctl enable nginx
```

### 4. Verify Nginx

```bash
# Check Nginx status
sudo systemctl status nginx

# Check Nginx logs
sudo tail -f /var/log/nginx/student-risk-monitoring.access.log
sudo tail -f /var/log/nginx/student-risk-monitoring.error.log
```

---

## Gunicorn Setup

### 1. Create Gunicorn Configuration

```bash
nano /var/www/student-risk-monitoring/gunicorn_config.py
```

### 2. Gunicorn Configuration File

```python
# /var/www/student-risk-monitoring/gunicorn_config.py

import multiprocessing
import os

# Server socket
bind = "127.0.0.1:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "student_risk_monitoring"

# Server mechanics
daemon = False
pidfile = "/var/run/gunicorn/student_risk_monitoring.pid"
umask = 0o007
tmp_upload_dir = None

# SSL (if not using Nginx for SSL)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

# Environment variables
raw_env = [
    "FLASK_ENV=production",
]
```

### 3. Create Log Directory

```bash
sudo mkdir -p /var/log/gunicorn
sudo chown deploy:deploy /var/log/gunicorn
```

### 4. Test Gunicorn

```bash
cd /var/www/student-risk-monitoring
source venv/bin/activate

# Test Gunicorn
gunicorn --config gunicorn_config.py main:app

# Press Ctrl+C to stop
```

---

## Supervisor Configuration

### 1. Create Supervisor Configuration

```bash
sudo nano /etc/supervisor/conf.d/student-risk-monitoring.conf
```

### 2. Supervisor Configuration File

```ini
; /etc/supervisor/conf.d/student-risk-monitoring.conf

[program:student-risk-monitoring]
command=/var/www/student-risk-monitoring/venv/bin/gunicorn --config /var/www/student-risk-monitoring/gunicorn_config.py main:app
directory=/var/www/student-risk-monitoring
user=deploy
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/supervisor/student-risk-monitoring.log
stdout_logfile_maxbytes=10MB
stdout_logfile_backups=10
environment=
    FLASK_ENV="production",
    SECRET_KEY="your-production-secret-key",
    DB_HOST="localhost",
    DB_PORT="3306",
    DB_NAME="student_risk_monitoring",
    DB_USER="deploy_user",
    DB_PASSWORD="strong_password_here"
```

### 3. Enable Supervisor

```bash
# Create log directory
sudo mkdir -p /var/log/supervisor

# Update Supervisor
sudo supervisorctl reread
sudo supervisorctl update

# Start application
sudo supervisorctl start student-risk-monitoring

# Check status
sudo supervisorctl status student-risk-monitoring

# View logs
sudo tail -f /var/log/supervisor/student-risk-monitoring.log
```

### 4. Supervisor Commands

```bash
# Start application
sudo supervisorctl start student-risk-monitoring

# Stop application
sudo supervisorctl stop student-risk-monitoring

# Restart application
sudo supervisorctl restart student-risk-monitoring

# Check status
sudo supervisorctl status

# View all logs
sudo supervisorctl tail -f student-risk-monitoring
```

---

## SSL Certificate

### 1. Obtain SSL Certificate with Let's Encrypt

```bash
# Stop Nginx temporarily
sudo systemctl stop nginx

# Obtain certificate
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Start Nginx
sudo systemctl start nginx
```

### 2. Auto-Renewal Setup

```bash
# Test renewal
sudo certbot renew --dry-run

# Create renewal cron job
sudo crontab -e

# Add this line:
0 3 * * * certbot renew --quiet --post-hook "systemctl reload nginx"
```

### 3. Verify SSL

```bash
# Check certificate
sudo certbot certificates

# Test SSL configuration
# Visit: https://www.ssllabs.com/ssltest/analyze.html?d=yourdomain.com
```

---

## Database Backup

### 1. Automated Backup Script

```bash
nano /var/www/student-risk-monitoring/backup_db.sh
```

```bash
#!/bin/bash
# /var/www/student-risk-monitoring/backup_db.sh

# Configuration
BACKUP_DIR="/var/backups/mysql"
DB_NAME="student_risk_monitoring"
DB_USER="deploy_user"
DB_PASSWORD="strong_password_here"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/${DB_NAME}_${DATE}.sql"
RETENTION_DAYS=30

# Create backup directory
mkdir -p $BACKUP_DIR

# Create backup
mysqldump -u $DB_USER -p$DB_PASSWORD $DB_NAME > $BACKUP_FILE

# Compress backup
gzip $BACKUP_FILE

# Remove old backups
find $BACKUP_DIR -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete

# Log backup
echo "Backup completed: ${BACKUP_FILE}.gz" >> /var/log/mysql_backup.log
```

### 2. Make Script Executable

```bash
chmod +x /var/www/student-risk-monitoring/backup_db.sh
```

### 3. Schedule Automated Backups

```bash
# Edit crontab
crontab -e

# Add backup schedule (daily at 2 AM)
0 2 * * * /var/www/student-risk-monitoring/backup_db.sh
```

### 4. Manual Backup

```bash
# Create manual backup
mysqldump -u deploy_user -p student_risk_monitoring > backup_$(date +%Y%m%d).sql

# Compress
gzip backup_$(date +%Y%m%d).sql
```

### 5. Restore Database

```bash
# Restore from backup
gunzip < backup_file.sql.gz | mysql -u deploy_user -p student_risk_monitoring
```

---

## Monitoring

### 1. Application Monitoring

#### System Monitoring with htop

```bash
# Install htop
sudo apt install -y htop

# Monitor system resources
htop
```

#### Application Logs

```bash
# View application logs
sudo tail -f /var/log/supervisor/student-risk-monitoring.log

# View Nginx logs
sudo tail -f /var/log/nginx/student-risk-monitoring.access.log
sudo tail -f /var/log/nginx/student-risk-monitoring.error.log

# View Gunicorn logs
sudo tail -f /var/log/gunicorn/access.log
sudo tail -f /var/log/gunicorn/error.log
```

### 2. Health Check Endpoint

The application includes a health check endpoint at `/health`:

```bash
# Test health check
curl http://localhost:5000/health

# Expected response: "healthy"
```

### 3. Monitoring Tools (Optional)

#### Install Prometheus & Grafana

```bash
# Install Prometheus
wget https://github.com/prometheus/prometheus/releases/download/v2.45.0/prometheus-2.45.0.linux-amd64.tar.gz
tar xvfz prometheus-*.tar.gz
cd prometheus-*

# Install Grafana
sudo apt install -y apt-transport-https
sudo wget -q -O /usr/share/keyrings/grafana.key https://apt.grafana.com/gpg.key
echo "deb [signed-by=/usr/share/keyrings/grafana.key] https://apt.grafana.com stable main" | sudo tee -a /etc/apt/sources.list.d/grafana.list
sudo apt update
sudo apt install -y grafana

# Start Grafana
sudo systemctl start grafana-server
sudo systemctl enable grafana-server
```

### 4. Alerting

#### Email Alerts for Critical Issues

```bash
# Install mailutils
sudo apt install -y mailutils

# Create alert script
nano /var/www/student-risk-monitoring/check_health.sh
```

```bash
#!/bin/bash
# check_health.sh

HEALTH_URL="http://localhost:5000/health"
ADMIN_EMAIL="admin@yourdomain.com"

# Check health
response=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL)

if [ $response != "200" ]; then
    echo "Application health check failed with status: $response" | mail -s "ALERT: Student Risk Monitoring Down" $ADMIN_EMAIL
fi
```

```bash
# Schedule health checks (every 5 minutes)
*/5 * * * * /var/www/student-risk-monitoring/check_health.sh
```

---

## Docker Deployment

### 1. Using Docker Compose

```bash
# Clone repository
git clone <repository-url>
cd student-risk-monitoring

# Configure environment
cp .env.example .env
nano .env

# Build and start containers
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### 2. Docker Compose Configuration

See [`docker-compose.yml`](docker-compose.yml) for the complete configuration.

### 3. Docker Commands

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f app

# Restart services
docker-compose restart

# Remove volumes (careful!)
docker-compose down -v
```

---

## Security Best Practices

### 1. Firewall Configuration

```bash
# Install UFW
sudo apt install -y ufw

# Configure firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable

# Check status
sudo ufw status
```

### 2. SSH Security

```bash
# Edit SSH configuration
sudo nano /etc/ssh/sshd_config

# Recommended changes:
# PermitRootLogin no
# PasswordAuthentication no
# Port 2222 (optional)

# Restart SSH
sudo systemctl restart sshd
```

### 3. Fail2Ban

```bash
# Install Fail2Ban
sudo apt install -y fail2ban

# Configure
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo nano /etc/fail2ban/jail.local

# Enable for SSH and Nginx
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 4. Regular Updates

```bash
# Create update script
nano /var/www/student-risk-monitoring/update_system.sh
```

```bash
#!/bin/bash
# update_system.sh

# Update system packages
sudo apt update && sudo apt upgrade -y

# Update application
cd /var/www/student-risk-monitoring
git pull origin main
source venv/bin/activate
pip install -r requirements.txt

# Restart application
sudo supervisorctl restart student-risk-monitoring

# Reload Nginx
sudo systemctl reload nginx
```

---

## Performance Optimization

### 1. Database Optimization

```sql
-- Optimize MySQL
SET GLOBAL innodb_buffer_pool_size = 1G;
SET GLOBAL query_cache_size = 64M;
SET GLOBAL max_connections = 200;
```

### 2. Nginx Optimization

```nginx
# Add to nginx.conf
worker_processes auto;
worker_connections 1024;

# Enable gzip
gzip on;
gzip_vary on;
gzip_proxied any;
gzip_comp_level 6;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
```

### 3. Application Optimization

```python
# In config.py
class ProductionConfig:
    SQLALCHEMY_POOL_SIZE = 10
    SQLALCHEMY_POOL_RECYCLE = 3600
    SQLALCHEMY_MAX_OVERFLOW = 20
```

### 4. Caching

```bash
# Install Redis (optional)
sudo apt install -y redis-server

# Configure Flask-Caching
pip install Flask-Caching
```

---

## Deployment Checklist

- [ ] Server provisioned and configured
- [ ] MySQL installed and configured
- [ ] Python environment set up
- [ ] Application deployed
- [ ] Environment variables configured
- [ ] Database initialized and seeded
- [ ] ML model trained
- [ ] Nginx configured
- [ ] Gunicorn configured
- [ ] Supervisor configured
- [ ] SSL certificate installed
- [ ] Firewall configured
- [ ] Automated backups scheduled
- [ ] Monitoring set up
- [ ] Health checks working
- [ ] Application accessible via domain
- [ ] All features tested in production

---

## Rollback Procedure

If deployment fails:

```bash
# Stop application
sudo supervisorctl stop student-risk-monitoring

# Restore database
gunzip < /var/backups/mysql/latest_backup.sql.gz | mysql -u deploy_user -p student_risk_monitoring

# Revert code
cd /var/www/student-risk-monitoring
git checkout previous_working_commit

# Restart application
sudo supervisorctl start student-risk-monitoring
```

---

## Support

For deployment issues:
- Check logs: `/var/log/supervisor/student-risk-monitoring.log`
- Review Nginx logs: `/var/log/nginx/student-risk-monitoring.error.log`
- Contact: [your.email@example.com]

---

**Last Updated**: 2024
**Version**: 1.0.0

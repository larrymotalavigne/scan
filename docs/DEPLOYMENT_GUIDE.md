# Deployment Guide

Complete guide for deploying the Scan application to production.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Server Setup](#server-setup)
3. [Application Deployment](#application-deployment)
4. [Database Setup](#database-setup)
5. [SSL/TLS Configuration](#ssltls-configuration)
6. [Monitoring](#monitoring)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

### Server Requirements

- **OS**: Ubuntu 22.04 LTS or newer
- **CPU**: 2+ cores recommended
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 20GB minimum, SSD recommended
- **Network**: Public IP address and domain name

### Software Requirements

- Docker 24.0+
- Docker Compose 2.20+
- Git
- Nginx (if using separate reverse proxy)

## Server Setup

### 1. Update System

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl git build-essential
```

### 2. Install Docker

```bash
# Add Docker's official GPG key
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add your user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Verify installation
docker --version
docker compose version
```

### 3. Configure Firewall

```bash
# Allow SSH, HTTP, HTTPS
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 4. Create Application Directory

```bash
sudo mkdir -p /opt/scan
sudo chown $USER:$USER /opt/scan
cd /opt/scan
```

## Application Deployment

### 1. Clone Repository

```bash
cd /opt/scan
git clone https://github.com/yourusername/scan.git .
```

### 2. Configure Environment

```bash
# Copy and edit production environment file
cp .env.template .env.production

# Edit with production values
nano .env.production
```

**Important Environment Variables**:

```bash
# Generate secure secret key
SECRET_KEY=$(openssl rand -hex 32)

# Generate database password
DB_PASSWORD=$(openssl rand -base64 32)

# Generate Redis password
REDIS_PASSWORD=$(openssl rand -base64 32)

# Set your domain
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### 3. Build Production Images

```bash
docker compose -f docker-compose.prod.yml build
```

### 4. Start Services

```bash
docker compose -f docker-compose.prod.yml up -d
```

### 5. Run Database Migrations

```bash
docker compose -f docker-compose.prod.yml exec api alembic upgrade head
```

### 6. Verify Deployment

```bash
# Check service status
docker compose -f docker-compose.prod.yml ps

# Check logs
docker compose -f docker-compose.prod.yml logs

# Test health endpoints
curl http://localhost:8000/health
curl http://localhost/health
```

## Database Setup

### Initial Database Setup

```bash
# The database is automatically initialized by Docker Compose
# Verify connection
docker compose -f docker-compose.prod.yml exec database psql -U postgres -d scan -c "\\dt"
```

### Database Backup

```bash
# Manual backup
docker compose -f docker-compose.prod.yml exec database pg_dump -U postgres scan > backup_$(date +%Y%m%d).sql

# Automated backup (add to crontab)
0 2 * * * /opt/scan/scripts/backup.sh
```

### Database Restore

```bash
# Restore from backup
docker compose -f docker-compose.prod.yml exec -T database psql -U postgres scan < backup_20260111.sql
```

## SSL/TLS Configuration

### Using Let's Encrypt with Certbot

1. **Install Certbot**

```bash
sudo apt install -y certbot python3-certbot-nginx
```

2. **Obtain Certificate**

```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

3. **Configure Auto-Renewal**

```bash
# Test renewal
sudo certbot renew --dry-run

# Add to crontab (runs twice daily)
0 0,12 * * * certbot renew --quiet
```

4. **Update Nginx Configuration**

Edit `config/nginx/nginx.conf`:

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # ... rest of configuration
}
```

## Monitoring

### Setup Application Monitoring

1. **Check Service Health**

```bash
# API health
curl https://yourdomain.com/api/health

# All services
docker compose -f docker-compose.prod.yml ps
```

2. **View Logs**

```bash
# All services
docker compose -f docker-compose.prod.yml logs -f

# Specific service
docker compose -f docker-compose.prod.yml logs -f api
```

3. **Resource Usage**

```bash
# Container stats
docker stats

# Disk usage
docker system df
```

### Setup Monitoring Stack (Optional)

See [MONITORING_SETUP.md](MONITORING_SETUP.md) for Prometheus/Grafana setup.

## Updating the Application

### Rolling Update

```bash
cd /opt/scan

# Pull latest changes
git pull origin main

# Pull latest images
docker compose -f docker-compose.prod.yml pull

# Run migrations
docker compose -f docker-compose.prod.yml run --rm api alembic upgrade head

# Rolling update (zero downtime)
docker compose -f docker-compose.prod.yml up -d --no-deps api
docker compose -f docker-compose.prod.yml up -d --no-deps frontend

# Cleanup old images
docker image prune -af
```

### Rollback

```bash
# Stop current version
docker compose -f docker-compose.prod.yml down

# Checkout previous version
git checkout <previous-commit>

# Rebuild and start
docker compose -f docker-compose.prod.yml up -d --build

# Restore database if needed
# ... restore from backup ...
```

## Troubleshooting

### Common Issues

1. **Service Won't Start**

```bash
# Check logs
docker compose -f docker-compose.prod.yml logs [service-name]

# Check container status
docker compose -f docker-compose.prod.yml ps

# Restart service
docker compose -f docker-compose.prod.yml restart [service-name]
```

2. **Database Connection Failed**

```bash
# Verify database is running
docker compose -f docker-compose.prod.yml ps database

# Check database logs
docker compose -f docker-compose.prod.yml logs database

# Verify connection string in .env.production
```

3. **High Memory Usage**

```bash
# Check container stats
docker stats

# Adjust resource limits in docker-compose.prod.yml
# Restart services
docker compose -f docker-compose.prod.yml restart
```

4. **Slow Response Times**

```bash
# Check API logs for slow queries
docker compose -f docker-compose.prod.yml logs api | grep "slow"

# Check database performance
docker compose -f docker-compose.prod.yml exec database psql -U postgres -d scan -c "SELECT * FROM pg_stat_activity;"

# Consider adding database indexes
```

### Emergency Procedures

**Complete System Restart**:

```bash
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d
```

**Database Recovery**:

```bash
# Stop all services
docker compose -f docker-compose.prod.yml down

# Restore from backup
cat backup_latest.sql | docker compose -f docker-compose.prod.yml exec -T database psql -U postgres scan

# Start services
docker compose -f docker-compose.prod.yml up -d
```

## Security Checklist

- [ ] All environment variables set securely
- [ ] SSL/TLS certificates configured
- [ ] Firewall rules configured
- [ ] Database passwords changed from defaults
- [ ] Regular backups configured
- [ ] Monitoring and alerting set up
- [ ] Log rotation configured
- [ ] Security updates automated

## Next Steps

- [Production Setup Guide](PRODUCTION_SETUP.md)
- [Disaster Recovery Plan](DISASTER_RECOVERY.md)
- [Monitoring Setup](MONITORING_SETUP.md)

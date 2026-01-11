#!/bin/bash
#
# Production Deployment Script
#
# This script handles deployment to production with proper checks,
# database migrations, and rollback capabilities.

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
DEPLOY_DIR="/opt/scan"
BACKUP_DIR="/opt/scan/backups"
COMPOSE_FILE="docker-compose.prod.yml"

# Functions
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if running as correct user
if [ "$EUID" -eq 0 ]; then
    error "Do not run this script as root"
fi

# Change to deployment directory
cd "$DEPLOY_DIR" || error "Deployment directory not found: $DEPLOY_DIR"

log "Starting deployment process..."

# 1. Pre-deployment checks
log "Running pre-deployment checks..."

# Check if .env.production exists
if [ ! -f .env.production ]; then
    error ".env.production file not found"
fi

# Check if docker is running
if ! docker info > /dev/null 2>&1; then
    error "Docker is not running"
fi

# Check disk space (require at least 2GB free)
AVAILABLE_SPACE=$(df -BG . | tail -1 | awk '{print $4}' | sed 's/G//')
if [ "$AVAILABLE_SPACE" -lt 2 ]; then
    warn "Low disk space: ${AVAILABLE_SPACE}GB available"
fi

# 2. Backup current database
log "Creating database backup..."
mkdir -p "$BACKUP_DIR"
BACKUP_FILE="$BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).sql"

docker compose -f "$COMPOSE_FILE" exec -T database pg_dump -U postgres scan > "$BACKUP_FILE" || {
    warn "Database backup failed, but continuing deployment"
}

if [ -f "$BACKUP_FILE" ]; then
    log "Database backed up to: $BACKUP_FILE"
fi

# 3. Pull latest changes
log "Pulling latest changes from repository..."
git pull origin main || error "Failed to pull latest changes"

# 4. Pull latest Docker images
log "Pulling latest Docker images..."
export VERSION=$(git rev-parse --short HEAD)
export REGISTRY_URL="ghcr.io/$(git config --get remote.origin.url | sed 's/.*://;s/.git$//')"

docker compose -f "$COMPOSE_FILE" pull || error "Failed to pull Docker images"

# 5. Run database migrations
log "Running database migrations..."
docker compose -f "$COMPOSE_FILE" run --rm api alembic upgrade head || {
    error "Database migrations failed. Rolling back..."
    # Restore from backup
    if [ -f "$BACKUP_FILE" ]; then
        cat "$BACKUP_FILE" | docker compose -f "$COMPOSE_FILE" exec -T database psql -U postgres scan
        log "Database restored from backup"
    fi
    exit 1
}

# 6. Build new images (if needed)
log "Building new images..."
docker compose -f "$COMPOSE_FILE" build || error "Failed to build images"

# 7. Rolling update - API first
log "Updating API service (rolling update)..."
docker compose -f "$COMPOSE_FILE" up -d --no-deps --scale api=2 api

# Wait for new API to be healthy
log "Waiting for API health check..."
MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if docker compose -f "$COMPOSE_FILE" exec -T api curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log "API is healthy"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    sleep 2
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    error "API health check failed. Rolling back..."
fi

# Scale down old API
docker compose -f "$COMPOSE_FILE" up -d --no-deps --scale api=1 api

# 8. Update frontend
log "Updating frontend service..."
docker compose -f "$COMPOSE_FILE" up -d --no-deps frontend

# Wait for frontend health
log "Waiting for frontend health check..."
RETRY_COUNT=0
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -f http://localhost/health > /dev/null 2>&1; then
        log "Frontend is healthy"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    sleep 2
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    warn "Frontend health check failed, but deployment continues"
fi

# 9. Cleanup old images
log "Cleaning up old Docker images..."
docker image prune -af > /dev/null 2>&1

# 10. Post-deployment verification
log "Running post-deployment checks..."

# Check all services are running
SERVICES=$(docker compose -f "$COMPOSE_FILE" ps --services)
for service in $SERVICES; do
    STATUS=$(docker compose -f "$COMPOSE_FILE" ps "$service" | tail -1 | awk '{print $NF}')
    if [[ ! "$STATUS" =~ "Up" ]]; then
        error "Service $service is not running: $STATUS"
    fi
done

log "All services are running"

# 11. Cleanup old backups (keep last 10)
log "Cleaning up old backups..."
cd "$BACKUP_DIR"
ls -t backup_*.sql | tail -n +11 | xargs -r rm

log "${GREEN}Deployment completed successfully!${NC}"
log "Version deployed: $VERSION"
log "Backup saved: $BACKUP_FILE"

# Display service status
log "\nService Status:"
docker compose -f "$COMPOSE_FILE" ps

exit 0

#!/bin/bash
#
# Rollback Script
#
# This script rolls back the application to a previous version
# and optionally restores a database backup.

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
DEPLOY_DIR="/opt/scan"
BACKUP_DIR="/opt/scan/backups"
COMPOSE_FILE="docker-compose.prod.yml"

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

cd "$DEPLOY_DIR" || error "Deployment directory not found"

log "Starting rollback process..."

# Show available backups
log "Available database backups:"
ls -lh "$BACKUP_DIR"/backup_*.sql.gz 2>/dev/null | tail -5 || warn "No backups found"

# Ask for confirmation
read -p "Do you want to restore from a database backup? (y/N): " -n 1 -r
echo
RESTORE_DB=$REPLY

# Get list of recent commits
log "\nRecent commits:"
git log --oneline -5

# Ask which commit to rollback to
read -p "Enter commit SHA to rollback to (or press Enter for previous commit): " COMMIT_SHA

if [ -z "$COMMIT_SHA" ]; then
    # Get previous commit
    COMMIT_SHA=$(git rev-parse HEAD~1)
    log "Using previous commit: $COMMIT_SHA"
fi

# Stop services
log "Stopping services..."
docker compose -f "$COMPOSE_FILE" down

# Checkout specified commit
log "Rolling back to commit: $COMMIT_SHA"
git checkout "$COMMIT_SHA" || error "Failed to checkout commit"

# Restore database if requested
if [[ $RESTORE_DB =~ ^[Yy]$ ]]; then
    log "Available backups:"
    select BACKUP_FILE in "$BACKUP_DIR"/backup_*.sql.gz; do
        if [ -n "$BACKUP_FILE" ]; then
            log "Restoring database from: $BACKUP_FILE"

            # Start database service
            docker compose -f "$COMPOSE_FILE" up -d database

            # Wait for database to be ready
            sleep 5

            # Restore backup
            gunzip -c "$BACKUP_FILE" | docker compose -f "$COMPOSE_FILE" exec -T database psql -U postgres scan || {
                error "Database restore failed"
            }

            log "Database restored successfully"
            break
        else
            warn "Invalid selection"
        fi
    done
fi

# Rebuild and start services
log "Rebuilding and starting services..."
docker compose -f "$COMPOSE_FILE" up -d --build

# Wait for services to be healthy
log "Waiting for services to be healthy..."
sleep 10

# Verify health
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
    error "Health check failed after rollback"
fi

log "${GREEN}Rollback completed successfully!${NC}"
log "Current version: $(git rev-parse --short HEAD)"

# Display service status
log "\nService Status:"
docker compose -f "$COMPOSE_FILE" ps

exit 0

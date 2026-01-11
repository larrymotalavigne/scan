#!/bin/bash
#
# Database Backup Script
#
# This script creates backups of the PostgreSQL database
# and manages backup retention.

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
BACKUP_DIR="/opt/scan/backups"
COMPOSE_FILE="/opt/scan/docker-compose.prod.yml"
RETENTION_DAYS=30
RETENTION_COUNT=10

# Create backup directory
mkdir -p "$BACKUP_DIR"

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# Backup filename with timestamp
BACKUP_FILE="$BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).sql"
BACKUP_FILE_COMPRESSED="$BACKUP_FILE.gz"

log "Starting database backup..."

# Create backup
cd /opt/scan
docker compose -f "$COMPOSE_FILE" exec -T database pg_dump -U postgres scan > "$BACKUP_FILE" || error "Backup failed"

# Compress backup
gzip "$BACKUP_FILE"

log "Backup created: $BACKUP_FILE_COMPRESSED"

# Get backup size
BACKUP_SIZE=$(du -h "$BACKUP_FILE_COMPRESSED" | cut -f1)
log "Backup size: $BACKUP_SIZE"

# Cleanup old backups by count (keep last N)
log "Cleaning up old backups (keeping last $RETENTION_COUNT)..."
cd "$BACKUP_DIR"
ls -t backup_*.sql.gz | tail -n +$((RETENTION_COUNT + 1)) | xargs -r rm
log "Removed old backups (kept last $RETENTION_COUNT)"

# Cleanup old backups by age (older than N days)
find "$BACKUP_DIR" -name "backup_*.sql.gz" -type f -mtime +$RETENTION_DAYS -delete
log "Removed backups older than $RETENTION_DAYS days"

# List remaining backups
BACKUP_COUNT=$(ls -1 "$BACKUP_DIR"/backup_*.sql.gz 2>/dev/null | wc -l)
log "Total backups: $BACKUP_COUNT"

log "Backup completed successfully!"

exit 0

#!/bin/bash
set -e
mkdir -p backups
timestamp=$(date "+%Y%m%d-%H%M%S")
tar czf backups/state_backup_$timestamp.tar.gz state/
echo "✅ Backup saved: backups/state_backup_$timestamp.tar.gz"

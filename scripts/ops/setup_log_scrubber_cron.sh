#!/bin/bash
# 🕐 [CRON SETUP] - Configuration automatique du log scrubber
# Roadmap S1-P1 - Automatisation nettoyage logs

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
PYTHON_PATH="${PROJECT_ROOT}/arkalia-luna-venv/bin/python"
SCRUBBER_SCRIPT="${PROJECT_ROOT}/scripts/ops/log_scrubber.py"

echo "🕐 [CRON SETUP] Configuration automatique du log scrubber"
echo "📂 Projet: $PROJECT_ROOT"
echo "🐍 Python: $PYTHON_PATH"
echo "🧹 Script: $SCRUBBER_SCRIPT"

# Vérification des prérequis
if [ ! -f "$PYTHON_PATH" ]; then
    echo "❌ Python venv non trouvé: $PYTHON_PATH"
    echo "ℹ️ Utilisation du python système"
    PYTHON_PATH="/usr/bin/python3"
fi

if [ ! -f "$SCRUBBER_SCRIPT" ]; then
    echo "❌ Script log_scrubber.py non trouvé: $SCRUBBER_SCRIPT"
    exit 1
fi

# Configuration cron jobs
CRON_CONFIG="# 🧹 Arkalia-LUNA Log Scrubber - Roadmap S1-P1
# Nettoyage quotidien à 02:00 (mode production)
0 2 * * * cd $PROJECT_ROOT && $PYTHON_PATH $SCRUBBER_SCRIPT >> logs/cron_scrubber.log 2>&1

# Nettoyage hebdomadaire complet à 03:00 le dimanche
0 3 * * 0 cd $PROJECT_ROOT && $PYTHON_PATH $SCRUBBER_SCRIPT --verbose >> logs/cron_scrubber.log 2>&1

# Vérification mensuelle archives (1er du mois à 04:00)
0 4 1 * * cd $PROJECT_ROOT && find logs/archives/ -name '*.gz' -mtime +90 -delete >> logs/cron_scrubber.log 2>&1
"

echo "🕐 Configuration cron jobs..."

# Backup crontab existante
echo "📦 Sauvegarde crontab existante..."
if crontab -l > /dev/null 2>&1; then
    crontab -l > "${PROJECT_ROOT}/logs/crontab_backup_$(date +%Y%m%d_%H%M%S).txt"
    echo "✅ Crontab sauvegardée"
else
    echo "ℹ️ Aucune crontab existante"
fi

# Installation nouvelle crontab
echo "📝 Installation des tâches cron..."
{
    # Préserver crontab existante (sauf anciennes tâches Arkalia)
    if crontab -l 2>/dev/null | grep -v "Arkalia-LUNA Log Scrubber"; then
        crontab -l 2>/dev/null | grep -v "Arkalia-LUNA Log Scrubber" || true
    fi
    # Ajouter nouvelle configuration
    echo "$CRON_CONFIG"
} | crontab -

echo "✅ Cron jobs configurés avec succès !"

# Affichage de la configuration finale
echo ""
echo "📋 Configuration cron actuelle :"
crontab -l | grep -A 10 -B 2 "Arkalia-LUNA" || echo "❌ Erreur affichage crontab"

# Test manuel du scrubber
echo ""
echo "🧪 Test rapide du scrubber..."
cd "$PROJECT_ROOT"
$PYTHON_PATH "$SCRUBBER_SCRIPT" --dry-run | head -10

echo ""
echo "🎉 Log scrubber automatique configuré !"
echo "📋 Planification:"
echo "   • 02:00 quotidien : Nettoyage automatique"
echo "   • 03:00 dimanche : Nettoyage complet"
echo "   • 04:00 1er mois : Purge archives anciennes"
echo "📄 Logs: logs/cron_scrubber.log"
echo ""
echo "🔧 Commandes utiles:"
echo "   crontab -l                    # Voir les tâches"
echo "   crontab -e                    # Éditer les tâches"
echo "   tail -f logs/cron_scrubber.log # Suivre les logs"

#!/bin/bash
# 🧹 Nettoyage des fichiers d'état volatils et snapshots temporaires Arkalia-LUNA

echo "🧹 Nettoyage des fichiers d'état volatils et snapshots temporaires…"

# Snapshots Sandozia
echo "- Suppression des intelligence_snapshot_*.json"
find state/sandozia/ -name "intelligence_snapshot_*.json" -delete
echo "- Suppression des heatmap_data_*.json"
find state/sandozia/ -name "heatmap_data_*.json" -delete
echo "- Suppression des detected_patterns.jsonl"
find state/sandozia/ -name "detected_patterns.jsonl" -delete

echo "- Suppression du cache metrics (latest_metrics.json)"
rm -f state/sandozia/latest_metrics.json

echo "✅ Nettoyage terminé. Seuls les états critiques sont conservés."

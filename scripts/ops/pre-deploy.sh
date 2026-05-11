#!/bin/bash

echo "🔧 Préparation de la génération du statut ZeroIA..."

# Active le venv si disponible
if [ -f "./arkalia-luna-venv/bin/activate" ]; then
  source ./arkalia-luna-venv/bin/activate
fi

# Vérifie si Docker est dispo
if ! command -v docker &> /dev/null; then
  echo "⚠️ Docker non disponible — suppression du statut existant si présent."
  rm -f docs/logs/zeroia_status.md
  exit 0
fi

# Vérifie si le container existe
if ! docker ps -a --format '{{.Names}}' | grep -q '^zeroia$'; then
  echo "⚠️ Container 'zeroia' introuvable — suppression du statut."
  rm -f docs/logs/zeroia_status.md
  exit 0
fi

# Vérifie si le container est en état sain
STATUS=$(docker inspect --format='{{.State.Status}}' zeroia)
if [ "$STATUS" != "running" ]; then
  echo "⚠️ ZeroIA n'est pas actif (status=$STATUS) — suppression du statut."
  rm -f docs/logs/zeroia_status.md
  exit 0
fi

# Exécution du script de génération
echo "🧠 ZeroIA actif, génération du fichier de statut..."
python scripts/_generate_zeroia_status.py

# Vérifie l'exécution
if [ $? -ne 0 ]; then
  echo "❌ Erreur lors de la génération du statut ZeroIA — suppression de sécurité."
  rm -f docs/logs/zeroia_status.md
  exit 1
fi

echo "✅ Fichier zeroia_status.md généré avec succès."
exit 0

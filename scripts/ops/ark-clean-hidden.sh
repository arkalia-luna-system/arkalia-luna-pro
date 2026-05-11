#!/bin/bash
# 🧹 Script de nettoyage des fichiers macOS cachés et autres fichiers temporaires
# Supprime tous les fichiers et dossiers ._* qui causent des problèmes avec Docker

set -e

echo "🧹 Nettoyage des fichiers invisibles macOS..."

# Supprimer tous les fichiers ._* (pas seulement dans docs)
find . -name "._*" -type f -delete 2>/dev/null || true

# Supprimer tous les dossiers ._*
find . -name "._*" -type d -delete 2>/dev/null || true

# Supprimer les fichiers .DS_Store
find . -name ".DS_Store" -delete 2>/dev/null || true

# Supprimer les dossiers __pycache__
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Supprimer les fichiers .pyc
find . -name "*.pyc" -delete 2>/dev/null || true

# Supprimer les fichiers .coverage temporaires
find . -name "._.coverage*" -delete 2>/dev/null || true

echo "✅ Nettoyage terminé !"
echo "📊 Fichiers supprimés :"
echo "   - Fichiers ._* (macOS cachés)"
echo "   - Dossiers ._* (macOS cachés)"
echo "   - Fichiers .DS_Store"
echo "   - Dossiers __pycache__"
echo "   - Fichiers .pyc"
echo "   - Fichiers ._.coverage*"

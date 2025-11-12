#!/bin/bash
# 🧹 Script de correction automatique des erreurs de linting
# Arkalia-LUNA Pro - v2.8.0

set -e

echo "🧹 === CORRECTION AUTOMATIQUE LINTING ==="
echo "   Arkalia-LUNA Pro - Nettoyage intelligent"
echo ""

# Vérifier que nous sommes dans le bon répertoire
if [[ ! -f "version.toml" ]]; then
    echo "❌ Erreur: Ce script doit être exécuté depuis la racine du projet"
    exit 1
fi

echo "🔍 Vérification de l'environnement..."

# Vérifier les outils
if ! command -v black &> /dev/null; then
    echo "❌ Black non trouvé. Installation..."
    pip install black
fi

if ! command -v ruff &> /dev/null; then
    echo "❌ Ruff non trouvé. Installation..."
    pip install ruff
fi

# if ! command -v isort &> /dev/null; then
#     echo "❌ isort non trouvé. Installation..."
#     pip install isort
# fi
# DÉSACTIVÉ - isort cause des problèmes

echo "✅ Outils de linting disponibles"

# 1. Nettoyage des fichiers cachés macOS
echo ""
echo "🧹 Nettoyage fichiers cachés macOS..."
find . -name "._*" -delete 2>/dev/null || true
find . -name ".DS_Store" -delete 2>/dev/null || true
echo "✅ Fichiers cachés supprimés"

# 2. Nettoyage des caches Python
echo ""
echo "🧹 Nettoyage caches Python..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true
echo "✅ Caches Python supprimés"

# 3. Formatage avec isort - DÉSACTIVÉ
# echo ""
# echo "📝 Tri des imports avec isort..."
# isort . --profile black --skip-glob "*/generated/*" --skip-glob "*/venv/*" || {
#     echo "⚠️ Erreur isort, continuation..."
# }
# DÉSACTIVÉ - isort cause des problèmes de performance

# 4. Formatage avec black
echo ""
echo "🎨 Formatage avec black..."
black . --exclude archive/ --exclude "._*" --exclude "/(generated|venv|\.venv|__pycache__)/" || {
    echo "⚠️ Erreur black, continuation..."
}

# 5. Correction automatique avec ruff
echo ""
echo "🔧 Correction automatique avec ruff..."
ruff check . --fix --exclude archive/ --exclude "._*" || {
    echo "⚠️ Erreur ruff, continuation..."
}

# 6. Vérification des fichiers de configuration
echo ""
echo "⚙️ Vérification des fichiers de configuration..."

# Vérifier .pre-commit-config.yaml
if command -v pre-commit &> /dev/null; then
    echo "🔍 Validation pre-commit config..."
    pre-commit validate-config || {
        echo "⚠️ Erreur dans pre-commit config"
    }
fi

# 7. Nettoyage des logs temporaires
echo ""
echo "🧹 Nettoyage logs temporaires..."
find logs/ -name "*.tmp" -delete 2>/dev/null || true
find logs/ -name "*.log" -size -1c -delete 2>/dev/null || true
echo "✅ Logs temporaires nettoyés"

# 8. Vérification finale
echo ""
echo "🔍 Vérification finale..."

# Vérifier s'il reste des erreurs critiques
echo "📊 Rapport d'erreurs restantes:"
ruff check . --output-format=concise --exclude archive/ --exclude "._*" || {
    echo "⚠️ Il reste des erreurs de linting"
}

echo ""
echo "✅ === NETTOYAGE TERMINÉ ==="
echo "💡 Si des erreurs persistent, elles nécessitent une correction manuelle"
echo "🚀 Tu peux maintenant relancer tes tests !"

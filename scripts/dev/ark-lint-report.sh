#!/bin/bash
# 📊 Script de rapport d'erreurs de linting
# Arkalia-LUNA Pro - v2.8.0

echo "📊 === RAPPORT ERREURS LINTING ARKALIA-LUNA ==="
echo "   Version: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# Vérifier que nous sommes dans le bon répertoire
if [[ ! -f "version.toml" ]]; then
    echo "❌ Erreur: Ce script doit être exécuté depuis la racine du projet"
    exit 1
fi

echo "🔍 === ANALYSE RUFF ==="
ruff_count=$(ruff check . --output-format=concise --exclude="generated,venv,.venv,__pycache__" 2>/dev/null | wc -l || echo "0")
echo "📈 Erreurs Ruff: $ruff_count"

echo ""
echo "🔍 === ANALYSE FLAKE8 ==="
flake8_count=$(flake8 . --exclude=generated,venv,.venv,__pycache__ --count 2>/dev/null || echo "0")
echo "📈 Erreurs Flake8: $flake8_count"

echo ""
echo "🔍 === ANALYSE BLACK ==="
black_check=$(black . --check --exclude "/(generated|venv|\.venv|__pycache__)/" 2>&1 | grep -c "would reformat" || echo "0")
echo "📈 Fichiers à reformater: $black_check"

echo ""
echo "🔍 === ANALYSE ISORT ==="
isort_check=$(isort . --check-only --profile black --skip-glob "*/generated/*" --skip-glob "*/venv/*" 2>&1 | grep -c "ERROR" || echo "0")
echo "📈 Erreurs isort: $isort_check"

echo ""
echo "📊 === RÉSUMÉ ==="
total_errors=$((ruff_count + flake8_count + black_check + isort_check))
echo "🎯 Total erreurs: $total_errors"

echo ""
echo "🔍 === DÉTAIL DES ERREURS ==="
echo ""

echo "🐍 RUFF:"
ruff check . --output-format=concise --exclude="generated,venv,.venv,__pycache__" 2>/dev/null || echo "Aucune erreur Ruff"

echo ""
echo "🐍 FLAKE8:"
flake8 . --exclude=generated,venv,.venv,__pycache__ 2>/dev/null || echo "Aucune erreur Flake8"

echo ""
echo "🎨 BLACK:"
black . --check --exclude "/(generated|venv|\.venv|__pycache__)/" 2>/dev/null || echo "Aucune erreur Black"

echo ""
echo "📝 ISORT:"
isort . --check-only --profile black --skip-glob "*/generated/*" --skip-glob "*/venv/*" 2>/dev/null || echo "Aucune erreur isort"

echo ""
echo "✅ === RAPPORT TERMINÉ ==="
echo "💡 Utilise './scripts/dev/ark-fix-linting.sh' pour corriger automatiquement"
echo "💡 Utilise './scripts/dev/ark-fix-style.sh' pour corriger le style"

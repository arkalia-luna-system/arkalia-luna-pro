#!/bin/bash
# Script pour exécuter les tests de manière optimisée (faible consommation mémoire)

set -e

echo "🧪 Exécution tests optimisée (mode léger)"
echo ""

# Option 1: Tests unitaires uniquement (le plus léger)
if [ "$1" = "unit" ]; then
    echo "📦 Mode: Tests unitaires uniquement"
    python -m pytest tests/unit/ \
        -q \
        --cov=modules \
        --cov=scripts \
        --cov=core \
        --cov=app \
        --cov=helloria \
        --cov=arkalia \
        --cov-report=term \
        --cov-report=html:htmlcov \
        --cov-fail-under=15 \
        -x \
        --maxfail=5

# Option 2: Exclure tests lents
elif [ "$1" = "fast" ]; then
    echo "⚡ Mode: Tests rapides (exclut slow et benchmark)"
    python -m pytest \
        -q \
        -m "not slow and not benchmark" \
        --cov=modules \
        --cov=scripts \
        --cov=core \
        --cov=app \
        --cov=helloria \
        --cov=arkalia \
        --cov-report=term \
        --cov-report=html:htmlcov \
        --cov-fail-under=15 \
        -x \
        --maxfail=5

# Option 3: Un seul fichier de test
elif [ -n "$1" ]; then
    echo "🎯 Mode: Fichier spécifique: $1"
    python -m pytest "$1" \
        -q \
        --cov=modules \
        --cov=scripts \
        --cov=core \
        --cov=app \
        --cov=helloria \
        --cov=arkalia \
        --cov-report=term \
        -x

# Option par défaut: Tests unitaires
else
    echo "📦 Mode: Tests unitaires (par défaut)"
    python -m pytest tests/unit/ \
        -q \
        --cov=modules \
        --cov=scripts \
        --cov=core \
        --cov=app \
        --cov=helloria \
        --cov=arkalia \
        --cov-report=term \
        --cov-report=html:htmlcov \
        --cov-fail-under=15 \
        -x \
        --maxfail=5
fi

echo ""
echo "✅ Tests terminés !"


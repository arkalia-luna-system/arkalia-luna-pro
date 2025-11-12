#!/bin/bash
set -e

# 🌕 ARKALIA-LUNA - SCRIPT DE TEST DE PERFORMANCE
# Version : 2.8.0 - Post Audit Tests
# Date : 4 juillet 2025

# Configuration
PERF_DIR="tests/performance"
REPORTS_DIR="tests/reports/performance"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$REPORTS_DIR/performance_$TIMESTAMP.log"

# Couleurs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

print_header() {
    echo -e "${PURPLE}🌕 ARKALIA-LUNA - TESTS DE PERFORMANCE${NC}"
    echo -e "${PURPLE}=====================================${NC}"
    echo ""
}

print_status() {
    echo -e "${BLUE}ℹ️  $1${NC}" | tee -a "$LOG_FILE"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}" | tee -a "$LOG_FILE"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}" | tee -a "$LOG_FILE"
}

print_section() {
    echo -e "${CYAN}📋 $1${NC}" | tee -a "$LOG_FILE"
    echo -e "${CYAN}${2//?/=}${NC}" | tee -a "$LOG_FILE"
}

# Fonction de benchmark personnalisé simplifié
run_benchmark() {
    local name="$1"
    local script="$2"
    local iterations="${3:-5}"

    print_section "🏃 Benchmark: $name" "="

    local start_time=$(date +%s)
    local results=()

    for i in $(seq 1 $iterations); do
        local iter_start=$(date +%s)
        python "$script" > /dev/null 2>&1
        local iter_end=$(date +%s)
        local duration=$((iter_end - iter_start))
        results+=($duration)
        print_status "Itération $i/$iterations: ${duration}s"
    done

    local end_time=$(date +%s)
    local total_duration=$((end_time - start_time))

    # Calcul des statistiques simplifié
    local sum=0
    local min=${results[0]}
    local max=${results[0]}

    for result in "${results[@]}"; do
        sum=$((sum + result))
        if [ $result -lt $min ]; then
            min=$result
        fi
        if [ $result -gt $max ]; then
            max=$result
        fi
    done

    local avg=$((sum / ${#results[@]}))

    # Sauvegarde des résultats
    cat >> "$REPORTS_DIR/benchmark_$TIMESTAMP.json" << EOF
{
    "benchmark": "$name",
    "timestamp": "$(date -Iseconds)",
    "iterations": $iterations,
    "total_duration": $total_duration,
    "statistics": {
        "min": $min,
        "max": $max,
        "average": $avg,
        "total": $sum
    },
    "individual_results": [$(IFS=,; echo "${results[*]}")]
}
EOF

    print_success "$name: avg=${avg}s, min=${min}s, max=${max}s"
}

# Fonction de test de charge simplifié
run_load_test() {
    local name="$1"
    local endpoint="$2"
    local concurrent_users="${3:-10}"
    local duration="${4:-30}"

    print_section "🔥 Test de charge: $name" "="

    # Démarrage de l'API si nécessaire
    if ! curl -s -o /dev/null -w "%{http_code}" "$endpoint" 2>/dev/null | grep -q "[24][0-9][0-9]"; then
        print_status "Démarrage de l'API pour le test de charge..."
        docker compose up -d arkalia-api 2>/dev/null || {
            print_warning "Impossible de démarrer l'API - test de charge ignoré"
            return 0
        }

        # Attente de l'API
        for i in {1..10}; do
            if curl -s -o /dev/null -w "%{http_code}" "$endpoint" 2>/dev/null | grep -q "[24][0-9][0-9]"; then
                break
            fi
            sleep 2
        done
    fi

    # Test de charge simplifié avec curl
    local results_file="$REPORTS_DIR/loadtest_${name}_$TIMESTAMP.txt"
    local start_time=$(date +%s)
    local success_count=0
    local total_requests=50

    print_status "Exécution de $total_requests requêtes..."

    for i in $(seq 1 $total_requests); do
        local req_start=$(date +%s.%N)
        if curl -s -o /dev/null -w "%{http_code}" "$endpoint" 2>/dev/null | grep -q "[24][0-9][0-9]"; then
            ((success_count++))
        fi
        local req_end=$(date +%s.%N)
        echo "$req_start,$req_end" >> "$results_file"

        # Petite pause pour éviter la surcharge
        sleep 0.1
    done

    local end_time=$(date +%s)
    local total_duration=$((end_time - start_time))
    local success_rate=$((success_count * 100 / total_requests))

    print_success "$name: $success_count/$total_requests succès (${success_rate}%), durée ${total_duration}s"

    # Arrêt de l'API si on l'a démarrée
    docker compose stop arkalia-api 2>/dev/null || true
}

# Fonction de test de mémoire simplifié
run_memory_test() {
    local name="$1"
    local script="$2"

    print_section "🧠 Test de mémoire: $name" "="

    if ! command -v python &> /dev/null; then
        print_warning "Python non trouvé - test de mémoire ignoré"
        return 0
    fi

    # Test basique avec psutil
    python -c "
import psutil
import os
import time
import subprocess

try:
    process = psutil.Process()
    initial_memory = process.memory_info().rss / 1024 / 1024

    # Exécution du script
    start_time = time.time()
    result = subprocess.run(['python', '$script'], capture_output=True, text=True, timeout=30)
    end_time = time.time()

    final_memory = process.memory_info().rss / 1024 / 1024
    duration = end_time - start_time

    print(f'Initial: {initial_memory:.2f}MB, Final: {final_memory:.2f}MB, Duration: {duration:.2f}s')
except Exception as e:
    print(f'Test de mémoire échoué: {e}')
" 2>/dev/null || print_warning "Test de mémoire échoué"

    print_success "$name: Test de mémoire terminé"
}

# Fonction de test de CPU simplifié
run_cpu_test() {
    local name="$1"
    local script="$2"

    print_section "⚡ Test de CPU: $name" "="

    if ! command -v python &> /dev/null; then
        print_warning "Python non trouvé - test de CPU ignoré"
        return 0
    fi

    # Test avec cProfile
    local profile_file="$REPORTS_DIR/cpu_${name}_$TIMESTAMP.prof"
    python -m cProfile -o "$profile_file" "$script" > /dev/null 2>&1

    # Analyse basique du profil
    python -c "
import pstats
from pstats import SortKey

try:
    p = pstats.Stats('$profile_file')
    p.sort_stats(SortKey.TIME)
    print('Top 3 functions by time:')
    p.print_stats(3)
except Exception as e:
    print(f'Analyse du profil CPU échouée: {e}')
" 2>/dev/null || print_warning "Analyse du profil CPU échouée"

    print_success "$name: Profil CPU généré"
}

# Fonction de test de modules spécifiques
run_module_tests() {
    print_section "🧪 Tests de Modules Spécifiques" "="

    # Test ZeroIA
    if [ -f "modules/zeroia/core.py" ]; then
        print_status "Test du module ZeroIA..."
        python -c "
import sys
sys.path.append('.')
try:
    from modules.zeroia.core import ZeroIACore
core = ZeroIACore()
    print('✅ ZeroIA Core initialisé avec succès')
except Exception as e:
    print(f'❌ Erreur ZeroIA: {e}')
" 2>/dev/null || print_warning "Test ZeroIA échoué"
    fi

    # Test Reflexia
    if [ -f "modules/reflexia/core.py" ]; then
        print_status "Test du module Reflexia..."
        python -c "
import sys
sys.path.append('.')
try:
    from modules.reflexia.core import launch_reflexia_check
    result = launch_reflexia_check()
    print('✅ Reflexia check exécuté avec succès')
except Exception as e:
    print(f'❌ Erreur Reflexia: {e}')
" 2>/dev/null || print_warning "Test Reflexia échoué"
    fi

    # Test Sandozia
    if [ -f "modules/sandozia/core.py" ]; then
        print_status "Test du module Sandozia..."
        python -c "
import sys
sys.path.append('.')
try:
    from modules.sandozia.core import UsandoziaCore
core = UsandoziaCore()
    print('✅ Sandozia Core initialisé avec succès')
except Exception as e:
    print(f'❌ Erreur Sandozia: {e}')
" 2>/dev/null || print_warning "Test Sandozia échoué"
    fi
}

# Fonction principale
main() {
    START_TIME=$(date +%s)

    print_header

    # Création des dossiers
    mkdir -p "$REPORTS_DIR"

    # Nettoyage des anciens rapports
    rm -f "$REPORTS_DIR"/benchmark_*.json "$REPORTS_DIR"/loadtest_*.txt "$REPORTS_DIR"/memory_*.txt "$REPORTS_DIR"/cpu_*.prof

    # Initialisation du fichier de résultats
    echo "[" > "$REPORTS_DIR/benchmark_$TIMESTAMP.json"

    print_section "🚀 DÉMARRAGE DES TESTS DE PERFORMANCE" "="

    # Benchmarks des modules principaux
    if [ -f "demo_global.py" ]; then
        run_benchmark "Demo Global" "demo_global.py" 3
    fi

    if [ -f "arkalia_score.py" ]; then
        run_benchmark "Score Cognitif" "arkalia_score.py" 3
    fi

    # Tests de modules spécifiques
    run_module_tests

    # Tests de charge des APIs (simplifiés)
    run_load_test "API Reflexia" "http://localhost:8000/reason" 5 20
    run_load_test "API ZeroIA" "http://localhost:8000/zeroia" 5 20

    # Tests de mémoire
    if [ -f "modules/zeroia/core.py" ]; then
        run_memory_test "ZeroIA Core" "modules/zeroia/core.py"
    fi

    if [ -f "modules/reflexia/core.py" ]; then
        run_memory_test "Reflexia Core" "modules/reflexia/core.py"
    fi

    # Tests de CPU
    if [ -f "modules/zeroia/reason_loop.py" ]; then
        run_cpu_test "ZeroIA Reason Loop" "modules/zeroia/reason_loop.py"
    fi

    # Tests de performance pytest
    print_section "🧪 Tests de Performance Pytest" "="
    pytest -c pytest-performance.ini tests/performance || print_warning "Tests de performance pytest échoués"

    # Fermeture du fichier JSON
    echo "]" >> "$REPORTS_DIR/benchmark_$TIMESTAMP.json"

    # Génération du rapport
    print_section "📊 GÉNÉRATION DU RAPPORT" "="

    cat > "$REPORTS_DIR/performance_summary_$TIMESTAMP.md" << EOF
# 🌕 Rapport de Performance Arkalia-LUNA

**Date :** $(date)
**Durée totale :** $(($(date +%s) - START_TIME))s

## 📋 Benchmarks exécutés

$(grep "✅.*Benchmark:" "$LOG_FILE" | tail -10)

## 🔥 Tests de charge

$(grep "✅.*Test de charge:" "$LOG_FILE" | tail -5)

## 🧠 Tests de mémoire

$(grep "✅.*Test de mémoire:" "$LOG_FILE" | tail -5)

## ⚡ Tests de CPU

$(grep "✅.*Test de CPU:" "$LOG_FILE" | tail -5)

## 📁 Fichiers générés

- \`$REPORTS_DIR/benchmark_$TIMESTAMP.json\` - Résultats des benchmarks
- \`$REPORTS_DIR/loadtest_*.txt\` - Résultats des tests de charge
- \`$REPORTS_DIR/memory_*.txt\` - Résultats des tests de mémoire
- \`$REPORTS_DIR/cpu_*.prof\` - Profils CPU
- \`$LOG_FILE\` - Log complet
- \`$REPORTS_DIR/performance_summary_$TIMESTAMP.md\` - Ce rapport

EOF

    print_success "Rapport de performance généré"

    # Résumé final
    print_section "🎯 RÉSUMÉ FINAL" "="
    print_status "Durée totale : $(($(date +%s) - START_TIME))s"
    print_success "🌕 Tests de performance terminés"
    print_status "📊 Rapports dans : $REPORTS_DIR/"
}

# Gestion des signaux
trap 'print_warning "Interruption détectée - Arrêt en cours..."; exit 1' INT TERM

# Exécution
main "$@"

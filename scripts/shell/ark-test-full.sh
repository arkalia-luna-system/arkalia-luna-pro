#!/bin/bash
set -e

# =============================================================================
# ARKALIA-LUNA PRO - TEST SUITE (SIMPLIFIED)
# Version: 2.8.1 | Date: $(date +%Y-%m-%d)
# =============================================================================

# Configuration
REPORTS_DIR="tests/reports"
HTMLCOV_DIR="htmlcov"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$REPORTS_DIR/test_run_$TIMESTAMP.log"
SUMMARY_FILE="$REPORTS_DIR/summary_$TIMESTAMP.md"
DEBUG=0
FAST=0

# Couleurs simples
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
GRAY='\033[0;37m'
BOLD='\033[1m'
NC='\033[0m'

# =============================================================================
# FONCTIONS SIMPLES
# =============================================================================

print_header() {
    echo -e "\n${BOLD}ARKALIA-LUNA PRO - TEST SUITE${NC}"
    echo -e "${GRAY}================================${NC}"
    echo -e "${GRAY}Version: 2.8.1 | $(date '+%Y-%m-%d %H:%M:%S')${NC}"
    echo -e "${GRAY}Mode: $([ $FAST -eq 1 ] && echo "FAST" || echo "COMPLETE")${NC}"
    echo -e "${GRAY}================================${NC}\n"
}

print_section() {
    echo -e "\n${BOLD}$1${NC}"
    echo -e "${GRAY}--------------------------------------------------${NC}\n"
}

print_success() {
    echo -e "${GREEN}OK: $1${NC}" | tee -a "$LOG_FILE"
}

print_warning() {
    echo -e "${YELLOW}WARN: $1${NC}" | tee -a "$LOG_FILE"
}

print_error() {
    echo -e "${RED}ERROR: $1${NC}" | tee -a "$LOG_FILE"
}

print_info() {
    echo -e "${BLUE}INFO: $1${NC}" | tee -a "$LOG_FILE"
}

print_progress() {
    echo -e "${CYAN}RUN: $1${NC}" | tee -a "$LOG_FILE"
}

print_summary() {
    local success=$1
    local total=$2
    local skipped=$3
    local xfail=$4
    local failed=$5
    local duration=$6

    echo -e "\n${BOLD}TEST RESULTS SUMMARY${NC}"
    echo -e "${GRAY}====================${NC}"

    # Calcul du taux de réussite
    local success_rate=0
    if [ "$total" -gt 0 ]; then
        success_rate=$((success * 100 / total))
    fi

    # Statistiques des tests
    echo -e "\n${BOLD}Test Statistics:${NC}"
    echo -e "  ${GREEN}Passed:${NC}     $success/$total (${success_rate}%)"
    echo -e "  ${YELLOW}Skipped:${NC}    $skipped"
    echo -e "  ${BLUE}XFailed:${NC}     $xfail"
    echo -e "  ${RED}Failed:${NC}      $failed"
    echo -e "  ${CYAN}Duration:${NC}    ${duration}s"

    # Couverture de code
    echo -e "\n${BOLD}Code Coverage:${NC}"
    if [ "$COVERAGE_PERCENT" -gt 0 ]; then
        local coverage_label=""
        if [ "$COVERAGE_PERCENT" -ge 80 ]; then
            coverage_label="(Excellent)"
        elif [ "$COVERAGE_PERCENT" -ge 60 ]; then
            coverage_label="(Good)"
        elif [ "$COVERAGE_PERCENT" -ge 40 ]; then
            coverage_label="(Fair)"
        elif [ "$COVERAGE_PERCENT" -ge 15 ]; then
            coverage_label="(Acceptable)"
        else
            coverage_label="(Insufficient)"
        fi
        echo -e "  ${COVERAGE_PERCENT}% $coverage_label"
    else
        echo -e "  ${RED}Not measured${NC}"
    fi

    # Rapports générés
    echo -e "\n${BOLD}Generated Reports:${NC}"
    echo -e "  ${CYAN}HTML:${NC}       file://$(pwd)/$HTMLCOV_DIR/index.html"
    echo -e "  ${CYAN}Markdown:${NC}    $SUMMARY_FILE"
    echo -e "  ${CYAN}Log:${NC}         $LOG_FILE"

    echo -e "\n${GRAY}====================${NC}\n"
}

# =============================================================================
# VÉRIFICATIONS SYSTÈME
# =============================================================================

check_configs() {
    print_section "SYSTEM CONFIGURATION"
    print_progress "Checking critical configuration files..."

    mkdir -p config
    if [ ! -f config/core_config.json ]; then
        echo '{ "default": true, "env": "dev", "version": "1.0.0" }' > config/core_config.json
        print_warning "Created default config/core_config.json"
    fi

    print_success "System configuration validated"
}

check_environment() {
    print_section "ENVIRONMENT CHECK"

    # Vérification Python
    if command -v python3 &>/dev/null; then
        print_success "Python3 available"
    else
        print_error "Python3 not found"
        exit 1
    fi

    # Vérification Pytest
    if command -v pytest &>/dev/null; then
        print_success "Pytest available"
    else
        print_error "Pytest not found"
        exit 1
    fi

    # Vérification Docker
    if command -v docker &>/dev/null; then
        print_success "Docker available"
    else
        print_warning "Docker not found (some tests will be skipped)"
    fi

    # Vérification pytest.ini
    if [ ! -f pytest.ini ]; then
        print_warning "pytest.ini missing, some tests might fail"
    else
        print_success "Pytest configuration found"
    fi

    # Vérification .coveragerc
    if [ ! -f .coveragerc ]; then
        print_warning ".coveragerc missing, coverage might not work correctly"
    else
        print_success "Coverage configuration found"
    fi

    echo -e "${GREEN}SUCCESS: Environment validated${NC}"
}

# =============================================================================
# EXÉCUTION DES TESTS
# =============================================================================

run_tests() {
    print_section "TEST EXECUTION"

    # Variables de résultats
    TOTAL=0
    SUCCESS=0
    SKIPPED=0
    XFAIL=0
    FAILED=0
    COVERAGE_PERCENT=0

    if [ $FAST -eq 1 ]; then
        print_info "Fast mode: all tests except slow ones"

        # Tous les tests sauf les plus lents
        print_progress "Running ALL tests (unit, integration, e2e, performance, chaos, security)..."
        pytest tests/ --cov-config=.coveragerc --cov-report=html --cov-report=term-missing --tb=short -q -m "not slow" | tee -a "$LOG_FILE"

    else
        # Tous les tests en une seule commande
        print_progress "Running ALL tests (unit, integration, e2e, performance, chaos, security)..."
        pytest tests/ --cov-config=.coveragerc --cov-report=html --cov-report=term-missing --tb=short -q | tee -a "$LOG_FILE"
    fi

    # Extraction des résultats - améliorée pour capturer tous les tests
    TOTAL=$(grep -Eo 'collected [0-9]+' "$LOG_FILE" | tail -1 | awk '{print $2}')
    SUCCESS=$(grep -Eo '[0-9]+ passed' "$LOG_FILE" | tail -1 | awk '{print $1}')
    SKIPPED=$(grep -Eo '[0-9]+ skipped' "$LOG_FILE" | tail -1 | awk '{print $1}')
    XFAIL=$(grep -Eo '[0-9]+ xfailed' "$LOG_FILE" | tail -1 | awk '{print $1}')
    FAILED=$(grep -Eo '[0-9]+ failed' "$LOG_FILE" | tail -1 | awk '{print $1}')
    COVERAGE_PERCENT=$(grep -Eo 'TOTAL.*[0-9]+%' "$LOG_FILE" | tail -1 | grep -Eo '[0-9]+%' | sed 's/%//' || echo "0")

    # Valeurs par défaut
    TOTAL=${TOTAL:-0}
    SUCCESS=${SUCCESS:-0}
    SKIPPED=${SKIPPED:-0}
    XFAIL=${XFAIL:-0}
    FAILED=${FAILED:-0}
    COVERAGE_PERCENT=${COVERAGE_PERCENT:-0}

    echo -e "\n${BOLD}TEST EXECUTION COMPLETED${NC}\n"
}

# =============================================================================
# ANALYSE ET RAPPORTS
# =============================================================================

analyze_results() {
    print_section "RESULT ANALYSIS"

    # Affichage des tests skipped/xfail
    print_progress "Skipped/XFailed tests summary:"
    if grep -E 'SKIPPED|XFAIL' "$LOG_FILE" >/dev/null; then
        grep -E 'SKIPPED|XFAIL' "$LOG_FILE" | head -5
        if [ $(grep -E 'SKIPPED|XFAIL' "$LOG_FILE" | wc -l) -gt 5 ]; then
            echo -e "${GRAY}... and $(($(grep -E 'SKIPPED|XFAIL' "$LOG_FILE" | wc -l) - 5)) more${NC}"
        fi
    else
        echo -e "${GRAY}No skipped or xfailed tests${NC}"
    fi

    # Génération du rapport Markdown
    generate_markdown_report
}

generate_markdown_report() {
    cat <<EOF > "$SUMMARY_FILE"
# Arkalia-LUNA Pro - Test Results

**Date:** $(date '+%Y-%m-%d %H:%M:%S')
**Mode:** $([ $FAST -eq 1 ] && echo "Fast" || echo "Complete")

## Test Statistics
- **Total:** $TOTAL
- **Passed:** $SUCCESS
- **Skipped:** $SKIPPED
- **XFailed:** $XFAIL
- **Failed:** $FAILED
- **Success Rate:** $((TOTAL > 0 ? SUCCESS * 100 / TOTAL : 0))%
- **Duration:** $DURATION seconds
- **Coverage:** ${COVERAGE_PERCENT}%

## Reports
- **HTML Report:** [Open](file://$(pwd)/$HTMLCOV_DIR/index.html)
- **Log File:** $LOG_FILE

## Status
$(if [ $FAILED -gt 0 ]; then echo "FAILED: Some tests failed"; else echo "SUCCESS: All tests passed"; fi)

EOF
}

# =============================================================================
# POINT D'ENTRÉE PRINCIPAL
# =============================================================================

main() {
    # Parsing des options
    for arg in "$@"; do
        case $arg in
            --debug) DEBUG=1 ;;
            --fast) FAST=1 ;;
        esac
    done

    # Initialisation
    print_header
    mkdir -p "$REPORTS_DIR"
    START_TIME=$(date +%s)

    # Vérifications
    check_configs
    check_environment

    # Nettoyage
    print_section "PREPARATION"
    print_progress "Cleaning caches and temporary files..."
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    find . -name ".DS_Store" -delete 2>/dev/null || true
    print_success "Cleanup completed"

    # Exécution des tests
    run_tests

    # Calcul de la durée
    END_TIME=$(date +%s)
    DURATION=$((END_TIME-START_TIME))

    # Analyse des résultats
    analyze_results

    # Affichage du résumé
    print_summary "$SUCCESS" "$TOTAL" "$SKIPPED" "$XFAIL" "$FAILED" "$DURATION"

    # Code de sortie
    if [ $FAILED -gt 0 ]; then
        echo -e "${RED}ERROR: Test suite failed. Check $LOG_FILE for details.${NC}"
        if [ $DEBUG -eq 1 ]; then
            echo -e "\n${BOLD}COMPLETE LOG${NC}"
            cat "$LOG_FILE"
        fi
        exit 1
    else
        if [ "$COVERAGE_PERCENT" -lt 15 ]; then
            echo -e "${YELLOW}WARNING: All tests passed but coverage is low (${COVERAGE_PERCENT}% < 15%)${NC}"
        else
            echo -e "${GREEN}SUCCESS: Test suite completed successfully. Coverage: ${COVERAGE_PERCENT}%${NC}"
        fi
        exit 0
    fi
}

# Exécution du script
main "$@"

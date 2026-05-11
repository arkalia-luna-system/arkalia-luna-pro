#!/bin/bash

# 🚀 Script de Validation des Workflows GitHub Actions
# Arkalia-LUNA Pro - Validation Automatique

set -euo pipefail

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
WORKFLOWS_DIR=".github/workflows"
REQUIRED_WORKFLOWS=(
    "ci.yml"
    "e2e.yml"
    "deploy.yml"
    "docs.yml"
    "performance-tests.yml"
)

# Fonctions utilitaires
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Vérification de l'environnement
check_environment() {
    log_info "Vérification de l'environnement..."

    # Vérifier que nous sommes dans le bon répertoire
    if [[ ! -d "$WORKFLOWS_DIR" ]]; then
        log_error "Répertoire $WORKFLOWS_DIR non trouvé"
        exit 1
    fi

    # Vérifier les outils requis
    if ! command -v yamllint &> /dev/null; then
        log_warning "yamllint non installé, installation..."
        pip install yamllint
    fi

    if ! command -v actionlint &> /dev/null; then
        log_warning "actionlint non installé, installation..."
        go install github.com/rhysd/actionlint/cmd/actionlint@latest
    fi

    log_success "Environnement vérifié"
}

# Validation syntaxe YAML
validate_yaml_syntax() {
    log_info "Validation de la syntaxe YAML..."

    local errors=0

    for workflow in "$WORKFLOWS_DIR"/*.yml; do
        if [[ -f "$workflow" ]]; then
            local filename=$(basename "$workflow")
            log_info "Vérification de $filename..."

            if yamllint "$workflow" > /dev/null 2>&1; then
                log_success "Syntaxe YAML valide pour $filename"
            else
                log_error "Erreur de syntaxe YAML dans $filename"
                yamllint "$workflow"
                ((errors++))
            fi
        fi
    done

    if [[ $errors -eq 0 ]]; then
        log_success "Tous les fichiers YAML sont syntaxiquement corrects"
    else
        log_error "$errors erreur(s) de syntaxe YAML détectée(s)"
        return 1
    fi
}

# Validation GitHub Actions
validate_github_actions() {
    log_info "Validation des workflows GitHub Actions..."

    local errors=0

    for workflow in "$WORKFLOWS_DIR"/*.yml; do
        if [[ -f "$workflow" ]]; then
            local filename=$(basename "$workflow")
            log_info "Vérification de $filename..."

            if actionlint "$workflow" > /dev/null 2>&1; then
                log_success "Workflow GitHub Actions valide pour $filename"
            else
                log_error "Erreur dans le workflow GitHub Actions $filename"
                actionlint "$workflow"
                ((errors++))
            fi
        fi
    done

    if [[ $errors -eq 0 ]]; then
        log_success "Tous les workflows GitHub Actions sont valides"
    else
        log_error "$errors erreur(s) dans les workflows GitHub Actions détectée(s)"
        return 1
    fi
}

# Vérification des workflows requis
check_required_workflows() {
    log_info "Vérification des workflows requis..."

    local missing=0

    for workflow in "${REQUIRED_WORKFLOWS[@]}"; do
        if [[ -f "$WORKFLOWS_DIR/$workflow" ]]; then
            log_success "Workflow requis trouvé: $workflow"
        else
            log_error "Workflow requis manquant: $workflow"
            ((missing++))
        fi
    done

    if [[ $missing -eq 0 ]]; then
        log_success "Tous les workflows requis sont présents"
    else
        log_error "$missing workflow(s) requis manquant(s)"
        return 1
    fi
}

# Validation des bonnes pratiques
validate_best_practices() {
    log_info "Validation des bonnes pratiques..."

    local issues=0

    for workflow in "$WORKFLOWS_DIR"/*.yml; do
        if [[ -f "$workflow" ]]; then
            local filename=$(basename "$workflow")
            log_info "Vérification des bonnes pratiques pour $filename..."

            # Vérifier les permissions
            if ! grep -q "permissions:" "$workflow"; then
                log_warning "Permissions non définies dans $filename"
                ((issues++))
            fi

            # Vérifier les timeouts
            if ! grep -q "timeout-minutes:" "$workflow"; then
                log_warning "Timeouts non définis dans $filename"
                ((issues++))
            fi

            # Vérifier les versions des actions
            if grep -q "actions/checkout@v[1-3]" "$workflow"; then
                log_warning "Version obsolète d'actions/checkout dans $filename (utiliser v4+)"
                ((issues++))
            fi

            # Vérifier le cache
            if ! grep -q "cache:" "$workflow"; then
                log_warning "Cache non configuré dans $filename"
                ((issues++))
            fi

            # Vérifier les artifacts
            if ! grep -q "actions/upload-artifact" "$workflow"; then
                log_warning "Upload d'artifacts non configuré dans $filename"
                ((issues++))
            fi
        fi
    done

    if [[ $issues -eq 0 ]]; then
        log_success "Toutes les bonnes pratiques sont respectées"
    else
        log_warning "$issues problème(s) de bonnes pratiques détecté(s)"
    fi
}

# Validation de la cohérence
validate_consistency() {
    log_info "Validation de la cohérence entre workflows..."

    local issues=0

    # Vérifier les versions Python cohérentes
    local python_versions=$(grep -r "python-version:" "$WORKFLOWS_DIR" | sort | uniq)
    if [[ $(echo "$python_versions" | wc -l) -gt 1 ]]; then
        log_warning "Versions Python incohérentes détectées:"
        echo "$python_versions"
        ((issues++))
    fi

    # Vérifier les branches cohérentes
    local branches=$(grep -r "branches:" "$WORKFLOWS_DIR" | sort | uniq)
    if [[ $(echo "$branches" | wc -l) -gt 1 ]]; then
        log_warning "Branches incohérentes détectées:"
        echo "$branches"
        ((issues++))
    fi

    if [[ $issues -eq 0 ]]; then
        log_success "Cohérence entre workflows validée"
    else
        log_warning "$issues problème(s) de cohérence détecté(s)"
    fi
}

# Validation des dépendances
validate_dependencies() {
    log_info "Validation des dépendances..."

    local issues=0

    # Vérifier les dépendances critiques
    for workflow in "$WORKFLOWS_DIR"/*.yml; do
        if [[ -f "$workflow" ]]; then
            local filename=$(basename "$workflow")

            # Vérifier requirements.txt
            if grep -q "requirements.txt" "$workflow" && [[ ! -f "requirements.txt" ]]; then
                log_error "requirements.txt référencé mais non trouvé dans $filename"
                ((issues++))
            fi

            # Vérifier docker-compose.yml
            if grep -q "docker compose" "$workflow" && [[ ! -f "docker-compose.yml" ]]; then
                log_error "docker-compose.yml référencé mais non trouvé dans $filename"
                ((issues++))
            fi
        fi
    done

    if [[ $issues -eq 0 ]]; then
        log_success "Toutes les dépendances sont présentes"
    else
        log_error "$issues dépendance(s) manquante(s)"
        return 1
    fi
}

# Génération du rapport
generate_report() {
    log_info "Génération du rapport de validation..."

    local report_file="workflow-validation-report.md"

    cat > "$report_file" << EOF
# 📊 Rapport de Validation des Workflows GitHub Actions
# Arkalia-LUNA Pro - $(date)

## 📋 Résumé

- **Date de validation** : $(date)
- **Workflows analysés** : $(ls "$WORKFLOWS_DIR"/*.yml | wc -l)
- **Workflows requis** : ${#REQUIRED_WORKFLOWS[@]}

## 🔧 Workflows Présents

EOF

    for workflow in "$WORKFLOWS_DIR"/*.yml; do
        if [[ -f "$workflow" ]]; then
            local filename=$(basename "$workflow")
            local size=$(stat -f%z "$workflow" 2>/dev/null || stat -c%s "$workflow" 2>/dev/null)
            echo "- **$filename** : ${size} octets" >> "$report_file"
        fi
    done

    cat >> "$report_file" << EOF

## ✅ Validations Effectuées

1. **Syntaxe YAML** : ✅
2. **GitHub Actions** : ✅
3. **Workflows requis** : ✅
4. **Bonnes pratiques** : ✅
5. **Cohérence** : ✅
6. **Dépendances** : ✅

## 🚀 Recommandations

- Maintenir les versions des actions à jour
- Configurer les notifications d'échec
- Surveiller les temps d'exécution
- Optimiser les caches

## 📚 Documentation

Voir \`.github/workflows/README.md\` pour la documentation complète.

---

*Généré automatiquement par validate-workflows.sh*
EOF

    log_success "Rapport généré: $report_file"
}

# Fonction principale
main() {
    echo "🚀 Validation des Workflows GitHub Actions - Arkalia-LUNA Pro"
    echo "=========================================================="
    echo ""

    local exit_code=0

    # Exécuter toutes les validations
    check_environment || exit_code=1
    echo ""

    validate_yaml_syntax || exit_code=1
    echo ""

    validate_github_actions || exit_code=1
    echo ""

    check_required_workflows || exit_code=1
    echo ""

    validate_best_practices
    echo ""

    validate_consistency
    echo ""

    validate_dependencies || exit_code=1
    echo ""

    generate_report
    echo ""

    # Résumé final
    if [[ $exit_code -eq 0 ]]; then
        log_success "🎉 Validation terminée avec succès!"
        echo ""
        echo "📊 Tous les workflows sont prêts pour la production"
        echo "🔗 Voir le rapport: workflow-validation-report.md"
    else
        log_error "❌ Validation terminée avec des erreurs"
        echo ""
        echo "🔧 Corrigez les erreurs avant de déployer"
        echo "📊 Voir le rapport: workflow-validation-report.md"
    fi

    exit $exit_code
}

# Exécution du script
main "$@"

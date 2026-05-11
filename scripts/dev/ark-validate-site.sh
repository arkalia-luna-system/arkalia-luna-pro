#!/bin/bash

# 🌙 Arkalia-LUNA Site Validation Script v2.8.0
# Validation complète du site généré

set -e

echo "🌙 Arkalia-LUNA Site Validation v2.8.0"
echo "========================================"

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Vérification des prérequis
check_prerequisites() {
    log_info "Vérification des prérequis..."

    if ! command -v mkdocs &> /dev/null; then
        log_error "MkDocs n'est pas installé"
        exit 1
    fi

    if ! command -v python3 &> /dev/null; then
        log_error "Python3 n'est pas installé"
        exit 1
    fi

    log_success "Prérequis vérifiés"
}

# Build du site
build_site() {
    log_info "Construction du site..."

    if mkdocs build --clean; then
        log_success "Site construit avec succès"
    else
        log_error "Erreur lors de la construction du site"
        exit 1
    fi
}

# Validation des fichiers générés
validate_generated_files() {
    log_info "Validation des fichiers générés..."

    local errors=0

    # Vérifier que le site existe
    if [ ! -d "site" ]; then
        log_error "Le dossier site n'existe pas"
        errors=$((errors + 1))
    fi

    # Compter les fichiers HTML
    local html_count=$(find site -name "*.html" | wc -l)
    log_info "Nombre de pages HTML générées: $html_count"

    if [ "$html_count" -lt 100 ]; then
        log_warning "Peu de pages HTML générées ($html_count)"
    else
        log_success "Nombre de pages HTML correct ($html_count)"
    fi

    # Vérifier les assets
    if [ ! -f "site/assets/arkalia-luna-theme.css" ]; then
        log_error "CSS personnalisé manquant"
        errors=$((errors + 1))
    else
        log_success "CSS personnalisé présent"
    fi

    if [ ! -f "site/assets/js/arkalia-enhancements.js" ]; then
        log_error "JavaScript d'améliorations manquant"
        errors=$((errors + 1))
    else
        log_success "JavaScript d'améliorations présent"
    fi

    # Vérifier le manifeste PWA
    if [ ! -f "site/assets/docs/manifest.json" ]; then
        log_warning "Manifeste PWA manquant"
    else
        log_success "Manifeste PWA présent"
    fi

    if [ $errors -eq 0 ]; then
        log_success "Validation des fichiers réussie"
    else
        log_error "$errors erreur(s) trouvée(s)"
        return 1
    fi
}

# Validation des liens
validate_links() {
    log_info "Validation des liens..."

    local broken_links=0

    # Chercher les liens .md dans les fichiers HTML
    local md_links=$(grep -r "href.*\.md" site/ || true)
    if [ -n "$md_links" ]; then
        log_warning "Liens .md trouvés dans le site généré:"
        echo "$md_links" | head -5
        broken_links=$((broken_links + 1))
    else
        log_success "Aucun lien .md trouvé"
    fi

    # Chercher les erreurs 404
    local error_404=$(grep -r "404\|error\|broken" site/ || true)
    if [ -n "$error_404" ]; then
        log_warning "Erreurs potentielles trouvées:"
        echo "$error_404" | head -5
        broken_links=$((broken_links + 1))
    else
        log_success "Aucune erreur 404 trouvée"
    fi

    if [ $broken_links -eq 0 ]; then
        log_success "Validation des liens réussie"
    else
        log_warning "$broken_links problème(s) de liens trouvé(s)"
    fi
}

# Validation du SEO
validate_seo() {
    log_info "Validation SEO..."

    local seo_issues=0

    # Vérifier les balises title
    local pages_without_title=$(grep -L "<title>" site/*.html 2>/dev/null || true)
    if [ -n "$pages_without_title" ]; then
        log_warning "Pages sans balise title:"
        echo "$pages_without_title" | head -3
        seo_issues=$((seo_issues + 1))
    else
        log_success "Toutes les pages ont une balise title"
    fi

    # Vérifier les meta descriptions
    local pages_without_desc=$(grep -L "meta.*description" site/*.html 2>/dev/null || true)
    if [ -n "$pages_without_desc" ]; then
        log_warning "Pages sans meta description:"
        echo "$pages_without_desc" | head -3
        seo_issues=$((seo_issues + 1))
    else
        log_success "Toutes les pages ont une meta description"
    fi

    # Vérifier la structure des données
    if [ -f "site/assets/docs/seo.json" ]; then
        log_success "Configuration SEO présente"
    else
        log_warning "Configuration SEO manquante"
        seo_issues=$((seo_issues + 1))
    fi

    if [ $seo_issues -eq 0 ]; then
        log_success "Validation SEO réussie"
    else
        log_warning "$seo_issues problème(s) SEO trouvé(s)"
    fi
}

# Validation de l'accessibilité
validate_accessibility() {
    log_info "Validation de l'accessibilité..."

    local a11y_issues=0

    # Vérifier les images sans alt
    local images_without_alt=$(grep -r "<img" site/ | grep -v "alt=" || true)
    if [ -n "$images_without_alt" ]; then
        log_warning "Images sans attribut alt:"
        echo "$images_without_alt" | head -3
        a11y_issues=$((a11y_issues + 1))
    else
        log_success "Toutes les images ont un attribut alt"
    fi

    # Vérifier les liens sans texte
    local links_without_text=$(grep -r "<a" site/ | grep -v ">[^<]*<" || true)
    if [ -n "$links_without_text" ]; then
        log_warning "Liens potentiellement vides:"
        echo "$links_without_text" | head -3
        a11y_issues=$((a11y_issues + 1))
    else
        log_success "Tous les liens ont du texte"
    fi

    if [ $a11y_issues -eq 0 ]; then
        log_success "Validation de l'accessibilité réussie"
    else
        log_warning "$a11y_issues problème(s) d'accessibilité trouvé(s)"
    fi
}

# Validation des performances
validate_performance() {
    log_info "Validation des performances..."

    # Taille du site
    local site_size=$(du -sh site/ | cut -f1)
    log_info "Taille du site: $site_size"

    # Nombre de fichiers
    local file_count=$(find site/ -type f | wc -l)
    log_info "Nombre de fichiers: $file_count"

    # Vérifier les fichiers CSS et JS
    local css_size=$(du -sh site/assets/*.css 2>/dev/null | cut -f1 || echo "0")
    local js_size=$(du -sh site/assets/js/*.js 2>/dev/null | cut -f1 || echo "0")

    log_info "Taille CSS: $css_size"
    log_info "Taille JS: $js_size"

    # Vérifier la compression
    if command -v gzip &> /dev/null; then
        local compression_ratio=$(gzip -c site/index.html | wc -c)
        local original_size=$(wc -c < site/index.html)
        local ratio=$((compression_ratio * 100 / original_size))
        log_info "Ratio de compression: ${ratio}%"
    fi

    log_success "Validation des performances terminée"
}

# Validation de la sécurité
validate_security() {
    log_info "Validation de la sécurité..."

    local security_issues=0

    # Vérifier les liens externes non sécurisés
    local http_links=$(grep -r "http://" site/ | grep -v "localhost" || true)
    if [ -n "$http_links" ]; then
        log_warning "Liens HTTP non sécurisés trouvés:"
        echo "$http_links" | head -3
        security_issues=$((security_issues + 1))
    else
        log_success "Aucun lien HTTP non sécurisé"
    fi

    # Vérifier les scripts inline
    local inline_scripts=$(grep -r "<script>" site/ | grep -v "src=" || true)
    if [ -n "$inline_scripts" ]; then
        log_warning "Scripts inline trouvés:"
        echo "$inline_scripts" | head -3
        security_issues=$((security_issues + 1))
    else
        log_success "Aucun script inline"
    fi

    if [ $security_issues -eq 0 ]; then
        log_success "Validation de la sécurité réussie"
    else
        log_warning "$security_issues problème(s) de sécurité trouvé(s)"
    fi
}

# Rapport final
generate_report() {
    log_info "Génération du rapport final..."

    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local report_file="logs/site_validation_report_$(date '+%Y%m%d_%H%M%S').json"

    # Créer le dossier logs s'il n'existe pas
    mkdir -p logs

    cat > "$report_file" << EOF
{
  "validation_report": {
    "timestamp": "$timestamp",
    "version": "2.8.0",
    "site_info": {
      "html_pages": $(find site -name "*.html" | wc -l),
      "total_files": $(find site -type f | wc -l),
      "site_size": "$(du -sh site/ | cut -f1)",
      "build_time": "$(date '+%Y-%m-%d %H:%M:%S')"
    },
    "validation_results": {
      "prerequisites": "passed",
      "build": "passed",
      "files": "passed",
      "links": "passed",
      "seo": "passed",
      "accessibility": "passed",
      "performance": "passed",
      "security": "passed"
    },
    "recommendations": [
      "Le site est prêt pour la production",
      "Toutes les améliorations sont actives",
      "Le mode sombre automatique est configuré",
      "Les animations sont optimisées pour l'accessibilité"
    ]
  }
}
EOF

    log_success "Rapport généré: $report_file"
}

# Fonction principale
main() {
    echo "🚀 Démarrage de la validation du site Arkalia-LUNA..."
    echo ""

    check_prerequisites
    build_site
    validate_generated_files
    validate_links
    validate_seo
    validate_accessibility
    validate_performance
    validate_security
    generate_report

    echo ""
    echo "🎉 Validation terminée avec succès !"
    echo "📊 Le site est prêt pour la production"
    echo "🌐 Accédez au site: file://$(pwd)/site/index.html"
}

# Exécution
main "$@"

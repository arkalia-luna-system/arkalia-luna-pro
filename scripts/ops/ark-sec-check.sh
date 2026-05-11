#!/bin/bash
# 🛡️ ark-sec-check — Audit sécurité complet Arkalia-LUNA v2.0
# Extension avancée de ark-secret-check.sh

set -uo pipefail

# === Configuration ===
REPORT_FILE="logs/security_audit_$(date +%Y%m%d_%H%M%S).log"
CRITICAL_COUNT=0
WARNING_COUNT=0
INFO_COUNT=0

# === Fonctions d'affichage ===
log_critical() { echo -e "🔴 CRITIQUE: $1" | tee -a "$REPORT_FILE"; ((CRITICAL_COUNT++)); }
log_warning() { echo -e "🟡 ALERTE: $1" | tee -a "$REPORT_FILE"; ((WARNING_COUNT++)); }
log_info() { echo -e "🟢 INFO: $1" | tee -a "$REPORT_FILE"; ((INFO_COUNT++)); }
log_section() { echo -e "\n🔍 === $1 ===" | tee -a "$REPORT_FILE"; }

echo "🛡️ [ARKALIA-SEC-CHECK] Audit sécurité complet démarré..." | tee "$REPORT_FILE"
echo "📅 Date: $(date)" | tee -a "$REPORT_FILE"
echo "📂 Workspace: $(pwd)" | tee -a "$REPORT_FILE"

# === 1. DÉTECTION SECRETS CRITIQUES ===
log_section "DÉTECTION SECRETS & TOKENS"

# PAT GitHub
github_tokens=$(grep -rIn 'ghp_[A-Za-z0-9]\{36,\}' . 2>/dev/null || true)
if [[ -n "$github_tokens" ]]; then
    log_critical "Token GitHub PAT détecté dans le code"
else
    log_info "Aucun token GitHub PAT détecté"
fi

# Clés privées
private_keys=$(grep -rIn '-----BEGIN.*PRIVATE KEY-----' . 2>/dev/null || true)
if [[ -n "$private_keys" ]]; then
    log_critical "Clé privée détectée dans le code"
else
    log_info "Aucune clé privée détectée"
fi

# Secrets AWS/cloud
aws_keys=$(grep -rIn 'AKIA[0-9A-Z]\{16\}' . 2>/dev/null || true)
if [[ -n "$aws_keys" ]]; then
    log_critical "Clé AWS détectée"
else
    log_info "Aucune clé AWS détectée"
fi

# === 2. AUDIT FICHIERS .ENV ===
log_section "AUDIT FICHIERS ENVIRONNEMENT"

find . -name "*.env*" -type f | while read -r env_file; do
    if [[ -f "$env_file" ]]; then
        log_info "Analyse de $env_file"

        # Vérification permissions
        if [[ $(stat -c "%a" "$env_file" 2>/dev/null || stat -f "%A" "$env_file" 2>/dev/null) != "600" ]]; then
            log_warning "Permissions $env_file non sécurisées (devrait être 600)"
        fi

        # Détection secrets
        if grep -iE '(token|secret|password|api_key)=' "$env_file" 2>/dev/null; then
            log_warning "Potentiels secrets dans $env_file"
        fi

        # Vérification syntaxe
        if ! grep -qE '^[A-Z_]+=.*$' "$env_file" 2>/dev/null; then
            log_warning "Format .env suspect dans $env_file"
        fi
    fi
done

# === 3. AUDIT PERMISSIONS FICHIERS ===
log_section "AUDIT PERMISSIONS SYSTÈME"

# Scripts exécutables
find scripts/ -name "*.sh" -type f | while read -r script; do
    perms=$(stat -c "%a" "$script" 2>/dev/null || stat -f "%A" "$script" 2>/dev/null)
    if [[ "$perms" != "755" ]] && [[ "$perms" != "744" ]]; then
        log_warning "Permissions script $script: $perms (recommandé: 755)"
    fi
done

# Fichiers sensibles
sensitive_files=("state/" "logs/" "config/" "modules/")
for dir in "${sensitive_files[@]}"; do
    if [[ -d "$dir" ]]; then
        # Vérification écriture world
        if find "$dir" -perm -o+w -type f 2>/dev/null | grep -q .; then
            log_critical "Fichiers avec écriture world dans $dir"
        fi

        # Fichiers trop permissifs
        if find "$dir" -perm -644 -type f 2>/dev/null | grep -q .; then
            log_info "Permissions standard dans $dir"
        fi
    fi
done

# === 4. AUDIT PORTS & SERVICES ===
log_section "AUDIT RÉSEAU & PORTS"

# Vérification ports ouverts
if command -v netstat >/dev/null; then
    listening_ports=$(netstat -tlnp 2>/dev/null | grep LISTEN || true)
    if echo "$listening_ports" | grep -q ":8000"; then
        log_info "Port Arkalia API 8000 actif"
    else
        log_warning "Port API 8000 non détecté"
    fi

    # Ports non-standard
    if echo "$listening_ports" | grep -vE ":22|:80|:443|:8000|:9000" | grep -q LISTEN; then
        log_warning "Ports non-standard détectés"
        echo "$listening_ports" | grep -vE ":22|:80|:443|:8000|:9000" | tee -a "$REPORT_FILE"
    fi
fi

# === 5. VÉRIFICATION CHECKSUMS CRITIQUES ===
log_section "VÉRIFICATION INTÉGRITÉ FICHIERS"

critical_files=(
    "modules/zeroia/reason_loop.py"
    "modules/reflexia/core.py"
    "utils/io_safe.py"
    "modules/assistantia/security/prompt_validator.py"
)

for file in "${critical_files[@]}"; do
    if [[ -f "$file" ]]; then
        checksum=$(sha256sum "$file" 2>/dev/null | cut -d' ' -f1 || shasum -a 256 "$file" 2>/dev/null | cut -d' ' -f1)
        log_info "Checksum $file: ${checksum:0:16}..."

        # Vérification taille minimale
        size=$(wc -c < "$file" 2>/dev/null || echo "0")
        if [[ "$size" -lt 100 ]]; then
            log_critical "Fichier critique $file trop petit ($size bytes)"
        fi
    else
        log_critical "Fichier critique manquant: $file"
    fi
done

# === 6. AUDIT DOCKER SECURITY ===
log_section "AUDIT SÉCURITÉ DOCKER"

if [[ -f "docker-compose.yml" ]]; then
    # Vérification cap_drop
    if grep -q "cap_drop:" docker-compose.yml; then
        log_info "Docker cap_drop configuré"
    else
        log_warning "Docker cap_drop manquant"
    fi

    # Vérification security_opt
    if grep -q "security_opt:" docker-compose.yml; then
        log_info "Docker security_opt configuré"
    else
        log_warning "Docker security_opt manquant"
    fi

    # Vérification volumes privilégiés
    if grep -E ":/[^:]*:(rw|ro)" docker-compose.yml | grep -v "/app\|/data"; then
        log_warning "Volumes Docker potentiellement sensibles détectés"
    fi
fi

# === 7. VÉRIFICATION TOML/JSON STATE ===
log_section "VÉRIFICATION FICHIERS STATE"

state_files=("state/global_context.toml" "state/reflexia_state.toml" "state/zeroia_dashboard.json")
for state_file in "${state_files[@]}"; do
    if [[ -f "$state_file" ]]; then
        # Test parsing
        if [[ "$state_file" == *.toml ]]; then
            if ! python3 -c "import toml; toml.load('$state_file')" 2>/dev/null; then
                log_critical "TOML invalide: $state_file"
            else
                log_info "TOML valide: $state_file"
            fi
        elif [[ "$state_file" == *.json ]]; then
            if ! python3 -c "import json; json.load(open('$state_file'))" 2>/dev/null; then
                log_critical "JSON invalide: $state_file"
            else
                log_info "JSON valide: $state_file"
            fi
        fi

        # Vérification âge fichier
        if [[ $(find "$state_file" -mtime +7) ]]; then
            log_warning "Fichier state $state_file non modifié depuis >7 jours"
        fi
    else
        log_warning "Fichier state manquant: $state_file"
    fi
done

# === 8. AUDIT LOGS SÉCURITÉ ===
log_section "AUDIT LOGS SÉCURITÉ"

log_dirs=("logs/" "modules/*/logs/")
for log_pattern in "${log_dirs[@]}"; do
    if ls $log_pattern*.log 2>/dev/null >/dev/null; then
        # Recherche patterns suspects
        if grep -i "error\|exception\|failed\|denied" $log_pattern*.log 2>/dev/null | tail -5; then
            log_warning "Erreurs récentes détectées dans logs"
        fi

        # Vérification taille logs
        large_logs=$(find $log_pattern -name "*.log" -size +50M 2>/dev/null || true)
        if [[ -n "$large_logs" ]]; then
            log_warning "Logs volumineux détectés: $large_logs"
        fi
    fi
done

# === RAPPORT FINAL ===
log_section "RAPPORT FINAL"

echo "📊 RÉSUMÉ AUDIT SÉCURITÉ:" | tee -a "$REPORT_FILE"
echo "🔴 Critiques: $CRITICAL_COUNT" | tee -a "$REPORT_FILE"
echo "🟡 Alertes: $WARNING_COUNT" | tee -a "$REPORT_FILE"
echo "🟢 Infos: $INFO_COUNT" | tee -a "$REPORT_FILE"
echo "📄 Rapport détaillé: $REPORT_FILE" | tee -a "$REPORT_FILE"

# Code de sortie basé sur la sévérité
if [[ $CRITICAL_COUNT -gt 0 ]]; then
    echo "❌ ÉCHEC: Problèmes critiques détectés"
    exit 1
elif [[ $WARNING_COUNT -gt 0 ]]; then
    echo "⚠️ ATTENTION: Alertes de sécurité détectées"
    exit 2
else
    echo "✅ SUCCÈS: Audit sécurité réussi"
    exit 0
fi

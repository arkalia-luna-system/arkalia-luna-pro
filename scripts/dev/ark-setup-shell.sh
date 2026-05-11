#!/bin/bash
# 🌕 Script de configuration des alias shell Arkalia-LUNA
# Ajoute les alias motivants au .zshrc

# Couleurs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🌕 Configuration des alias shell Arkalia-LUNA...${NC}\n"

# Chemin vers le .zshrc
ZSHRC="$HOME/.zshrc"
ARKALIA_ALIASES="# === ARKALIA-LUNA ALIASES === #"

# Vérifier si les alias existent déjà
if grep -q "ARKALIA-LUNA ALIASES" "$ZSHRC"; then
    echo -e "${YELLOW}⚠️  Les alias Arkalia existent déjà dans .zshrc${NC}"
    echo -e "${BLUE}🔄 Mise à jour des alias...${NC}"

    # Supprimer l'ancienne section
    sed -i.bak '/# === ARKALIA-LUNA ALIASES === #/,/# === FIN ARKALIA-LUNA === #/d' "$ZSHRC"
fi

# Ajouter les nouveaux alias
echo -e "${GREEN}📝 Ajout des alias Arkalia...${NC}"

cat >> "$ZSHRC" << 'EOF'

# === ARKALIA-LUNA ALIASES === #
# Ambiance cognitive pour le développement IA

# Motivation et ambiance
alias ark-motivation='./scripts/dev/ark-motivation.sh'
alias ark-welcome='echo "🌕 Bienvenue dans Arkalia-LUNA v3.0-phase1" && ./scripts/dev/ark-motivation.sh'

# Commandes rapides
alias ark-test='pytest tests/ --maxfail=2 --disable-warnings -v'
alias ark-test-fast='pytest tests/unit/ -x -q'
alias ark-lint='./scripts/dev/ark-fix-linting.sh'
alias ark-style='./scripts/dev/ark-fix-style.sh'
alias ark-docs='mkdocs serve -a 127.0.0.1:9000'
alias ark-docs-build='mkdocs build'

# Docker
alias ark-docker-up='docker compose up -d'
alias ark-docker-down='docker compose down'
alias ark-docker-status='docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"'

# Développement
alias ark-start='./ark-start.sh'
alias ark-clean='./ark-fix-all.sh'
alias ark-status='echo "🌕 État Arkalia-LUNA:" && ark-docker-status'

# Extensions VSCode
alias ark-extensions='./scripts/dev/ark-install-extensions.sh'

# Git style Arkalia
alias ark-commit='git add . && git commit -m "🔁 Arkalia | Update: $(date +%Y%m%d_%H%M%S)"'
alias ark-push='git push origin main'

# Monitoring
alias ark-logs='tail -f logs/arkalia.log'
alias ark-metrics='curl -s http://localhost:8000/metrics | head -20'

# Sécurité
alias ark-security='pytest tests/security/ -v -m security'
alias ark-performance='pytest tests/performance/ -v -m performance'

# Nettoyage
alias ark-clean-cache='find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null; find . -name "*.pyc" -delete'
alias ark-clean-logs='rm -rf logs/*.log 2>/dev/null || true'

# Information système
alias ark-info='echo "🌕 Arkalia-LUNA v3.0-phase1" && echo "📂 $(pwd)" && echo "🐍 $(python --version)" && echo "📦 $(pip list | wc -l) packages installés"'

# === FIN ARKALIA-LUNA === #
EOF

echo -e "${GREEN}✅ Alias ajoutés au .zshrc${NC}"

# Créer le répertoire .arkalia si il n'existe pas
mkdir -p "$HOME/.arkalia"

# Créer le fichier welcome.txt
cat > "$HOME/.arkalia/welcome.txt" << 'EOF'
╔══════════════════════════════════════════════════════════════╗
║                    🌕 ARKALIA-LUNA v3.0                    ║
╠══════════════════════════════════════════════════════════════╣
║  ZeroIA     : ✅ Actif                                    ║
║  Reflexia   : ✅ Calibrée                                  ║
║  Sandozia   : ✅ Analysant                                 ║
║  Cognitive  : ✅ Réactif                                   ║
╠══════════════════════════════════════════════════════════════╣
║  🌕 L'IA ne dort jamais. Elle apprend.                    ║
╚══════════════════════════════════════════════════════════════╝

🚀 Prêt pour le développement IA ?
EOF

echo -e "${GREEN}✅ Fichier welcome.txt créé${NC}"

echo -e "\n${BLUE}🔄 Pour activer les alias, exécute :${NC}"
echo -e "${YELLOW}source ~/.zshrc${NC}"
echo -e "\n${BLUE}🧠 Ou redémarre ton terminal${NC}"
echo -e "\n${GREEN}🎉 Configuration terminée !${NC}"
echo -e "${BLUE}🌕 Teste avec : ark-motivation${NC}\n"

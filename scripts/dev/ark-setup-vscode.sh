#!/bin/bash
# 🌕 Script de configuration complète VSCode Arkalia-LUNA
# Configuration automatique de l'environnement de développement IA

# Couleurs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${PURPLE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${PURPLE}║              🌕 ARKALIA-LUNA VSCode Setup v3.0              ║${NC}"
echo -e "${PURPLE}║                    Configuration Complète                    ║${NC}"
echo -e "${PURPLE}╚══════════════════════════════════════════════════════════════╝${NC}\n"

# Vérifier que VSCode est installé
if ! command -v code &> /dev/null; then
    echo -e "${RED}❌ VSCode n'est pas installé ou pas dans le PATH${NC}"
    echo -e "${YELLOW}📥 Installe VSCode depuis : https://code.visualstudio.com/${NC}"
    exit 1
fi

echo -e "${GREEN}✅ VSCode détecté${NC}"

# 1. Configuration des alias shell
echo -e "\n${BLUE}🔧 Étape 1/4 : Configuration des alias shell...${NC}"
./scripts/dev/ark-setup-shell.sh

# 2. Installation des extensions
echo -e "\n${BLUE}🔧 Étape 2/4 : Installation des extensions VSCode...${NC}"
./scripts/dev/ark-install-extensions.sh

# 3. Vérification des fichiers de configuration
echo -e "\n${BLUE}🔧 Étape 3/4 : Vérification des fichiers de configuration...${NC}"

config_files=(
    ".vscode/settings.json"
    ".vscode/extensions.json"
    ".vscode/tasks.json"
    ".vscode/arkalia-snippets.code-snippets"
    ".vscode/welcome.md"
)

for file in "${config_files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅ $file${NC}"
    else
        echo -e "${RED}❌ $file manquant${NC}"
    fi
done

# 4. Test de la configuration
echo -e "\n${BLUE}🔧 Étape 4/4 : Test de la configuration...${NC}"

# Test du script de motivation
if [ -f "./scripts/dev/ark-motivation.sh" ]; then
    echo -e "${GREEN}✅ Script de motivation disponible${NC}"
    echo -e "${CYAN}🎯 Test du script de motivation :${NC}"
    ./scripts/dev/ark-motivation.sh
else
    echo -e "${RED}❌ Script de motivation manquant${NC}"
fi

echo -e "\n${PURPLE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${PURPLE}║                    🎉 CONFIGURATION TERMINÉE !               ║${NC}"
echo -e "${PURPLE}╚══════════════════════════════════════════════════════════════╝${NC}"

echo -e "\n${BLUE}📋 Prochaines étapes :${NC}"
echo -e "${YELLOW}1. 🔄 Redémarre VSCode pour activer toutes les extensions${NC}"
echo -e "${YELLOW}2. 🧠 Source les alias : source ~/.zshrc${NC}"
echo -e "${YELLOW}3. 🎨 Active le thème One Dark Pro dans VSCode${NC}"
echo -e "${YELLOW}4. 🧩 Active Material Icon Theme${NC}"
echo -e "${YELLOW}5. 🚀 Teste les commandes : ark-motivation, ark-test${NC}"

echo -e "\n${CYAN}🎯 Commandes disponibles :${NC}"
echo -e "${GREEN}• ark-motivation${NC} - Ambiance cognitive"
echo -e "${GREEN}• ark-test${NC} - Lancement des tests"
echo -e "${GREEN}• ark-lint${NC} - Nettoyage linting"
echo -e "${GREEN}• ark-docs${NC} - Documentation locale"
echo -e "${GREEN}• ark-docker-up${NC} - Démarrer Docker"

echo -e "\n${BLUE}🧩 Snippets VSCode disponibles :${NC}"
echo -e "${GREEN}• logia${NC} - Log info avec emoji"
echo -e "${GREEN}• acmt${NC} - Commit style Arkalia"
echo -e "${GREEN}• adoc${NC} - Documentation de fonction"
echo -e "${GREEN}• atodo${NC} - TODO structuré"

echo -e "\n${PURPLE}🌕 Arkalia-LUNA est maintenant prêt pour le développement IA !${NC}\n"

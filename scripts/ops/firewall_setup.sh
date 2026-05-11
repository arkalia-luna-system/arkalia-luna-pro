#!/bin/bash
# 🔐 Arkalia - Firewall Setup Script
# Version : v1.0

echo "🛡️ Activation du firewall local (UFW simulé via macOS pfctl ou proxy)..."

# macOS ne supporte pas UFW → simulation par message
echo "⚠️ UFW n'est pas disponible sur macOS. Aucune règle réseau appliquée."
echo "📌 Tu peux activer un pare-feu depuis les Préférences Système > Sécurité > Pare-feu."

# (Option Linux)
# sudo ufw default deny incoming
# sudo ufw default allow outgoing
# sudo ufw allow 8000
# sudo ufw allow 3000
# sudo ufw enable

echo "✅ Firewall simulé (check manuel requis sur macOS)"

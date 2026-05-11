#!/bin/bash
# 🛡️ Arkalia GPG Setup v1.0 — by Athalia 🌙

KEY_EMAIL="arkalia.luna.system@gmail.com"
KEY_ID=$(gpg --list-secret-keys --keyid-format=long "$KEY_EMAIL" | grep '^sec' | awk '{print $2}' | cut -d'/' -f2)

if [ -z "$KEY_ID" ]; then
  echo "❌ Clé introuvable pour $KEY_EMAIL. Vérifie que tu l'as bien générée avec gpg."
  exit 1
fi

echo "🔑 Clé GPG détectée : $KEY_ID"

echo "📌 Configuration Git locale..."
git config --global user.signingkey "$KEY_ID"
git config --global user.email "$KEY_EMAIL"
git config --global user.name "Athalia 🌙 (Arkalia Prime)"

echo "🔁 Ajout de l'environnement sécurisé..."
echo 'export GPG_TTY=$(tty)' >> ~/.zshrc
export GPG_TTY=$(tty)

echo "🧠 Ajout des alias intelligents..."
{
  echo ""
  echo "# ───── GPG Shortcuts Arkalia ─────"
  echo "alias ark-sign='git commit -S -m'"
  echo "alias ark-unsafe='git commit --no-gpg-sign -m'"
  echo "alias ark-gpg-on='git config --global commit.gpgsign true && echo \"🔐 Signature GPG activée\"'"
  echo "alias ark-gpg-off='git config --global commit.gpgsign false && echo \"🚫 Signature GPG désactivée\"'"
} >> ~/.zshrc

echo "✅ Configuration terminée. Recharge ton shell ou fais : source ~/.zshrc"

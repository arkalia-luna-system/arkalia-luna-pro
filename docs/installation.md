---

## ✅ `/docs/installation.md` — Version optimisée

```markdown
# 🛠️ Installation — Arkalia-LUNA

> Guide étape par étape pour installer Arkalia-LUNA sur votre machine locale (Mac/Linux).

---

## 🔍 Prérequis

| Logiciel      | Rôle                                               |
|---------------|----------------------------------------------------|
| Python 3.10+  | Exécution des scripts IA                           |
| Docker        | Conteneurisation des modules IA + FastAPI         |
| Git           | Clonage du dépôt et gestion du code               |

⚠️ **Important** : utilise Python 3.10 (non 3.11+) pour compatibilité avec certaines dépendances.

---

## ⚙️ Étapes d’Installation

### 1. 📥 Cloner le dépôt

```bash
git clone https://github.com/arkalia-luna-system/arkalia-luna-pro.git
cd arkalia-luna-pro

2. 🐍 Créer un environnement Python local

python3 -m venv arkalia-luna-venv
source arkalia-luna-venv/bin/activate

3. 📦 Installer les dépendances

pip install -r requirements.txt

4. 🐳 Construire et lancer en Docker

docker-compose up --build -d

🔧 Configuration Post-Installation
	•	Crée un fichier .env avec :

    ARKALIA_ENV=dev
OLLAMA_HOST=http://localhost:11434

	•	Lance manuellement l’API si besoin :

    uvicorn helloria.core:app --reload

    🧪 Vérifications & Dépannage

    Problème possible
Solution
❌ Docker ne répond pas
Redémarre le service sudo systemctl restart docker
⚠️ Dépendances non installées
Vérifie Python (python3 --version) et pip
🐛 Problèmes API
Regarde les logs FastAPI / Docker (docker logs)
🔍 Test rapide
Visite http://127.0.0.1:8000/ et teste /status


🎯 Finalisation
	•	Venv activé ?
	•	FastAPI accessible ?
	•	LLM Ollama chargé (ollama list) ?
	•	Tests passés (ark-test) ?

⸻

🧠 Arkalia-LUNA est conçue pour être installée en local, sans cloud, sans dépendances extérieures — pour une IA souveraine et maîtrisée.
# 🌌 Arkalia-LUNA PRO

**Système Cognitif IA Local, Modulaire, Auto-Réflexif et Documenté**

> 🧠 Version : `v1.0.9`  
> 📘 Docs : [arkalia-luna-system.github.io/arkalia-luna-pro](https://arkalia-luna-system.github.io/arkalia-luna-pro)  
> 🐳 Docker • 🧪 CI • 🧠 ReflexIA • ⚙️ ZeroIA  
>  
> 🔒 Maintenu par le système cognitif Arkalia-LUNA — [github.com/arkalia-luna-system](https://github.com/arkalia-luna-system)

---

## 📘 Accès rapide

[![📘 Docs](https://img.shields.io/badge/docs-online-blue?style=flat-square&logo=readthedocs)](https://arkalia-luna-system.github.io/arkalia-luna-pro/)
[![version](https://img.shields.io/badge/version-v1.0.9-purple?style=flat-square)](https://github.com/arkalia-luna-system/arkalia-luna-pro/releases)
[![CI](https://github.com/arkalia-luna-system/arkalia-luna-pro/actions/workflows/ci.yml/badge.svg)](https://github.com/arkalia-luna-system/arkalia-luna-pro/actions)
[![Pre-Commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen)](https://pre-commit.com/)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/docker-ready-blue)](https://www.docker.com/)
[![Sitemap](https://img.shields.io/badge/sitemap-valid-brightgreen?style=flat-square&logo=sitemaps)](https://arkalia-luna-system.github.io/arkalia-luna-pro/sitemap.xml)
[![CI + Sitemap](https://img.shields.io/badge/CI%20%2B%20Sitemap-passing-brightgreen?style=flat-square&logo=github)](https://github.com/arkalia-luna-system/arkalia-luna-pro/actions)
[![Tests](https://img.shields.io/badge/tests-100%25-brightgreen?style=flat-square&logo=pytest)](https://github.com/arkalia-luna-system/arkalia-luna-pro/actions)

---

## 🌟 Objectif

Créer un **système IA local, modulaire, interfaçable, auto-réparant**, et entièrement versionné.

Fonctions principales :

- 📦 Modules IA autonomes : `reflexia`, `nyxalia`, `helloria`
- 🛰️ API locale via FastAPI (`/status`, `/trigger`)
- 🔁 Scripts intelligents orchestrés par ReflexIA / ZeroIA
- 🔐 Dockerisé, testé, synchronisé avec GitHub (CI + Docs)
- 🧠 Compatible LLM locaux (`ollama`) : mistral, llama2, tinyllama

---

## 🧱 Architecture technique

arkalia-luna-pro/
├── core/                  # Logique transversale
├── modules/               # Modules IA autonomes
├── config/                # Fichiers TOML / JSON
├── logs/                  # Logs horodatés
├── state/                 # États persistants
├── scripts/               # Scripts de build, ReflexIA, Docker
├── tests/                 # Couverture via pytest
├── docs/                  # Documentation MkDocs
└── .github/workflows/     # Pipelines CI GitHub Actions

### 🛠️ Scripts essentiels

| Script | Fonction |
|--------|----------|
| `ark-test` | Lancer tous les tests + couverture HTML |
| `ark-docker-rebuild.sh` | Rebuild Docker + relance serveur |
| `ark-clean-push` | Formatage (black + ruff) + commit & push |
| `trigger_scan.sh` | Déclenchement manuel ReflexIA |

---

## 🚀 Lancement rapide (Docker)

**Prérequis :**
- Docker Desktop (macOS, Linux)
- Python 3.10+ si mode manuel

**Commandes :**

```bash
docker compose down
find . -name '._*' -delete && find . -name '.DS_Store' -delete
docker compose build --no-cache
docker compose up

📍 Accès local : http://localhost:8000

⸻

💡 Tips & Aliases
	•	./scripts/ark-docker-rebuild.sh → rebuild rapide
	•	ark-test → lance les tests + ouvre couverture (htmlcov/)
	•	Intégration automatique MkDocs via GitHub Actions

⸻

📃 Historique des versions

Version
État
Description
v1.0.9
✅ Stable
Docs + Docker + Design Arkalia Final
v1.0.6
✅ Propre
CI/CD, Docker, couverture 100%, docs pro
v0.3.0
✅ Fonctionnel
Docker + FastAPI OK
v0.2.0
⚙️ Structuré
CI ajoutée, scripts initiaux
v0.1.1
🚀 Devstation
Environnement IA local installé

🧠 En cours de développement
	•	🧩 Modules supplémentaires : Kaelia, Psykalia
	•	📊 IA réflexive : pondération (weights.toml)
	•	📁 Mémoire vectorielle (FAISS)
	•	🚦 Monitoring système : Prometheus, Grafana

⸻

🪪 À propos

Arkalia-LUNA est une base cognitive IA locale conçue pour être :
	•	Propre
	•	Interconnectable
	•	Modulaire
	•	Durable

Chaque composant est autonome mais orchestré de manière réflexive via une boucle IA adaptative.
Un projet signé 🌓 Système Lunaire Arkalia.

## 🧠 AssistantIA

> Module de dialogue intelligent intégré à Arkalia.  
> Environnement : Dockerisé, FastAPI, port 8001

- **Status :** ✅ Actif
- **Port :** `8001`
- **Commande dev locale :** `uvicorn modules.assistantia.core:app --port 8001`
- **Commande Docker :** `docker-compose up assistantia`

### 🔗 Endpoints disponibles

| Méthode | URL                     | Description                |
|---------|-------------------------|----------------------------|
| GET     | /                       | Accueil API AssistantIA    |
| POST    | /chat                   | (À venir) Dialogue IA      |

[![Version](https://img.shields.io/badge/version-v1.2.1--stable--docker-blue)](https://github.com/arkalia-luna-system/arkalia-luna-pro/releases)

Pour plus de détails, consultez la [documentation AssistantIA](docs/assistantia.md).

---

## 🐳 Docker Services Actifs

| Service       | Port | Commande Docker                        |
|---------------|------|----------------------------------------|
| arkalia-api   | 8000 | `docker-compose up arkalia-api`        |
| assistantia   | 8001 | `docker-compose up assistantia`        |

## 🚀 Lancer le projet avec Docker

```bash
# Lancer les deux services
docker-compose up --build

# Ou relancer seulement assistantia
docker-compose up assistantia
```

![Docker](https://img.shields.io/badge/docker-ready-blue)

# 🌙 Arkalia-LUNA Pro

> **Orchestrateur IA Entreprise Gouverné** — Plateforme modulaire orientée fiabilité, observabilité, sécurité et auditabilité pour workflows IA en phase de stabilisation.

[![Release](https://img.shields.io/github/v/tag/arkalia-luna-system/arkalia-luna-pro?label=release)](https://github.com/arkalia-luna-system/arkalia-luna-pro/releases)
[![Status](https://img.shields.io/badge/status-active%20stabilization-yellow.svg)](https://github.com/arkalia-luna-system/arkalia-luna-pro)
[![Docker](https://img.shields.io/badge/containers-5%20active-success.svg)](https://github.com/arkalia-luna-system/arkalia-luna-pro)
[![Tests](https://img.shields.io/badge/test%20files-100-success.svg)](https://github.com/arkalia-luna-system/arkalia-luna-pro)
[![codecov](https://codecov.io/gh/arkalia-luna-system/arkalia-luna-pro/branch/develop/graph/badge.svg)](https://codecov.io/gh/arkalia-luna-system/arkalia-luna-pro)
[![Workflows](https://img.shields.io/badge/CI%2FCD-7%20workflows-blue.svg)](https://github.com/arkalia-luna-system/arkalia-luna-pro/.github/workflows)
[![CodeQL](https://github.com/arkalia-luna-system/arkalia-luna-pro/actions/workflows/codeql.yml/badge.svg)](https://github.com/arkalia-luna-system/arkalia-luna-pro/actions/workflows/codeql.yml)
[![Secret Scan](https://github.com/arkalia-luna-system/arkalia-luna-pro/actions/workflows/secret-scan.yml/badge.svg)](https://github.com/arkalia-luna-system/arkalia-luna-pro/actions/workflows/secret-scan.yml)

---

## 📑 Sommaire

- [🌙 Arkalia-LUNA Pro](#-arkalia-luna-pro)
  - [📑 Sommaire](#-sommaire)
  - [🚀 Démarrage Rapide](#-démarrage-rapide)
    - [🔗 Accès aux Services](#-accès-aux-services)
  - [🧩 Modules Principaux](#-modules-principaux)
- [🎯 Positionnement](#-positionnement)
  - [Différenciation](#différenciation)
  - [📊 Cas d'Usage](#-cas-dusage)
    - [✅ Adapté pour](#-adapté-pour)
    - [⚠️ Limitations](#️-limitations)
  - [🏗️ Architecture](#️-architecture)
    - [Services Principaux](#services-principaux)
  - [💡 Exemples d'Utilisation](#-exemples-dutilisation)
    - [🔒 Détection de Sécurité](#-détection-de-sécurité)
    - [⚡ Optimisation de Performance](#-optimisation-de-performance)
    - [🧠 Apprentissage Automatique](#-apprentissage-automatique)
    - [🎯 Démo Complète](#-démo-complète)
  - [⚙️ Fonctionnalités Principales](#️-fonctionnalités-principales)
    - [🎯 ZeroIA — Système de Décision](#-zeroia--système-de-décision)
    - [💬 AssistantIA — Interface Conversationnelle](#-assistantia--interface-conversationnelle)
    - [👁️ ReflexIA — Surveillance](#️-reflexia--surveillance)
    - [🔍 Sandozia — Analyse](#-sandozia--analyse)
    - [🛡️ Security — Sécurité](#️-security--sécurité)
  - [📈 Monitoring](#-monitoring)
    - [Grafana](#grafana)
    - [Prometheus](#prometheus)
    - [Logs](#logs)
    - [Alertes](#alertes)
  - [🧪 Tests](#-tests)
  - [🔐 Sécurité](#-sécurité)
  - [📚 Documentation](#-documentation)
  - [🤝 Contribuer](#-contribuer)
- [🗺️ Relance Produit (90 jours)](#️-relance-produit-90-jours)

> 💡 **Astuce** : Utilisez `Ctrl+F` (ou `Cmd+F` sur Mac) pour rechercher rapidement une section dans ce README.

---

## 🚀 Démarrage Rapide

```bash
# 1. Cloner le projet
git clone https://github.com/arkalia-luna-system/arkalia-luna-pro.git
cd arkalia-luna-pro

# 2. Démarrer tous les services
docker-compose up -d

# 3. Vérifier que tout fonctionne
curl http://localhost:8000/health
```

### 🔗 Accès aux Services

| Service | URL | Description |
|---------|-----|-------------|
| **API principale** | http://localhost:8000 | API centrale |
| **Documentation API** | http://localhost:8000/docs | Documentation interactive |
| **Grafana** | http://localhost:3000 | Stack monitoring dédiée |
| **Prometheus** | http://localhost:9090 | Stack monitoring dédiée |

> 💡 **Note** : Grafana/Prometheus/Loki/AlertManager sont fournis par la stack monitoring dédiée, pas par `docker-compose.yml` principal.

---

## 🧩 Modules Principaux

| Module | Description |
|--------|-------------|
| **ZeroIA** | Système de décision intelligent |
| **Reflexia** | Surveillance et monitoring |
| **Sandozia** | Analyse et validation croisée |
| **AssistantIA** | Interface conversationnelle avec IA |
| **Memoria** | Mémoire vectorielle locale (souvenirs long terme) |
| **Security** | Protection et audit de sécurité |
| **Monitoring** | Observabilité complète (Prometheus, Grafana) |

---

## 🎯 Positionnement

Arkalia-LUNA Pro se positionne comme une couche d'**orchestration IA gouvernée pour l'entreprise**:

- exécution orchestrée de modules IA avec garde-fous de sécurité
- observabilité native (métriques, logs, alertes) orientée exploitation
- traçabilité et audit des décisions pour les environnements régulés
- architecture modulaire pour intégrer des agents et services hétérogènes

### Différenciation

Comparaison simplifiée avec l'écosystème:

- **LangChain**: framework de développement d'applications LLM (focus DX)
- **CrewAI / AutoGen**: orchestration de conversations multi-agents
- **Arkalia-LUNA Pro**: orchestration **opérationnelle entreprise** (SLO, monitoring, sécurité, audit, intégration infra)

---

## 📊 Cas d'Usage

### ✅ Adapté pour

- Exécution de workflows IA internes avec exigences de conformité
- Supervision centralisée de modules IA en environnement Docker
- Prototypage vers production avec monitoring et sécurité intégrés
- Évaluation de performance et de résilience avant passage en exploitation

### ⚠️ Limitations

- Nécessite Ollama installé localement
- Couverture de tests encore en progression (objectif court terme: 70%+)
- Le projet est en phase de relance produit et d'ouverture communautaire
- Le statut "production-ready" n'est pas revendiqué tant que les critères de fiabilité/sécurité ne sont pas atteints

---

## 🏗️ Architecture

Le système est organisé en modules qui communiquent entre eux :

- **API** : Point d'entrée principal (Helloria, AssistantIA, ReflexIA)
- **Intelligence** : Modules de décision et d'analyse (ZeroIA, Sandozia, Cognitive Reactor)
- **Sécurité** : Protection et audit (Vault, Sandbox, Scanner)
- **Monitoring** : Observabilité (Prometheus, Grafana, Loki)
- **Stockage** : Gestion des données (JSON, SQLite, Memoria)

### Services Principaux

| Service | Port | Description |
|---------|------|-------------|
| **arkalia-api** | 8000 | API centrale |
| **arkalia-assistantia** | 8001 | Interface conversationnelle IA |
| **reflexia** | 8002 | Surveillance et monitoring |
| **arkalia-sandozia** | - | Analyse et validation |
| **cognitive** | 8003 | Intelligence avancée |

> 📖 Pour plus de détails, voir [Architecture complète](docs/architecture/overview.md)

---

## 💡 Exemples d'Utilisation

### 🔒 Détection de Sécurité

Le système détecte automatiquement les tentatives d'intrusion et bloque les menaces.

```bash
python scripts/launch_demo_scenario.py --scenario security
```

### ⚡ Optimisation de Performance

Détection automatique des problèmes de performance et optimisation.

```bash
python scripts/launch_demo_scenario.py --scenario performance
```

### 🧠 Apprentissage Automatique

Le système apprend des patterns et améliore ses décisions.

```bash
python scripts/launch_demo_scenario.py --scenario learning
```

### 🎯 Démo Complète

Tester tous les scénarios en une fois :

```bash
python scripts/launch_demo_scenario.py --all
```

---

## ⚙️ Fonctionnalités Principales

### 🎯 ZeroIA — Système de Décision

- Prise de décision intelligente
- Calcul de confiance
- Récupération automatique d'erreurs
- Surveillance en temps réel

### 💬 AssistantIA — Interface Conversationnelle

- Dialogue avec l'IA via API
- Intégration Ollama (modèles locaux)
- Contexte adaptatif
- Intégration avec **Memoria** pour une mémoire à long terme vectorielle locale (souvenirs de chat, idées de projets, décisions)

### 🧠 Memoria — Mémoire Long Terme

- Stockage local dans `state/memoria.db` (SQLite)
- Index vectoriel léger (embeddings via Ollama si disponible, sinon fallback déterministe)
- Rappel sémantique de souvenirs pertinents dans le prompt d'AssistantIA
- Activation via variable d'environnement `MEMORIA_ENABLED=true`

### 👁️ ReflexIA — Surveillance

- Monitoring des autres modules
- Détection de problèmes
- Analyse comportementale

### 🔍 Sandozia — Analyse

- Validation croisée entre modules
- Détection de patterns
- Intelligence collaborative

### 🛡️ Security — Sécurité

- Gestion des secrets
- Audit automatique
- Protection contre les attaques

---

## 📈 Monitoring

### Grafana

- **URL** : http://localhost:3000
- **Tableaux de bord** : État système, performance, sécurité
- **Identifiants** : `admin` / `arkalia-secure-2025`

### Prometheus

- **URL** : http://localhost:9090
- **Métriques** : Collecte en temps réel de toutes les métriques système

### Logs

- **Loki** : http://localhost:3100
- **Recherche** : Tous les logs centralisés et consultables

### Alertes

- **AlertManager** : http://localhost:9093
- **Alertes automatiques** configurées

---

## 🧪 Tests

```bash
# Lancer tous les tests
make test

# Tests unitaires
make test-unit

# Tests d'intégration
make test-integration
```

**Statut** : 🔄 Stabilisation active (couverture en progression)

---

## 🔐 Sécurité

- Authentification par token
- Limitation de débit (rate limiting)
- Secrets chiffrés
- Audit automatique
- Scan de sécurité automatisé
- Politique de sécurité publique: `SECURITY.md`
- Scan SAST: CodeQL
- Scan secrets: Gitleaks
- Mises à jour dépendances: Dependabot

---

## 📚 Documentation

- **Documentation complète** : [docs/](docs/)
- **API interactive** : http://localhost:8000/docs
- **Guide de démarrage** : [Quick Start](docs/getting-started/quick-start.md)

---

## 🤝 Contribuer

- **Signaler un bug** : [GitHub Issues](https://github.com/arkalia-luna-system/arkalia-luna-pro/issues)
- **Proposer une fonctionnalité** : Fork → Pull Request
- **Améliorer la documentation** : Toute contribution est bienvenue

> **Standards** : Tests obligatoires, formatage avec Black/Ruff, documentation à jour

---

## 🗺️ Relance Produit (90 jours)

### J0-J15: clarifier la proposition de valeur

- Cibler 1-2 cas d'usage entreprise prioritaires
- Formaliser les critères de succès (coût, latence, fiabilité, auditabilité)
- Publier une feuille de route orientée impact utilisateur

### J15-J45: renforcer la crédibilité technique

- Monter la couverture de tests sur les modules critiques
- Publier des benchmarks reproductibles (latence, coût, fiabilité)
- Stabiliser les scénarios E2E les plus utilisés

### J45-J90: relancer la traction

- Ouvrir les sujets "good first issue"
- Exécuter des POC avec utilisateurs pilotes
- Publier des notes techniques de retour d'expérience

---

<div align="center">

**Arkalia-LUNA Pro v2.8.0**

*Orchestrateur IA entreprise modulaire, observable et gouverné*

</div>

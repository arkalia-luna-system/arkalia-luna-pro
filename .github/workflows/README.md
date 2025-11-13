# 🚀 Workflows GitHub Actions - Arkalia-LUNA Pro

## 📋 **Workflows Essentiels (5 workflows ultra-pro)**

### 1. **`ci.yml`** - CI/CD Principale
- **But** : Pipeline CI/CD complète (lint, tests unitaires, intégration, sécurité, coverage)
- **Déclencheurs** : `push`, `pull_request` sur toutes les branches principales
- **Jobs** : Lint, tests unitaires, intégration, sécurité, artefacts, codecov
- **Statut** : **Workflow principal pour CI/CD**

### 2. **`deploy.yml`** - Déploiement Complet
- **But** : Déploiement complet (validation, build Docker, E2E post-build)
- **Déclencheurs** : `push`, `pull_request` sur branches principales
- **Jobs** : Validation pré-déploiement, build images Docker, tests E2E
- **Statut** : **Workflow principal pour déploiement**

### 3. **`security-scan.yml`** - Scan de Sécurité
- **But** : Scan de sécurité avancé (Bandit, Safety, pip-audit, npm audit)
- **Déclencheurs** : `push`, `pull_request`, `schedule` (cron quotidien)
- **Jobs** : Security scan, dependency update check, artefacts
- **Statut** : **Workflow spécialisé pour sécurité**

### 4. **`performance-tests.yml`** - Tests de Performance
- **But** : Tests de performance (ZeroIA, API, intégration)
- **Déclencheurs** : `push`, `pull_request`, `schedule` (cron quotidien)
- **Jobs** : Benchmarks, artefacts, rapport de performance
- **Statut** : **Workflow spécialisé pour performance**

### 5. **`docs.yml`** - Documentation
- **But** : Build, validation, et déploiement de la documentation
- **Déclencheurs** : `push`, `pull_request` sur branches principales
- **Jobs** : Validation, build, artefacts, déploiement GitHub Pages
- **Statut** : **Workflow spécialisé pour documentation**

---

## 🧹 **Optimisation Récente (novembre 2025)**

### **Suppression des Doublons**
- ❌ **`arkalia-ci-cd.yml`** supprimé (doublon avec `ci.yml` et `deploy.yml`)
- ✅ **Structure simplifiée** : 5 workflows essentiels au lieu de 6
- ✅ **Élimination de la redondance** dans les tests et scans

### **Architecture Optimisée**
- **`ci.yml`** : CI/CD principale (tests, lint, sécurité basique)
- **`deploy.yml`** : Déploiement (build Docker, E2E)
- **`security-scan.yml`** : Sécurité avancée (spécialisé)
- **`performance-tests.yml`** : Performance (spécialisé)
- **`docs.yml`** : Documentation (spécialisé)

### **🎯 Interface GitHub Actions Optimisée**
- **Workflows visibles** : 3 workflows essentiels (ci.yml, deploy.yml, docs.yml)
- **Workflows masqués** : 2 workflows spécialisés (performance-tests.yml, security-scan.yml)
- **Exécution manuelle** : Les workflows masqués sont disponibles via "Run workflow"
- **Interface plus propre** : Moins de bruit visuel dans l'onglet Actions

---

## 🎯 **Philosophie Ultra-Pro**

### **Conventions**
- **Nommage** : Emojis descriptifs + nom clair
- **Déclencheurs** : Cohérents entre workflows
- **Timeouts** : Définis pour éviter les jobs bloqués
- **Permissions** : Minimales et sécurisées
- **Artefacts** : Upload systématique avec rétention

### **Bonnes Pratiques**
- **Docker** : Utilisation de `docker compose` (nouvelle syntaxe)
- **Python** : Version 3.10, cache pip activé
- **Tests** : Couverture, timeouts, artefacts
- **Sécurité** : Bandit, permissions minimales
- **Documentation** : Build strict, validation

### **Environnements**
- **Branches principales** : `main`, `develop`
- **Runners** : `ubuntu-latest`
- **Timeouts** : 10-45 minutes selon la complexité
- **Artefacts** : Rétention 7-30 jours

---

## 🔧 **Configuration Technique**

### **Variables d'Environnement**
```yaml
PYTHON_VERSION: "3.10"
COVERAGE_MIN: 28
DOCKER_BUILDKIT: 1
COMPOSE_DOCKER_CLI_BUILD: 1
```

### **Permissions**
```yaml
permissions:
  contents: read
  packages: write  # Pour Docker Registry
  pages: write     # Pour GitHub Pages
  actions: read
```

### **Cache**
- **Pip** : Cache des dépendances Python
- **Docker** : Cache des layers BuildKit
- **Ruff** : Cache du linting

---

## 📊 **Métriques de Qualité**

### **Seuils**
- **Couverture tests** : ≥ 28% (seuil CI)
- **Lint** : 0 erreur, 0 warning
- **Sécurité** : 0 vulnérabilité critique
- **Performance** : < 500ms API, < 2s ZeroIA

### **Artefacts Générés**
- `test-results.xml` : Résultats tests JUnit
- `coverage.xml` : Couverture Codecov
- `htmlcov/` : Rapport couverture HTML
- `bandit-report.json` : Rapport sécurité
- `e2e-report.md` : Rapport E2E
- `performance-report.md` : Rapport performance

---

## 🚨 **Dépannage**

### **Erreurs Communes**
1. **Docker compose** : Utiliser `docker compose` (pas `docker-compose`)
2. **Permissions** : Vérifier les permissions dans le workflow
3. **Timeouts** : Augmenter si nécessaire selon la complexité
4. **Cache** : Nettoyer si corruption détectée

### **Logs Utiles**
- **Build** : Logs de construction Docker
- **Tests** : Résultats pytest avec coverage
- **E2E** : Logs des services et healthchecks
- **Performance** : Métriques et benchmarks

---

## ✅ **Validation Ultra-Pro**

### **Checklist Pré-Push**
- [ ] Tests unitaires passent localement
- [ ] Tests d'intégration passent localement
- [ ] Lint (black, ruff) sans erreur
- [ ] Documentation build sans erreur
- [ ] Docker compose config valide

### **Checklist Post-Push**
- [ ] CI principale (ci.yml) : ✅
- [ ] Tests E2E (e2e.yml) : ✅
- [ ] Performance (performance-tests.yml) : ✅
- [ ] Documentation (docs.yml) : ✅
- [ ] Déploiement (deploy.yml) : ✅

---

**Dernière mise à jour** : 27 novembre 2025
**Version** : Ultra-Pro v2.0
**Mainteneur** : Arkalia-LUNA Team

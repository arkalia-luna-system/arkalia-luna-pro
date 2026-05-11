# 🚀 Workflows GitHub Actions - Arkalia-LUNA Pro

## 📋 Workflows actifs (visibles dans Actions)

- `ci.yml` -> **CI · Build & Test**
- `deploy.yml` -> **Deploy · App**
- `docs.yml` -> **Deploy · Docs**
- `security-scan.yml` -> **Security · Dependency & Code Scan**
- `secret-scan.yml` -> **Security · Secret Scan**
- `codeql.yml` -> **Security · CodeQL**

## 🗄️ Workflows archivés (masqués de la vue Actions)

Ces workflows ne sont plus chargés par GitHub Actions car déplacés hors `.github/workflows/` :

- `.github/workflows_disabled/e2e.yml`
- `.github/workflows_disabled/performance-tests.yml`
- `.github/workflows_disabled/force-cleanup.yml`

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

### 🎯 Interface GitHub Actions optimisée
- Workflows actifs réduits et renommés de façon homogène.
- Workflows utilitaires/marche arrière archivés hors dossier actif.
- Interface Actions plus lisible (moins de bruit).

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

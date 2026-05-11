# 🔧 Scripts de Diagnostic et Maintenance

## Arkalia-LUNA Pro - Documentation des Scripts Utilitaires

**Date :** 2025-11-12  
**Version :** 2.8.0

---

## 📋 RÉSUMÉ

Ce document liste tous les scripts de diagnostic, validation et maintenance disponibles dans le projet Arkalia-LUNA Pro. Ces scripts facilitent le développement, le débogage et la maintenance du système.

---

## 🎯 SCRIPTS DE DIAGNOSTIC

### 1. `ark-master-diagnostic.py`

**Description :** Diagnostic complet du système Arkalia-LUNA Pro

**Usage :**
```bash
python scripts/ark-master-diagnostic.py
python scripts/ark-master-diagnostic.py --verbose
python scripts/ark-master-diagnostic.py --module zeroia
```

**Fonctionnalités :**
- Vérification de l'état de tous les modules
- Diagnostic des dépendances
- Vérification des configurations
- Test de connectivité entre modules
- Rapport détaillé des problèmes détectés

**Exemple de sortie :**
```
🔍 Diagnostic Arkalia-LUNA Pro
✅ Module zeroia: OK
✅ Module reflexia: OK
⚠️ Module sandozia: Configuration manquante
❌ Module assistantia: Erreur de connexion
```

---

### 2. `ark-master-orchestrator.py`

**Description :** Orchestrateur principal pour gérer tous les modules

**Usage :**
```bash
python scripts/ark-master-orchestrator.py --start
python scripts/ark-master-orchestrator.py --stop
python scripts/ark-master-orchestrator.py --status
python scripts/ark-master-orchestrator.py --restart
```

**Fonctionnalités :**
- Démarrage/arrêt de tous les modules
- Gestion du cycle de vie des modules
- Monitoring en temps réel
- Gestion des erreurs et récupération automatique

---

### 3. `ark-modules-analysis.py`

**Description :** Analyse approfondie de tous les modules

**Usage :**
```bash
python scripts/legacy/ark-modules-analysis.py
python scripts/legacy/ark-modules-analysis.py --module zeroia --detailed
python scripts/legacy/ark-modules-analysis.py --export report.json
```

**Fonctionnalités :**
- Analyse des dépendances entre modules
- Détection des doublons de code
- Analyse de la complexité cyclomatique
- Rapport de couverture de code
- Suggestions d'optimisation

---

## ✅ SCRIPTS DE VALIDATION

### 4. `ark-validate-performance.py`

**Description :** Validation des performances du système

**Usage :**
```bash
python scripts/ark-validate-performance.py
python scripts/ark-validate-performance.py --module zeroia
python scripts/ark-validate-performance.py --benchmark
```

**Fonctionnalités :**
- Tests de performance des modules
- Mesure du temps de réponse
- Analyse de l'utilisation mémoire
- Détection des goulots d'étranglement
- Comparaison avec les benchmarks

**Exemple de sortie :**
```
⚡ Validation Performance
Module zeroia: 45ms (✅ OK)
Module reflexia: 120ms (⚠️ LENT)
Module sandozia: 89ms (✅ OK)
```

---

### 5. `ark-validate-coverage.py`

**Description :** Validation de la couverture de code

**Usage :**
```bash
python scripts/ark-validate-coverage.py
python scripts/ark-validate-coverage.py --module zeroia
python scripts/ark-validate-coverage.py --threshold 80
```

**Fonctionnalités :**
- Calcul de la couverture de code par module
- Identification des zones non testées
- Rapport détaillé avec seuils personnalisables
- Export en différents formats (HTML, JSON, XML)

---

### 6. `ark-validate-monitoring.py`

**Description :** Validation du système de monitoring

**Usage :**
```bash
python scripts/ark-validate-monitoring.py
python scripts/ark-validate-monitoring.py --check-prometheus
python scripts/ark-validate-monitoring.py --check-grafana
```

**Fonctionnalités :**
- Vérification de la collecte de métriques
- Test des endpoints Prometheus
- Validation des dashboards Grafana
- Vérification des alertes

---

## 🧹 SCRIPTS DE NETTOYAGE

### 7. `cleanup_cache.py`

**Description :** Nettoyage des caches et fichiers temporaires

**Usage :**
```bash
python scripts/cleanup_cache.py
python scripts/cleanup_cache.py --root /path/to/project
python scripts/cleanup_cache.py --log-threshold 7 --state-limit 100
```

**Fonctionnalités :**
- Suppression des `__pycache__`
- Nettoyage des logs anciens (>7 jours par défaut)
- Gestion de la taille du dossier `state/` (limite 100MB par défaut)
- Libération de RAM et espace disque

**Options :**
- `--root`: Chemin racine du projet (détecté automatiquement si non fourni)
- `--log-threshold`: Nombre de jours pour conserver les logs (défaut: 7)
- `--state-limit`: Limite de taille pour `state/` en MB (défaut: 100)

---

### 8. `cleanup_confidence_memory.py`

**Description :** Nettoyage du fichier `confidence_memory.toml` (peut atteindre 570MB)

**Usage :**
```bash
python scripts/cleanup_confidence_memory.py
python scripts/cleanup_confidence_memory.py --days 30 --max-entries 1000
python scripts/cleanup_confidence_memory.py --file state/confidence_memory.toml --no-backup
```

**Fonctionnalités :**
- Réduction de la taille de `confidence_memory.toml`
- Conservation des entrées récentes (30 jours par défaut)
- Limitation du nombre d'entrées (1000 par défaut)
- Création automatique de backup avant nettoyage

**Options :**
- `--file`: Chemin vers `confidence_memory.toml` (défaut: `state/confidence_memory.toml`)
- `--days`: Nombre de jours à garder (défaut: 30)
- `--max-entries`: Nombre maximum d'entrées à garder (défaut: 1000)
- `--no-backup`: Ne pas créer de backup avant nettoyage

**Exemple :**
```bash
# Nettoyer en gardant 7 jours et max 500 entrées
python scripts/cleanup_confidence_memory.py --days 7 --max-entries 500
```

---

### 9. `ark-clean-state.sh`

**Description :** Nettoyage des fichiers d'état

**Usage :**
```bash
bash scripts/ark-clean-state.sh
```

**Fonctionnalités :**
- Suppression des fichiers d'état temporaires
- Nettoyage des snapshots anciens
- Conservation des backups importants

---

### 10. `ark-clean-json.sh`

**Description :** Nettoyage des fichiers JSON temporaires

**Usage :**
```bash
bash scripts/ark-clean-json.sh
```

**Fonctionnalités :**
- Suppression des fichiers JSON corrompus
- Nettoyage des fichiers JSON temporaires
- Validation de l'intégrité des JSON restants

---

### 11. `ark-clean-hidden.sh`

**Description :** Nettoyage des fichiers cachés macOS

**Usage :**
```bash
bash scripts/ark-clean-hidden.sh
```

**Fonctionnalités :**
- Suppression des fichiers `._*` (macOS)
- Suppression des fichiers `.DS_Store`
- Nettoyage avant commit/push

---

## 🔍 SCRIPTS D'ANALYSE

### 12. `ark-performance-benchmark.py`

**Description :** Benchmarks de performance détaillés

**Usage :**
```bash
python scripts/ark-performance-benchmark.py
python scripts/ark-performance-benchmark.py --iterations 100
python scripts/ark-performance-benchmark.py --module zeroia --export results.json
```

**Fonctionnalités :**
- Benchmarks répétés pour statistiques fiables
- Comparaison avant/après optimisations
- Export des résultats en JSON
- Génération de rapports détaillés

---

### 13. `ark-pyright-fix.py`

**Description :** Correction automatique des erreurs Pyright

**Usage :**
```bash
python scripts/dev/ark-pyright-fix.py
python scripts/dev/ark-pyright-fix.py --file modules/zeroia/core.py
```

**Fonctionnalités :**
- Détection des erreurs de type
- Correction automatique quand possible
- Suggestions de corrections manuelles
- Rapport des erreurs restantes

---

## 📊 SCRIPTS DE RAPPORT

### 14. `ark-lint-report.sh`

**Description :** Génération de rapport de linting

**Usage :**
```bash
bash scripts/dev/ark-lint-report.sh
bash scripts/dev/ark-lint-report.sh --output lint-report.html
```

**Fonctionnalités :**
- Analyse complète avec ruff, black, mypy
- Génération de rapport HTML
- Statistiques par module
- Suggestions de corrections

---

## 🚀 SCRIPTS DE DÉMARRAGE

### 15. `ark-zeroia-run`

**Description :** Démarrage rapide de ZeroIA

**Usage :**
```bash
./scripts/ark-zeroia-run
```

**Fonctionnalités :**
- Démarrage simplifié de ZeroIA
- Vérification des prérequis
- Configuration automatique

---

## 📝 NOTES IMPORTANTES

### Ordre d'exécution recommandé

1. **Avant développement :**
   ```bash
   python scripts/ark-master-diagnostic.py
   python scripts/ark-validate-coverage.py
   ```

2. **Avant commit :**
   ```bash
   bash scripts/ark-clean-hidden.sh
   bash scripts/dev/ark-fix-linting.sh
   bash scripts/dev/ark-fix-style.sh
   ```

3. **Maintenance régulière :**
   ```bash
   python scripts/cleanup_cache.py
   python scripts/cleanup_confidence_memory.py --days 30
   ```

4. **Après optimisations :**
   ```bash
   python scripts/ark-performance-benchmark.py
   python scripts/ark-validate-performance.py
   ```

### Scripts à exécuter quotidiennement

- `cleanup_cache.py` : Libère RAM et espace disque
- `ark-clean-hidden.sh` : Nettoie fichiers macOS

### Scripts à exécuter hebdomadairement

- `cleanup_confidence_memory.py` : Réduit taille fichiers état
- `ark-validate-coverage.py` : Vérifie couverture tests

### Scripts à exécuter mensuellement

- `ark-modules-analysis.py` : Analyse complète modules
- `ark-performance-benchmark.py` : Benchmarks complets

---

## 🔗 LIENS UTILES

- [Index des rapports](../reports/README.md)
- [Documentation principale](../README.md)

---

**Dernière mise à jour :** 2025-11-12


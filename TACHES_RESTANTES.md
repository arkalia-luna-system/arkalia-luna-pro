# 📋 TÂCHES RESTANTES - Arkalia-LUNA Pro

**Date :** 2025-11-12  
**Dernière mise à jour :** 2025-11-12 (Phase 3 terminée ✅)

---

## ✅ PHASES TERMINÉES

### 🎯 Phase 1 : Corrections Critiques (100% ✅)
- ✅ Supprimé `helloria/core.py` (doublon)
- ✅ Supprimé `modules/utils_enhanced/` (obsolète)
- ✅ Consolidé `configs/` → `config/pytest/` et `config/docker/`
- ✅ Migré 12 imports de `helloria.core` vers `modules.helloria.core`

### 🎯 Phase 2 : Standardisation I/O (100% ✅)
- ✅ Fusionné `save_json_if_changed()` et `save_toml_if_changed()` dans `io_safe.py`
- ✅ Migré 5 fichiers vers `modules/utils/helpers/io_safe.py`
- ✅ Supprimé implémentations redondantes
- ✅ Ajouté cache thread-safe pour `load_toml_cached()`

### 🎯 Phase 3 : Unification Logging (100% ✅)
- ✅ **70 fichiers migrés** vers `ark_logger`
- ✅ Tous les modules complétés
- ✅ LoggerService unifié avec ark_logger

---

## ❌ TÂCHES RESTANTES

### 🔴 PRIORITÉ HAUTE

#### 1. **Phase 4 : Optimisations Architecturales** ⏱️ 4-6h

**1.1. Fusionner `HelloriaStateManager` avec `StorageManager`**
- **Fichiers concernés :**
  - `modules/helloria/state.py` (HelloriaStateManager)
  - `modules/core/storage.py` (StorageManager)
- **Actions :**
  - Analyser les fonctionnalités de `HelloriaStateManager`
  - Intégrer dans `StorageManager` comme backend spécialisé
  - Migrer tous les usages de `HelloriaStateManager` vers `StorageManager`
  - Supprimer `HelloriaStateManager` après migration
  - Mettre à jour les tests

**1.2. Migrer `CrossModuleValidator` de Sandozia vers utils/validators**
- **Fichiers concernés :**
  - `modules/sandozia/validators/crossmodule.py` (766 lignes)
  - `modules/utils/validators/crossmodule_validator.py` (existe déjà)
- **Actions :**
  - Analyser les différences entre les deux implémentations
  - Fusionner les fonctionnalités dans `modules/utils/validators/crossmodule_validator.py`
  - Migrer tous les imports de Sandozia vers utils/validators
  - Supprimer `modules/sandozia/validators/crossmodule.py`
  - Mettre à jour les tests

---

### 🟠 PRIORITÉ MOYENNE

#### 2. **Screenshots dashboard** ⏱️ 2h (intervention manuelle)
- ⏳ Grafana
- ⏳ Prometheus
- ⏳ Docker
- ⏳ AlertManager

**Action requise :** Démarrer les services et capturer les screenshots

---

### 🟡 PRIORITÉ BASSE

#### 3. **Amélioration couverture tests** ⏱️ 8-10h
- **Objectif :** 65% de couverture (actuellement 59.25%)
- **Modules ciblés :**
  - `monitoring/prometheus_metrics.py` : 20% → 40%
  - `sandozia/reasoning/collaborative.py` : 28% → 50%
  - `sandozia/core/chronalia.py` : 30% → 50%

#### 4. **Documentation à mettre à jour**
- ⏳ `TODO_RESTANT.md` (à mettre à jour avec nouvelles tâches)
- ⏳ `plan-ameliorations-futures.md` (à mettre à jour avec état actuel)

---

## 📊 STATISTIQUES ACTUELLES

- **Fichiers Python** : 284 analysés
- **Fichiers migrés vers ark_logger** : 70/70 (100%) ✅
- **Modules redondants supprimés** : 3
- **Fonctions dupliquées supprimées** : 3
- **Tests** : 671 tests passent (59.25% couverture)
- **Qualité code** : ✅ Mypy OK, Ruff OK, Black OK
- **CI/CD** : ✅ 100% verte

---

## 🎯 PLAN D'ACTION RECOMMANDÉ

### Semaine 1
1. **Phase 4.1** : Fusionner HelloriaStateManager (2-3h)
2. **Phase 4.2** : Migrer CrossModuleValidator (2-3h)

### Semaine 2
3. **Screenshots dashboard** (2h - intervention manuelle)
4. **Amélioration couverture tests** (début - 4h)

### Semaine 3-4
5. **Finir amélioration couverture tests** (4-6h)
6. **Mettre à jour documentation** (1h)

---

**Dernière mise à jour :** 2025-11-12  
**Prochaine révision :** Après Phase 4


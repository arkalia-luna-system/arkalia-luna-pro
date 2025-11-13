# 📊 Analyse des Scripts Obsolètes ou Inutiles

## Arkalia-LUNA Pro - Rapport d'audit complet

**Date d'analyse** : novembre 2025
**Méthodologie** : Vérification double des références dans le codebase, documentation, Makefile, et workflows CI/CD

---

## 🔴 Scripts OBSOLÈTES à SUPPRIMER

### 1. Scripts de conteneurs Docker non utilisés

- **`scripts/ark-containers-fixed.sh`** ❌
  - **Raison** : Aucune référence trouvée dans le codebase
  - **Alternative** : Utiliser `ark-docker-start.sh`, `ark-docker-stop.sh`

- **`scripts/ark-containers-perfect.sh`** ❌
  - **Raison** : Aucune référence trouvée, semble être une version expérimentale
  - **Alternative** : Scripts Docker standardisés

- **`scripts/ark-containers-simple.sh`** ❌
  - **Raison** : Aucune référence trouvée
  - **Alternative** : Scripts Docker standardisés

### 2. Scripts Docker redondants

- **`scripts/docker-start-robust.sh`** ❌
  - **Raison** : Aucune référence trouvée
  - **Alternative** : `scripts/ark-docker-start.sh`

- **`scripts/docker-start-ultra-robust.sh`** ❌
  - **Raison** : Aucune référence trouvée
  - **Alternative** : `scripts/ark-docker-start.sh`

### 3. Scripts de validation redondants

- **`scripts/validate_workflows.sh`** ⚠️
  - **Raison** : Trois scripts similaires existent (`validate_workflows.sh`, `validate-all-workflows.sh`, `validate-workflows.sh`)
  - **Recommandation** : Conserver uniquement `validate-workflows.sh` (le plus complet avec 368 lignes)
  - **À supprimer** : `validate_workflows.sh` et `validate-all-workflows.sh`

### 4. Scripts de correction de linting redondants

- **`scripts/fix_final_linting.py`** ⚠️
  - **Raison** : Plusieurs scripts similaires (`fix_linting_issues.py`, `fix_imports_and_types.py`, etc.)
  - **Recommandation** : Conserver uniquement `scripts/ark-fix-linting.sh` qui est référencé dans les alias shell
  - **Note** : Ces scripts Python peuvent être utiles pour des corrections ponctuelles, mais ils sont redondants

- **`scripts/fix_linting_issues.py`** ⚠️
  - **Raison** : Redondant avec `ark-fix-linting.sh`

- **`scripts/fix_imports_and_types.py`** ⚠️
  - **Raison** : Redondant avec les autres scripts de fix

- **`scripts/fix_mypy_annotations.py`** ⚠️
  - **Raison** : Redondant, mypy n'est pas utilisé activement

- **`scripts/fix_type_annotations.py`** ⚠️
  - **Raison** : Redondant avec `fix_imports_and_types.py`

- **`scripts/fix_typing_errors.py`** ⚠️
  - **Raison** : Redondant

- **`scripts/fix_remaining_prints.py`** ⚠️
  - **Raison** : Correction ponctuelle, probablement obsolète

### 5. Scripts de rollback dupliqués

- **`scripts/zeroia_rollback.py`** ⚠️
  - **Raison** : Version alternative de `_zeroia_rollback.py`
  - **Recommandation** : Conserver uniquement `_zeroia_rollback.py` qui est testée et utilisée
  - **Note** : `_zeroia_rollback.py` a des tests unitaires dédiés

### 6. Script de push redondant

- **`scripts/ark-push-final.sh`** ⚠️
  - **Raison** : Simple wrapper qui pourrait être un alias shell
  - **Recommandation** : Intégrer dans `ark-setup-shell.sh` comme alias ou supprimer si non utilisé

### 7. Script de sitemap avec nom incorrect

- **`scripts/sitemap_gen.py`** ⚠️
  - **Raison** : Le fichier s'appelle `sitemap_gen.py` mais `hooks.py` et `build_docs.sh` cherchent `sitemap_generator.py`
  - **Problème** : Incohérence de nommage qui empêche l'exécution automatique
  - **Recommandation** : **RENOMMER** `sitemap_gen.py` → `sitemap_generator.py` pour corriger les références
  - **Impact** : Le sitemap ne peut pas être généré automatiquement actuellement

---

## 🟡 Scripts à VÉRIFIER (potentiellement obsolètes)

### Scripts de déploiement

- **`scripts/phase4-deploy.sh`** ⚠️
  - **Raison** : Aucune référence trouvée, semble être une version de déploiement spécifique
  - **Action** : Vérifier si c'est encore utilisé pour un déploiement spécifique

- **`scripts/switch-to-optimized-workflow.sh`** ⚠️
  - **Raison** : Script de migration ponctuel, peut être obsolète après migration
  - **Action** : Vérifier si la migration est terminée

### Scripts de diagnostic

- **`scripts/analyze_structure.py`** ⚠️
  - **Raison** : Utilisé uniquement dans des rapports, peut être utile pour maintenance
  - **Action** : Conserver si utilisé pour diagnostics périodiques

### Scripts de monitoring

- **`scripts/ark-monitor.py`** ✅
  - **Raison** : Référencé dans la documentation
  - **Action** : Conserver

---

## 🟢 Scripts UTILES à CONSERVER

### Scripts actifs référencés

- ✅ `scripts/ark-docker-*.sh` (start, stop, status, rebuild, dev)
- ✅ `scripts/ark-fix-*.sh` (linting, style, modules)
- ✅ `scripts/ark-validate-*.py` (monitoring, performance, coverage, site)
- ✅ `scripts/ark-setup-*.sh` (shell, vscode)
- ✅ `scripts/ark-vscode-*.sh` (reload, diagnostic)
- ✅ `scripts/ark-sec-check.sh`
- ✅ `scripts/ark-module-diagnostic.sh`
- ✅ `scripts/ark-motivation.sh` (utilisé dans setup)
- ✅ `scripts/ark-install-extensions.sh`
- ✅ `scripts/_zeroia_rollback.py` (testé et utilisé)
- ✅ `scripts/_generate_*.py` (utilisés dans les tests)
- ✅ `scripts/_reflexia_monitor.py` (testé)
- ✅ `scripts/_zeroia_health.py` (testé)
- ✅ `scripts/ark-performance-benchmark.py`
- ✅ `scripts/ark-master-orchestrator.py` (utilisé dans Dockerfile.master)
- ✅ `scripts/ark-master-diagnostic.py`
- ✅ `scripts/log_scrubber.py` (documenté dans security/log_redaction.md)
- ✅ `scripts/healthcheck_zeroia.py` (testé)
- ✅ `scripts/pre_push_zeroia_check.py` (testé)
- ✅ `scripts/arkalia-health-check.py`
- ✅ `scripts/arkalia_enhanced_integration.py` (documenté)
- ✅ `scripts/launch_demo_scenario.py` (documenté)
- ✅ `scripts/build_docs.sh` (utilisé)
- ✅ `scripts/bench_cognitif.py` (référencé dans rapports)
- ✅ `scripts/ci_validation.py`
- ✅ `scripts/check_versions.py`
- ✅ `scripts/check_docs.py`
- ✅ `scripts/update_docs_stats.py`
- ✅ `scripts/generate_dashboard.py`
- ✅ `scripts/json_diagnostic.py`
- ✅ `scripts/restore_broken_files.py`
- ✅ `scripts/diagnose-docker-issues.sh` (référencé dans switch-to-optimized-workflow.sh)
- ✅ `scripts/optimize_containers.sh`
- ✅ `scripts/auto-heal.sh`
- ✅ `scripts/backup_state.sh`
- ✅ `scripts/health_check.sh`
- ✅ `scripts/firewall_setup.sh`
- ✅ `scripts/start-monitoring.sh`
- ✅ `scripts/start_generative_ai.sh`
- ✅ `scripts/validate-dockerfiles.sh`
- ✅ `scripts/validate-workflows.sh` (le plus complet)
- ✅ Scripts dans `scripts/run/` (APIs)
- ✅ Scripts dans `scripts/shell/` (utilitaires shell)
- ✅ Scripts dans `scripts/demo/` (démonstrations)
- ✅ Scripts dans `scripts/tools/` (outils)

---

## 📋 Résumé des Actions Recommandées

### 🔴 Suppression immédiate (7 scripts)

1. `scripts/ark-containers-fixed.sh`
2. `scripts/ark-containers-perfect.sh`
3. `scripts/ark-containers-simple.sh`
4. `scripts/docker-start-robust.sh`
5. `scripts/docker-start-ultra-robust.sh`
6. `scripts/validate_workflows.sh` (garder `validate-workflows.sh`)
7. `scripts/validate-all-workflows.sh` (garder `validate-workflows.sh`)

### ⚠️ À examiner avant suppression (8 scripts)

1. `scripts/zeroia_rollback.py` (garder `_zeroia_rollback.py`)
2. `scripts/ark-push-final.sh` (intégrer comme alias ou supprimer)
3. `scripts/fix_final_linting.py` (garder uniquement si utilisé ponctuellement)
4. `scripts/fix_linting_issues.py` (redondant avec shell script)
5. `scripts/fix_imports_and_types.py` (redondant)
6. `scripts/fix_mypy_annotations.py` (redondant, mypy non utilisé)
7. `scripts/fix_type_annotations.py` (redondant)
8. `scripts/fix_typing_errors.py` (redondant)
9. `scripts/fix_remaining_prints.py` (correction ponctuelle)

### 🔧 À corriger (1 script)

1. `scripts/sitemap_gen.py` → Renommer en `sitemap_generator.py` OU corriger les références dans `hooks.py` et `build_docs.sh`

### ⚠️ À vérifier manuellement (2 scripts)

1. `scripts/phase4-deploy.sh` (déploiement spécifique ?)
2. `scripts/switch-to-optimized-workflow.sh` (migration terminée ?)

---

## 📊 Statistiques

- **Total scripts analysés** : ~122 scripts
- **Scripts obsolètes identifiés** : 7 à supprimer immédiatement
- **Scripts redondants** : 8 à examiner
- **Scripts à corriger** : 1
- **Scripts à vérifier** : 2
- **Scripts utiles conservés** : ~104

---

---

## 📊 Résumé

- **Scripts obsolètes identifiés** : 7 à supprimer
- **Scripts redondants** : 8 à examiner
- **Scripts à corriger** : 1 (sitemap_gen.py → sitemap_generator.py)
- **Scripts utiles conservés** : ~104

**Note** : Les scripts marqués comme "à examiner" nécessitent une vérification manuelle.

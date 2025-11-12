# 📋 TODO Restant - Corrections Luna Pro

**Date** : novembre 2025  
**Basé sur** : Audit V2 (AUDIT_VERIFICATION_PLAN_ACTION_V2.md)

---

## ✅ CE QUI A ÉTÉ FAIT

### 🔴 CRITIQUE - TERMINÉ
- ✅ **Badge containers corrigé** : `7 containers` → `5 active` (README ligne 9)
- ✅ **Titre corrigé** : `Enterprise` → `Production-Ready` (README ligne 1)
- ✅ **Mentions Enterprise corrigées** : Dans README et docs principaux
- ✅ **Dates uniformisées** : Tous les .md → `novembre 2025`
- ✅ **Formatage** : Black + Ruff OK
- ✅ **Push sur develop** : 3 commits effectués

---

## ❌ CE QUI RESTE À FAIRE

### 🔴 CRITIQUE (Impact crédibilité)

#### 1. **Badge Codecov officiel manquant** ⏱️ 15 min
- ❌ **État actuel** : Badge custom existe mais pas lié à Codecov
- ✅ **codecov.yml** existe et est configuré
- ❌ **Action** : Ajouter badge Codecov dans README :
  ```markdown
  [![codecov](https://codecov.io/gh/athalia-siwek/arkalia-luna-pro/branch/develop/graph/badge.svg)](https://codecov.io/gh/athalia-siwek/arkalia-luna-pro)
  ```
- 📍 **Emplacement** : Après le badge Coverage existant (ligne 11)

#### 2. **Documenter les 5 containers actifs** ⏱️ 1h
- ❌ **État actuel** : Pas de section dédiée dans README
- ✅ **docker-compose.yml** contient les définitions
- ❌ **Action** : Créer section "Architecture des Containers" dans README avec :
  - Liste des 5 containers actifs
  - Rôle de chaque container
  - Ports exposés
  - Dépendances entre containers
  - Diagramme Mermaid des interactions

---

### 🟠 HAUTE PRIORITÉ (Impact présentation)

#### 3. **Screenshots dashboard manquants** ⏱️ 2h
- ❌ **État actuel** : Seulement 1 PNG (`docs/img/diagram_kernel.png`)
- ❌ **Manque** :
  - Screenshot dashboard Grafana (8 dashboards mentionnés)
  - Screenshot orchestration Docker (`docker ps`)
  - Screenshot Prometheus
- ✅ **Action** :
  1. Capturer les screenshots
  2. Les ajouter dans `docs/img/`
  3. Les référencer dans README et `docs/infrastructure/monitoring.md`

#### 4. **Cas d'usage métier non documentés** ⏱️ 2-3h
- ❌ **État actuel** : Cas d'usage dans `reports/README_LANDING.md` mais pas dans doc principale
- ❌ **Manque** : Section "Cas d'usage" dans README et `docs/getting-started/`
- ✅ **Action** :
  1. Créer `docs/getting-started/use-cases.md`
  2. Déplacer/améliorer les 5 cas d'usage de `reports/README_LANDING.md`
  3. Ajouter exemples concrets avec code/config
  4. Ajouter section "Cas d'usage" dans README principal

#### 5. **Vue d'ensemble README à améliorer** ⏱️ 2h
- ⚠️ **État actuel** : README complet (339 lignes) mais manque de visuels
- ❌ **Manque** :
  - Diagramme d'architecture visuel (Mermaid ou image)
  - Section "Cas d'usage" avec exemples
  - Section "Architecture des Containers" avec diagramme
- ✅ **Action** :
  1. Ajouter diagramme Mermaid de l'architecture
  2. Ajouter section "Cas d'usage" avec exemples
  3. Améliorer section "Architecture" avec diagramme visuel

---

### 🟡 MOYENNE PRIORITÉ (Amélioration continue)

#### 6. **Documentation containers dédiée** ⏱️ 1h
- ❌ **État actuel** : Pas de fichier dédié
- ✅ **Action** : Créer `docs/architecture/containers.md` avec :
  - Description détaillée de chaque container
  - Diagramme d'interactions entre containers (Mermaid)
  - Guide de configuration et déploiement

---

## 📊 RÉSUMÉ PAR PRIORITÉ

| Priorité | Tâche | Temps | Statut |
|-----------|-------|-------|--------|
| 🔴 CRITIQUE | Badge Codecov | 15 min | ❌ À faire |
| 🔴 CRITIQUE | Doc 5 containers | 1h | ❌ À faire |
| 🟠 HAUTE | Screenshots dashboard | 2h | ❌ À faire |
| 🟠 HAUTE | Cas d'usage métier | 2-3h | ❌ À faire |
| 🟠 HAUTE | Vue d'ensemble README | 2h | ❌ À faire |
| 🟡 MOYENNE | Doc containers dédiée | 1h | ❌ À faire |

**Temps total estimé** : **8-10h**

---

## 🎯 PROCHAINES ÉTAPES RECOMMANDÉES

### Phase 1 : Corrections rapides (30 min)
1. ✅ Badge Codecov (15 min)
2. ✅ Section "Architecture des Containers" dans README (15 min)

### Phase 2 : Documentation (3-4h)
3. ✅ Cas d'usage métier (`docs/getting-started/use-cases.md`)
4. ✅ Section "Cas d'usage" dans README
5. ✅ Diagramme architecture Mermaid

### Phase 3 : Visuels (2h)
6. ✅ Screenshots dashboard Grafana
7. ✅ Screenshot orchestration Docker

### Phase 4 : Documentation avancée (1h)
8. ✅ `docs/architecture/containers.md` dédié

---

## 📝 NOTES

- **Badge Codecov** : Nécessite que le repo soit connecté à Codecov.io (peut nécessiter setup GitHub)
- **Screenshots** : Nécessite que Docker et Grafana soient démarrés pour capturer
- **Cas d'usage** : Contenu existe dans `reports/README_LANDING.md`, à déplacer/améliorer

---

**Dernière mise à jour** : novembre 2025  
**Basé sur** : AUDIT_VERIFICATION_PLAN_ACTION_V2.md


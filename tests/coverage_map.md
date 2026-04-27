# 🧪 Carte de couverture des tests

**Date** : avril 2026  
**Version** : v2.8.x  
**Objectif** : cartographie opérationnelle des zones de tests et commandes de validation.

> ⚠️ Cette carte est indicative. La source de vérité reste l’arborescence courante sous `tests/` et les résultats `pytest` en CI.

## 📋 Standards de qualité

Chaque module doit idéalement avoir :

- au moins 2 tests unitaires ;
- au moins 1 test d’intégration (si API) ;
- au moins 1 test edge case (si logique IA) ;
- une couverture renforcée pour les modules critiques.

## 🧠 Modules IA principaux

### ZeroIA

- **Statut** : à vérifier dynamiquement.
- **Commande de base** :

```bash
pytest tests/unit/zeroia/ -v
pytest tests/integration/zeroia/ -v
```

### Reflexia

- **Statut** : à vérifier dynamiquement.
- **Commande de base** :

```bash
pytest tests/unit/reflexia/ -v
pytest tests/integration/reflexia/ -v
```

### AssistantIA

- **Statut** : à vérifier dynamiquement.
- **Commande de base** :

```bash
pytest tests/unit/assistantia/ -v
pytest tests/integration/modules/test_assistantia_*.py -v
```

### Sandozia

- **Statut** : à vérifier dynamiquement.
- **Commande de base** :

```bash
pytest tests/unit/sandozia/ -v
pytest tests/integration/sandozia/ -v
```

### Cognitive Reactor

- **Statut** : couverture ciblée existante.
- **Commande de base** :

```bash
pytest tests/unit/cognitive_reactor/ -v
pytest tests/integration/cognitive_reactor/ -v
```

## 🔒 Sécurité et support

### Security

```bash
pytest tests/unit/security/ -v
pytest tests/security/ -v
```

### Core

```bash
pytest tests/unit/core/ -v
pytest tests/integration/modules/test_core_optimizations_integration.py -v
```

### Monitoring

```bash
pytest tests/unit/monitoring/ -v
pytest tests/integration/test_metrics_endpoint.py -v
```

## 🧪 Tests spécialisés

### Performance

```bash
pytest tests/performance/ -v -m performance
pytest tests/performance/zeroia/test_zeroia_performance.py -v
```

### Chaos

```bash
pytest tests/chaos/ -v -m chaos
```

### E2E

```bash
pytest tests/e2e/ -v
```

## 📊 Objectifs de couverture

| Domaine | Cible |
| --- | --- |
| Modules critiques | >= 80% |
| Couverture globale | seuil CI en vigueur |
| Régression | 0 test cassé sur suites ciblées |

## 🚀 Commandes de validation

### Validation rapide locale

```bash
pytest tests/unit/ -x -q
```

### Validation complète

```bash
make test
```

### Rapport HTML

```bash
pytest --cov=modules --cov-report=html
open htmlcov/index.html
```

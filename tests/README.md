# 📚 Arkalia-LUNA Pro — Stratégie et Structure des Tests

## 🧪 Pyramide de tests

- **Unitaires** : tests isolés, sans dépendance externe (`unit/`)
- **Intégration** : interactions entre modules/services (`integration/`)
- **Performance** : benchmarks, stress, temps de réponse (`performance/`)
- **Chaos** : résilience, tolérance aux pannes (`chaos/`)
- **Sécurité** : vulnérabilités, permissions, secrets (`security/`)
- **E2E** : scénarios bout-en-bout, API, DB, mémoire (`e2e/`)
- **Fixtures** : données et helpers partagés (`fixtures/`)
- **Reports** : rapports de couverture, logs, benchmarks (`reports/`)

## 📁 Structure

```
tests/
├── unit/
├── integration/
├── performance/
├── chaos/
├── security/
├── e2e/
├── fixtures/
├── reports/
├── conftest.py
├── tmp/  # À ignorer dans Git
└── README.md
```

## 🚦 Exécution

- **Tous les tests** : `pytest tests/`
- **Unitaires** : `pytest tests/unit/`
- **Intégration** : `pytest -c config/pytest/pytest-integration.ini`
- **Performance** : `pytest -c pytest-performance.ini`
- **Chaos** : `pytest -c pytest-chaos.ini`
- **Sécurité** : `pytest -c pytest-security.ini`
- **E2E** : `pytest tests/e2e/`

## 🛠️ Bonnes pratiques

- Respecter la structure et les conventions de nommage
- Centraliser les fixtures dans `fixtures/`
- Documenter chaque dossier avec un README
- Ne pas versionner `tmp/` ni les fichiers générés automatiquement
- Utiliser les scripts CI pour générer les rapports dans `reports/`

## 📚 Ressources
- [Guide de contribution](../docs/credits/CONTRIBUTING.md)
- [Cahier des charges](../docs/architecture/cahier_des_charges_v4.0.md)

# 🧪 tests/

Ce dossier contient tous les **tests unitaires, d'intégration, de performance et de sécurité** du projet.

- `unit/` : tests unitaires
- `integration/` : tests d'intégration
- `performance/` : tests de performance
- `security/` : tests de sécurité
- `fixtures/` : fixtures et helpers

**Lancez les tests avec `pytest` ou les scripts fournis.**

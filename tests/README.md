# 📚 Arkalia-LUNA Pro — Stratégie et Structure des Tests

## 🧪 Pyramide de tests

- **Unitaires** : tests isolés, sans dépendance externe (`unit/`)
- **Intégration** : interactions entre modules/services (`integration/`)
- **Performance** : benchmarks, stress, temps de réponse (`performance/`)
- **Chaos** : résilience, tolérance aux pannes (`chaos/`)
- **Sécurité** : vulnérabilités, permissions, secrets (`security/`)
- **E2E** : scénarios bout-en-bout, API, DB, mémoire (`e2e/`)
- **Fixtures** : données et helpers partagés (`fixtures/`)
- **Reports** : rapports générés en CI/local (dossier non versionné)

## 📁 Structure

```text
tests/
├── unit/
├── integration/
├── performance/
├── chaos/
├── security/
├── e2e/
├── fixtures/
├── conftest.py
├── tmp/  # À ignorer dans Git
└── README.md
```

## 🚦 Exécution

- **Tous les tests** : `pytest tests/`
- **Unitaires** : `pytest tests/unit/`
- **Intégration** : `pytest tests/integration/ -v`
- **Performance** : `pytest tests/performance/ -v`
- **Chaos** : `pytest tests/chaos/ -v -m "not slow"`
- **Sécurité** : `pytest tests/security/ -v`
- **E2E** : `pytest tests/e2e/`

## 🛠️ Bonnes pratiques

- Respecter la structure et les conventions de nommage
- Centraliser les fixtures dans `fixtures/`
- Documenter chaque dossier avec un README
- Ne pas versionner `tmp/` ni les fichiers générés automatiquement
- Utiliser les scripts CI pour générer les rapports (artefacts CI/local non versionnés)

## 📚 Ressources

- [Guide de contribution](../docs/credits/CONTRIBUTING.md)
- [Cahier des charges](../docs/architecture/cahier_des_charges_v4.0.md)

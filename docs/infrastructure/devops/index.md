# DevOps & Qualite

Reference courte des pratiques DevOps du projet.

## Objectifs

- Pipeline reproductible (lint, tests, build).
- Validation securite continue.
- Documentation maintenable et non obsolescente.
- Surveillance runtime avec alertes.

## Boucle locale recommandee

```bash
ruff check .
black --check .
pytest tests/unit/ tests/integration/ -q
```

## Controles CI

- Linting Python.
- Tests automatiques.
- Checks securite.
- Build/validation des artefacts.

## Commandes utiles

```bash
# Verification monitoring
python scripts/dev/ark-validate-monitoring.py

# Verification securite
./scripts/ops/ark-sec-check.sh --full-validation

# Validation workflows
bash scripts/dev/validate-workflows.sh
```

## Sous-guides

- [Resolution linting](linting-resolution.md)
- [Securite DevOps](security.md)
- [Monitoring](../monitoring.md)

# Scripts shell legacy

Ce dossier contient des scripts historiques conservés pour compatibilité.

## Règle

- Préférer les scripts canoniques dans `scripts/` à la racine.
- Les scripts de ce dossier doivent idéalement rester des wrappers légers.

## Mappings recommandés

- `scripts/shell/ark-start.sh` -> `scripts/ark-docker-start.sh`
- `scripts/shell/docker-start.sh` -> `scripts/ark-docker-start.sh`
- `scripts/shell/ark-fix-all.sh` -> `scripts/ark-fix-linting.sh`
- `scripts/shell/test_healthcheck.sh` -> `scripts/health_check.sh full`

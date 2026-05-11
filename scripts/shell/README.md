# Scripts shell legacy

Ce dossier contient des scripts historiques conservés pour compatibilité.

## Règle

- Préférer les scripts canoniques dans `scripts/dev/`, `scripts/ops/` ou `scripts/run/`.
- Les scripts de ce dossier doivent idéalement rester des wrappers légers.

## Mappings recommandés

- `scripts/shell/ark-start.sh` -> `scripts/ops/ark-docker-start.sh`
- `scripts/shell/docker-start.sh` -> `scripts/ops/ark-docker-start.sh`
- `scripts/shell/ark-fix-all.sh` -> `scripts/dev/ark-fix-linting.sh`
- `scripts/shell/test_healthcheck.sh` -> `scripts/ops/health_check.sh full`

## Scripts encore autonomes

Ces scripts conservent une logique propre et ne sont pas encore migrés:

- `scripts/shell/ark-clean.sh`
- `scripts/shell/ark-archive.sh`
- `scripts/shell/ark-test-full.sh`
- `scripts/shell/ark-test-performance.sh`
- `scripts/shell/ark-consolidate.sh`
- `scripts/shell/ark-purge-archive.sh`
- `scripts/shell/dev-start.sh`
- `scripts/shell/restore_config.sh`
- `scripts/shell/arkalia-launch-optimized.sh`
- `scripts/shell/arkalia.sh`
- `scripts/shell/install_arkalia_enhanced.sh`

## Règle de migration

Lors d'une évolution d'un script autonome:

1. créer (ou identifier) un script canonique dans `scripts/dev/`, `scripts/ops/` ou `scripts/run/`,
2. y déplacer la logique métier,
3. convertir le script `scripts/shell/` en wrapper de compatibilité.

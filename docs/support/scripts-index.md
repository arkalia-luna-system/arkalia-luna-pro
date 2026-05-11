# Catalogue des scripts

Cette page sert de point d'entrée pour éviter la prolifération de scripts redondants.

## Convention de nommage

- Scripts shell: preferer `kebab-case` (ex: `ark-setup-shell.sh`).
- Scripts Python: preferer `snake_case` (ex: `check_versions.py`).
- Prefixe `ark-` reserve aux scripts shell de la toolchain locale.
- Nouveaux scripts a placer dans `scripts/dev/`, `scripts/ops/` ou `scripts/run/` (pas en racine).

## Exploitation Docker

- `scripts/ops/ark-docker-start.sh`
- `scripts/ops/ark-docker-stop.sh`
- `scripts/ops/ark-docker-status.sh`
- `scripts/ops/ark-docker-rebuild.sh`
- `scripts/ops/ark-docker-dev.sh`

## Nettoyage & hygiène

- `scripts/ops/ark-clean-state.sh`
- `scripts/ops/ark-clean-json.sh`
- `scripts/ops/ark-clean-hidden.sh`
- `scripts/dev/ark-fix-style.sh`
- `scripts/dev/ark-fix-linting.sh`

## Validation & sécurité

- `scripts/ops/ark-zeroia-check.sh`
- `scripts/ops/ark-sec-check.sh`
- `scripts/dev/validate-workflows.sh`
- `scripts/dev/validate-dockerfiles.sh`
- `scripts/dev/ark-docs-check.sh`

## Monitoring & santé

- `scripts/ops/start-monitoring.sh`
- `scripts/ops/health_check.sh`
- `scripts/ops/auto-heal.sh`
- `scripts/ops/setup_log_scrubber_cron.sh`

## VSCode / Cursor

- Script canonique: `scripts/dev/ark-vscode-reload.sh`
- Diagnostic: `scripts/dev/ark-vscode-diagnostic.sh`
- Correctif config: `scripts/dev/ark-fix-vscode-config.sh`

## Règles de maintenance

- Éviter les doublons fonctionnels.
- Préférer un script court et focalisé.
- Documenter les entrées/sorties attendues dans le script lui-même.
- Pour les scripts historiques, préférer un wrapper vers un script canonique.
- Consulter `scripts/shell/README.md` avant de modifier un script legacy.

## Migration recente (racine -> dossiers canoniques)

Les anciens noms en racine ont ete deplaces vers `scripts/dev/` et `scripts/ops/`.
Pour toute nouvelle integration, utiliser directement les chemins canoniques ci-dessus.

# Catalogue des scripts

Cette page sert de point d'entrée pour éviter la prolifération de scripts redondants.

## Exploitation Docker

- `scripts/ark-docker-start.sh`
- `scripts/ark-docker-stop.sh`
- `scripts/ark-docker-status.sh`
- `scripts/ark-docker-rebuild.sh`
- `scripts/ark-docker-dev.sh`

## Nettoyage & hygiène

- `scripts/ark-clean-state.sh`
- `scripts/ark-clean-json.sh`
- `scripts/ark-clean-hidden.sh`
- `scripts/ark-fix-style.sh`
- `scripts/ark-fix-linting.sh`

## Validation & sécurité

- `scripts/ark-zeroia-check.sh`
- `scripts/ark-sec-check.sh`
- `scripts/validate-workflows.sh`
- `scripts/validate-dockerfiles.sh`
- `scripts/ark-docs-check.sh`

## Monitoring & santé

- `scripts/start-monitoring.sh`
- `scripts/health_check.sh`
- `scripts/auto-heal.sh`
- `scripts/setup_log_scrubber_cron.sh`

## VSCode / Cursor

- Script canonique: `scripts/ark-vscode-reload.sh`
- Alias compatibilité: `scripts/ark-reload-vscode.sh`
- Diagnostic: `scripts/ark-vscode-diagnostic.sh`
- Correctif config: `scripts/ark-fix-vscode-config.sh`

## Règles de maintenance

- Éviter les doublons fonctionnels.
- Préférer un script court et focalisé.
- Documenter les entrées/sorties attendues dans le script lui-même.

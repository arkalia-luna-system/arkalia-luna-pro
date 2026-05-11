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

- `scripts/ark-check-hooks.sh` -> `scripts/dev/ark-check-hooks.sh`
- `scripts/ark-fix-modules.sh` -> `scripts/dev/ark-fix-modules.sh`
- `scripts/ark-fix-vscode-config.sh` -> `scripts/dev/ark-fix-vscode-config.sh`
- `scripts/ark-gpg-setup.sh` -> `scripts/dev/ark-gpg-setup.sh`
- `scripts/ark-install-extensions.sh` -> `scripts/dev/ark-install-extensions.sh`
- `scripts/ark-reset-cursor.sh` -> `scripts/dev/ark-reset-cursor.sh`
- `scripts/ark-setup-shell.sh` -> `scripts/dev/ark-setup-shell.sh`
- `scripts/ark-setup-vscode.sh` -> `scripts/dev/ark-setup-vscode.sh`
- `scripts/ark-vscode-diagnostic.sh` -> `scripts/dev/ark-vscode-diagnostic.sh`
- `scripts/ark-vscode-reload.sh` -> `scripts/dev/ark-vscode-reload.sh`
- `scripts/ark-validate-site.sh` -> `scripts/dev/ark-validate-site.sh`
- `scripts/build_docs.sh` -> `scripts/dev/build_docs.sh`
- `scripts/validate-dockerfiles.sh` -> `scripts/dev/validate-dockerfiles.sh`
- `scripts/validate-workflows.sh` -> `scripts/dev/validate-workflows.sh`
- `scripts/ark-clean-hidden.sh` -> `scripts/ops/ark-clean-hidden.sh`
- `scripts/ark-clean-json.sh` -> `scripts/ops/ark-clean-json.sh`
- `scripts/ark-clean-state.sh` -> `scripts/ops/ark-clean-state.sh`
- `scripts/ark-module-diagnostic.sh` -> `scripts/ops/ark-module-diagnostic.sh`
- `scripts/ark-sec-check.sh` -> `scripts/ops/ark-sec-check.sh`
- `scripts/ark-zeroia-check.sh` -> `scripts/ops/ark-zeroia-check.sh`
- `scripts/auto-heal.sh` -> `scripts/ops/auto-heal.sh`
- `scripts/backup_state.sh` -> `scripts/ops/backup_state.sh`
- `scripts/diagnose-docker-issues.sh` -> `scripts/ops/diagnose-docker-issues.sh`
- `scripts/firewall_setup.sh` -> `scripts/ops/firewall_setup.sh`
- `scripts/optimize_containers.sh` -> `scripts/ops/optimize_containers.sh`
- `scripts/start_generative_ai.sh` -> `scripts/ops/start_generative_ai.sh`

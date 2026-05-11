# Scripts - Index

Ce dossier regroupe les scripts d'exploitation, de developpement et d'execution.

## Structure canonique

- `scripts/dev/`: outillage dev (lint, docs, checks, maintenance locale).
- `scripts/ops/`: operations et runbooks locaux (docker, monitoring, health).
- `scripts/run/`: points d'entree de lancement des services Python.
- `scripts/shell/`: scripts historiques, a traiter comme couche de compatibilite.

## Regles d'ajout

- Verifier si un script existant couvre deja le besoin.
- Preferer l'extension d'un script existant plutot qu'un nouveau fichier.
- Garder un nom explicite et une responsabilite unique.
- Placer tout nouveau script dans `dev/`, `ops/` ou `run/` (pas en racine).
- Nommage shell: `kebab-case`; nommage Python: `snake_case`.

## Documentation detaillee

Le catalogue maintenu des scripts est dans `docs/support/scripts-index.md`.

# Backup & Recovery

Guide court et operationnel pour la sauvegarde et la restauration.

## Perimetre critique

- Etats applicatifs: `state/`, `global_state/`, `modules/*/state/`
- Configuration: `config/`, `.env` (si utilise)
- Logs utiles: `logs/`, `modules/*/logs/`
- Source de verite code: Git

## Politique recommandee

- Strategie 3-2-1: 3 copies, 2 supports, 1 hors site.
- Chiffrement obligatoire des archives hors machine.
- Verification d'integrite (checksums) sur chaque lot.
- Test de restauration planifie (hebdo minimum).

## Sauvegarde locale minimale

```bash
mkdir -p /backup/daily
TS="$(date +%Y%m%d_%H%M%S)"

tar -czf "/backup/daily/states_${TS}.tar.gz" state global_state modules/*/state 2>/dev/null
tar -czf "/backup/daily/config_${TS}.tar.gz" config .env 2>/dev/null
tar -czf "/backup/daily/logs_${TS}.tar.gz" logs modules/*/logs 2>/dev/null

cd /backup/daily
sha256sum "*_${TS}.tar.gz" > "checksums_${TS}.sha256"
```

## Restauration rapide (etat)

```bash
LATEST="$(ls -1t /backup/daily/states_*.tar.gz | head -1)"
test -n "$LATEST" || { echo "Aucun backup etat"; exit 1; }

docker compose down
tar -xzf "$LATEST" -C .
python scripts/ops/ark-sec-check.sh --basic-validation || exit 1
docker compose up -d
```

## Rollback ZeroIA

En cas de corruption d'etat ZeroIA:

```bash
python scripts/_zeroia_rollback.py
```

## Checklist exploitation

- Quotidien: verifier qu'un backup est cree.
- Hebdo: restaurer sur environnement de test.
- Mensuel: test de reprise complete (infra + etat).
- A chaque incident: archiver logs + etats avant action.

## Anti-regression

- Ne pas versionner les artefacts de backup/profiling.
- Garder `.gitignore` a jour (`*.prof`, archives, dumps).
- Documenter tout changement de procedure ici.

# Docker Hardening

Guide compact pour durcir les services Docker.

## Baseline recommande

- `read_only: true` quand possible.
- `security_opt: [no-new-privileges:true]`.
- `cap_drop: [ALL]` et ajout minimal de capabilities.
- Utilisateur non-root dans les images.
- Healthcheck actif sur chaque service critique.
- Segmentation reseau entre API, data et monitoring.

## Exemple Compose

```yaml
services:
  zeroia:
    read_only: true
    restart: on-failure:3
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    tmpfs:
      - /tmp:rw,size=64m,mode=1777
```

## Exemple Dockerfile (non-root)

```dockerfile
FROM python:3.11-slim
RUN groupadd -r app && useradd -r -g app -d /app app
WORKDIR /app
COPY --chown=app:app . /app
USER app:app
CMD ["python", "-m", "app.main"]
```

## Verifications rapides

```bash
docker compose config
docker compose ps
./scripts/ops/ark-sec-check.sh --full-validation
```

## Bonnes pratiques

- Monter `config/` en lecture seule.
- Externaliser les secrets (pas de secret en clair dans Git).
- Journaliser et centraliser les logs.
- Scanner les images avant deploiement (CI + local si besoin).

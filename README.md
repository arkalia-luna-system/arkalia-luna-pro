# Arkalia-LUNA Pro

Orchestrateur IA modulaire orienté fiabilité, observabilité et sécurité.

## Démarrage rapide

```bash
git clone https://github.com/arkalia-luna-system/arkalia-luna-pro.git
cd arkalia-luna-pro
docker-compose up -d
curl http://localhost:8000/health
```

## Services principaux

- API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- Grafana: `http://localhost:3000`
- Prometheus: `http://localhost:9090`

La stack monitoring est gérée séparément via `infrastructure/monitoring/docker-compose.monitoring.yml`.

## Vérifications rapides

```bash
python3 -m pytest -q
cd frontend && npm run build
```

## Documentation ciblée

- Guide de démarrage: `docs/getting-started/quick-start.md`
- Architecture: `docs/architecture/overview.md`
- Infrastructure: `docs/infrastructure/index.md`
- Sécurité: `docs/security/index.md`
- Support scripts: `docs/support/scripts-index.md`

## Contribution

- Policy sécurité: `SECURITY.md`
- Standards: tests + `black` + `ruff`

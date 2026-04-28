# TODO Opérationnel — Arkalia-LUNA Pro

Ce document centralise les tâches opérationnelles restantes.

## Screenshots Dashboard

**Temps estimé**: 2h (intervention manuelle)

Objectif: capturer des screenshots des dashboards de monitoring pour la documentation.

### Actions

1. Démarrer les services:

```bash
docker-compose up -d
cd infrastructure/monitoring
docker-compose -f docker-compose.monitoring.yml up -d
```

1. Capturer les screenshots:
   - Grafana: `http://localhost:3000` (8 dashboards principaux)
   - Prometheus: `http://localhost:9090`
   - AlertManager: `http://localhost:9093`
   - Docker: `docker ps` (sortie terminale)

1. Sauvegarder dans `docs/img/`:
   - `dashboard-grafana-overview.png`
   - `dashboard-grafana-cognitif.png`
   - `dashboard-prometheus.png`
   - `docker-containers.png`
   - `alertmanager.png`

1. Référencer dans:
   - `README.md` (section monitoring)
   - `docs/infrastructure/monitoring.md`

## Statut

- Code quality: OK
- Tests: OK
- Architecture: OK
- Documentation: complète, sauf captures visuelles

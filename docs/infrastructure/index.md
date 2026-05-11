# Infrastructure Arkalia-LUNA

Vue d'ensemble operationnelle de l'infrastructure.

## Composants

- API principale et modules applicatifs.
- Stack monitoring (`Prometheus`, `Grafana`, `Alertmanager`, `Loki`).
- CI/CD GitHub Actions.
- Outils securite et reprise (`docs/security/*`).

## Demarrage rapide

```bash
git clone https://github.com/arkalia-luna-system/arkalia-luna-pro.git
cd arkalia-luna-pro
cp config/settings.toml.example config/settings.toml
docker compose up -d
python scripts/dev/ark-validate-monitoring.py
```

## Verification minimale

```bash
docker compose ps
curl -fsS http://localhost:8000/health
curl -fsS http://localhost:8000/metrics | head
```

## Maintenance

```bash
# Securite
./scripts/ops/ark-sec-check.sh --full-validation

# Backup etat
./scripts/ops/backup_state.sh

# Nettoyage logs sensibles
python scripts/ops/log_scrubber.py --dry-run
```

## Guides associes

- [Deploiement](deployment.md)
- [Monitoring](monitoring.md)
- [CI/CD](ci-cd.md)
- [Configuration](configuration.md)
- [Guide Ops](guides/ops-guide.md)
- [Hardening Docker](guides/docker_hardening.md)

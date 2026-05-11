# Monitoring Complet - Arkalia-LUNA

Guide de reference pour l'observabilite Arkalia (Prometheus, Grafana, Alertmanager, Loki, cAdvisor).

## Vue d'ensemble

- Grafana : visualisation en temps reel.
- Prometheus : collecte et stockage des metriques.
- Alertmanager : routage et regroupement des alertes.
- Loki : centralisation des logs.
- cAdvisor : metriques conteneurs.
- Arkalia API : endpoint applicatif pour metriques et sante.

## Demarrage rapide

### 1) Demarrer la stack monitoring

```bash
cd infrastructure/monitoring
docker-compose -f infrastructure/monitoring/docker-compose.monitoring.yml up -d
docker-compose -f infrastructure/monitoring/docker-compose.monitoring.yml ps
```

### 2) Valider localement

```bash
python scripts/ark-validate-monitoring.py
pytest tests/performance/ -v
pytest tests/security/ -v
```

### 3) Acces services

| Service | URL | Description | Credentials |
| --- | --- | --- | --- |
| Grafana | [http://localhost:3000](http://localhost:3000) | Dashboards temps reel | `admin / arkalia-secure-2025` |
| Prometheus | [http://localhost:9090](http://localhost:9090) | Metriques systeme | - |
| Alertmanager | [http://localhost:9093](http://localhost:9093) | Gestion alertes | - |
| Loki | [http://localhost:3100](http://localhost:3100) | Centralisation logs | - |
| cAdvisor | [http://localhost:8080](http://localhost:8080) | Metriques conteneurs | - |
| Arkalia API | [http://localhost:8000](http://localhost:8000) | API principale | - |

## Familles de metriques

### Systeme

- `arkalia_system_cpu_usage`
- `arkalia_system_memory_usage`
- `arkalia_system_disk_usage`
- `arkalia_system_uptime`
- `arkalia_system_load_average`

### API

- `arkalia_api_requests_total`
- `arkalia_api_request_duration_seconds`
- `arkalia_api_requests_in_progress`
- `arkalia_api_errors_total`
- `arkalia_api_response_size_bytes`

### Modules

- `arkalia_module_status`
- `arkalia_module_performance_score`
- `arkalia_module_confidence_score`
- `arkalia_module_decision_count`
- `arkalia_module_error_count`

### ZeroIA

- `arkalia_zeroia_decisions_total`
- `arkalia_zeroia_confidence_average`
- `arkalia_zeroia_contradictions_detected`
- `arkalia_zeroia_processing_time_seconds`
- `arkalia_zeroia_circuit_breaker_status`

### AssistantIA

- `arkalia_assistantia_prompts_total`
- `arkalia_assistantia_response_time_seconds`
- `arkalia_assistantia_security_blocks`
- `arkalia_assistantia_rate_limit_hits`
- `arkalia_assistantia_model_usage`

### Reflexia

- `arkalia_reflexia_monitoring_checks`
- `arkalia_reflexia_system_latency_ms`
- `arkalia_reflexia_health_score`
- `arkalia_reflexia_alerts_generated`
- `arkalia_reflexia_recovery_actions`

### Securite

- `arkalia_security_blocks_total`
- `arkalia_security_rate_limit_violations`
- `arkalia_security_invalid_requests`
- `arkalia_security_authentication_failures`
- `arkalia_security_authorization_failures`

## Alerting

Niveaux usuels :

- `critical` : indisponibilite service ou saturation.
- `warning` : degradation de performance.
- `info` : evenement non bloquant.

Exemples de regles :

- CPU > 80 % sur 5 minutes.
- RAM > 6 Go sur 5 minutes.
- Erreurs 5xx > 5 % sur 2 minutes.
- Latence P95 > 2 s sur 3 minutes.

## Maintenance

```bash
# Verification quotidienne
python scripts/ark-validate-monitoring.py

# Nettoyage metriques anciennes
docker exec prometheus promtool tsdb clean --older-than 30d

# Regeneration dashboard local
python scripts/generate_dashboard.py
```

## Depannage rapide

```bash
curl http://localhost:9090/api/v1/status/targets
curl http://localhost:3000/api/health
curl http://localhost:9093/api/v1/status
curl http://localhost:8000/metrics
```

## Notes

- Derniere mise a jour : novembre 2025.
- Mainteneur : Arkalia-LUNA Team.

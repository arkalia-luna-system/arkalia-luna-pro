# ⚙️ Configuration — Arkalia-LUNA v2.8.0

> Guide complet pour configurer correctement le système IA **Arkalia-LUNA**, en garantissant stabilité, performance et sécurité avec monitoring complet.

---

## 🔑 Paramètres Essentiels

- **Fichier principal** : `config/system/config.yaml`
  Contient :
  - chemins d'accès (logs, state, modules…)
  - clés API locales (si activées)
  - poids IA initiaux (`weights.toml`)

- **Variables d'environnement** :
  - `ARKALIA_ENV=dev` ou `prod`
  - `OLLAMA_HOST=http://localhost:11434`
  - `ARKALIA_SECRET_KEY=...` *(à définir)*

Définir dans `.env`, `.zshrc` ou `docker-compose.yml` selon le mode utilisé.

---

## 📊 Configuration Monitoring

### Variables d'Environnement Monitoring
```bash
# Services Monitoring
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000
ALERTMANAGER_PORT=9093
LOKI_PORT=3100
CADVISOR_PORT=8080

# Grafana
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=arkalia-secure-2025

# Prometheus
PROMETHEUS_RETENTION_DAYS=30
PROMETHEUS_SCRAPE_INTERVAL=15s

# AlertManager
ALERTMANAGER_SMTP_HOST=smtp.gmail.com
ALERTMANAGER_SMTP_PORT=587
ALERTMANAGER_SMTP_USER=arkalia.luna.system@gmail.com
ALERTMANAGER_SMTP_PASSWORD=secure-password
```

### Ports des Services
| Service | Port | Description | URL |
|---------|------|-------------|-----|
| **Arkalia API** | 8000 | API principale + métriques | http://localhost:8000 |
| **Grafana** | 3000 | Dashboards temps réel | http://localhost:3000 |
| **Prometheus** | 9090 | Métriques système | http://localhost:9090 |
| **AlertManager** | 9093 | Gestion alertes | http://localhost:9093 |
| **Loki** | 3100 | Centralisation logs | http://localhost:3100 |
| **cAdvisor** | 8080 | Métriques conteneurs | http://localhost:8080 |

### Endpoints Métriques
```bash
# Métriques Prometheus
GET /metrics

# Statut détaillé
GET /status

# Health check
GET /health

# API principale
GET /
```

---

## ⚙️ Configuration Avancée

### 🔧 Modules personnalisés

Chaque module IA dispose de son propre fichier :

modules/<nom_module>/config/config.toml

- Tu peux y adapter le comportement (seuils, poids, déclencheurs, etc.)

### 📊 Configuration Monitoring Avancée

#### Prometheus
```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "rules/*.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets: ["alertmanager:9093"]

scrape_configs:
  - job_name: 'arkalia-api (port 8000)'
    static_configs:
      - targets: ['host.docker.internal:8000']
    metrics_path: '/metrics'
    scrape_interval: 15s
```

#### AlertManager
```yaml
# alertmanager.yml
global:
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_from: 'arkalia.luna.system@gmail.com'
  smtp_auth_username: 'arkalia.luna.system@gmail.com'
  smtp_auth_password: 'secure-password'

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'arkalia-alerts'

receivers:
  - name: 'arkalia-alerts'
    email_configs:
      - to: 'arkalia.luna.system@gmail.com'
```

### 🚀 Optimisations recommandées

- **Docker** : Limite CPU/mémoire pour chaque container
- **FastAPI** : Config `workers`, `keep-alive` dans `uvicorn`
- **Logs** : Rotation automatique via `logging.conf` si besoin
- **Monitoring** : Rétention Prometheus 30 jours, compression automatique

---

## 🧾 Bonnes pratiques

| Sécurité | Recommandation |
|---------|-----------------|
| 🔒 | Ne jamais committer les clés dans Git |
| 🛡️ | Sauvegarde automatique régulière (`ark-backup`) |
| 🔍 | Vérifier les accès avec `ZeroIA` ou `Reflexia` |
| 🧩 | Isoler les `venv`, les fichiers `.env` et `/state/` |
| 📊 | Monitoring 24/7 avec alertes automatiques |
| 🔐 | Chiffrement des métriques sensibles |

---

## ✅ Checklist post-installation

- [x] `config.yaml` bien rempli
- [x] variables d'environnement définies
- [x] modules IA accessibles
- [x] Docker + FastAPI fonctionnels
- [x] scripts `arkalia-*.sh` opérationnels
- [x] **Monitoring démarré** (`docker-compose -f docker-compose.monitoring.yml up -d`)
- [x] **Grafana accessible** (http://localhost:3000)
- [x] **Prometheus scrape** les métriques
- [x] **Alertes configurées** et testées
- [x] **Validation monitoring** (`python scripts/ark-validate-monitoring.py`)
- [x] **Tests de performance** (`pytest tests/performance/`)
- [x] **Tests de sécurité** (`pytest tests/security/`)

---

## 🔧 Validation Configuration

### Test Monitoring
```bash
# Validation complète
python scripts/ark-validate-monitoring.py

# Vérification services
docker-compose -f infrastructure/monitoring/docker-compose.monitoring.yml ps

# Test métriques
curl http://localhost:8000/metrics

# Test Grafana
curl -u admin:arkalia-secure-2025 http://localhost:3000/api/health
```

### Test Modules
```bash
# Test ZeroIA
python -c "from modules.zeroia.coordinator import ZeroIACoordinator; print('ZeroIA OK')"

# Test Sandozia
python -c "from modules.sandozia.core.sandozia_core import SandoziaCore; print('Sandozia OK')"

# Test Reflexia
python -c "from modules.reflexia.core import launch_reflexia_check; print('Reflexia OK')"

# Test API
curl http://localhost:8000/status
```

---

💡 Une **configuration propre**, c'est la garantie d'un système IA **autonome, sécurisé, monitoré et sans dette technique**.

### **Validation et Tests**
```bash
# Validation monitoring
python scripts/ark-validate-monitoring.py

# Tests de performance
pytest tests/performance/ -v

# Tests de sécurité
pytest tests/security/ -v
```

# 📊 Monitoring Complet - Arkalia-LUNA v2.8.0

> Guide complet pour l'infrastructure de monitoring d'Arkalia-LUNA avec observabilité totale, métriques avancées et alertes intelligentes.

---

## 🎯 Vue d'ensemble

Arkalia-LUNA v2.8.0 intègre une infrastructure de monitoring complète et professionnelle :

- **📊 Grafana** : Dashboards temps réel avec 8 panels spécialisés
- **📈 Prometheus** : Collecte et stockage de 34 métriques Arkalia
- **🚨 AlertManager** : 15 règles d'alertes intelligentes
- **📝 Loki** : Centralisation des logs système
- **🐳 cAdvisor** : Métriques des conteneurs Docker
- **🔌 Arkalia API** : Endpoints métriques intégrés

---

## 🚀 Démarrage Rapide

### 1. Démarrer le Monitoring
```bash
# Aller dans le dossier monitoring
cd infrastructure/monitoring

# Démarrer tous les services
docker-compose -f docker-compose.monitoring.yml up -d

# Vérifier le statut
docker-compose -f docker-compose.monitoring.yml ps
```

### 2. Validation Automatique
```bash
### **Validation du Monitoring**
```bash
# Validation complète
python scripts/ark-validate-monitoring.py

# Tests de performance
pytest tests/performance/ -v

# Tests de sécurité
pytest tests/security/ -v
```

### 3. Accès aux Services
| Service | URL | Description | Credentials |
|---------|-----|-------------|-------------|
| **Grafana** | http://localhost:3000 | Dashboards temps réel | admin / arkalia-secure-2025 |
| **Prometheus** | http://localhost:9090 | Métriques système | - |
| **AlertManager** | http://localhost:9093 | Gestion alertes | - |
| **Loki** | http://localhost:3100 | Centralisation logs | - |
| **cAdvisor** | http://localhost:8080 | Métriques conteneurs | - |
| **Arkalia API** | http://localhost:8000 | API principale + métriques | - |

---

## 📊 Métriques Arkalia

### Métriques Système
- `arkalia_system_cpu_usage` : Utilisation CPU en pourcentage
- `arkalia_system_memory_usage` : Utilisation mémoire en bytes
- `arkalia_system_disk_usage` : Utilisation disque en pourcentage
- `arkalia_system_uptime` : Temps de fonctionnement en secondes
- `arkalia_system_load_average` : Charge système moyenne

### Métriques API
- `arkalia_api_requests_total` : Nombre total de requêtes
- `arkalia_api_request_duration_seconds` : Durée des requêtes
- `arkalia_api_requests_in_progress` : Requêtes en cours
- `arkalia_api_errors_total` : Nombre total d'erreurs
- `arkalia_api_response_size_bytes` : Taille des réponses

### Métriques Modules
- `arkalia_module_status` : Statut des modules (0=inactif, 1=actif)
- `arkalia_module_performance_score` : Score de performance (0-1)
- `arkalia_module_confidence_score` : Score de confiance (0-1)
- `arkalia_module_decision_count` : Nombre de décisions prises
- `arkalia_module_error_count` : Nombre d'erreurs

### Métriques ZeroIA
- `arkalia_zeroia_decisions_total` : Décisions prises
- `arkalia_zeroia_confidence_average` : Confiance moyenne
- `arkalia_zeroia_contradictions_detected` : Contradictions détectées
- `arkalia_zeroia_processing_time_seconds` : Temps de traitement
- `arkalia_zeroia_circuit_breaker_status` : Statut circuit breaker

### Métriques AssistantIA
- `arkalia_assistantia_prompts_total` : Prompts traités
- `arkalia_assistantia_response_time_seconds` : Temps de réponse
- `arkalia_assistantia_security_blocks` : Blocages de sécurité
- `arkalia_assistantia_rate_limit_hits` : Limites de taux atteintes
- `arkalia_assistantia_model_usage` : Utilisation des modèles

### Métriques Reflexia
- `arkalia_reflexia_monitoring_checks` : Vérifications monitoring
- `arkalia_reflexia_system_latency_ms` : Latence système
- `arkalia_reflexia_health_score` : Score de santé
- `arkalia_reflexia_alerts_generated` : Alertes générées
- `arkalia_reflexia_recovery_actions` : Actions de récupération

### Métriques Sécurité
- `arkalia_security_blocks_total` : Blocages totaux
- `arkalia_security_rate_limit_violations` : Violations rate limit
- `arkalia_security_invalid_requests` : Requêtes invalides
- `arkalia_security_authentication_failures` : Échecs authentification
- `arkalia_security_authorization_failures` : Échecs autorisation

---

## 🎨 Dashboards Grafana

### Dashboard Principal
- **URL** : http://localhost:3000/d/arkalia-monitoring
- **Panels** : 8 panels spécialisés
- **Refresh** : 30 secondes
- **Thème** : Dark mode

### Panels Disponibles

#### 1. Système CPU & Mémoire
- Utilisation CPU en temps réel
- Utilisation mémoire avec seuils
- Charge système moyenne
- Tendances sur 24h

#### 2. Statut des Modules Arkalia
- Statut de chaque module (actif/inactif)
- Score de performance
- Score de confiance
- Indicateurs de santé

#### 3. Requêtes API en Temps Réel
- Nombre de requêtes par minute
- Répartition par endpoint
- Codes de statut HTTP
- Taux d'erreur

#### 4. Durée des Requêtes (P50/P95)
- Latence moyenne
- Percentiles P50 et P95
- Tendances de performance
- Seuils d'alerte

#### 5. ZeroIA - Confiance & Décisions
- Décisions prises par minute
- Score de confiance moyen
- Contradictions détectées
- Temps de traitement

#### 6. AssistantIA - Prompts & Réponses
- Prompts traités
- Temps de réponse moyen
- Blocages de sécurité
- Utilisation des modèles

#### 7. Reflexia - Monitoring Système
- Vérifications monitoring
- Latence système
- Score de santé
- Actions de récupération

#### 8. Erreurs & Alertes
- Erreurs par type
- Alertes actives
- Violations de sécurité
- Actions correctives

---

## 🚨 Système d'Alertes

### Niveaux de Sévérité
- **Critical** : Modules inactifs, erreurs 5xx, ressources critiques
- **Warning** : Performance dégradée, ressources élevées, seuils approchés
- **Info** : Blocages de sécurité, événements normaux, métriques

### Alertes Principales

#### Alertes Système
- **ArkaliaHighCPU** : CPU > 80% pendant 5 minutes
- **ArkaliaHighMemory** : RAM > 6GB pendant 5 minutes
- **ArkaliaHighDiskUsage** : Disque > 85% utilisé
- **ArkaliaSystemLoad** : Charge système > 5.0

#### Alertes Modules
- **ModuleInactive** : Module Arkalia inactif pendant 2 minutes
- **ModuleLowPerformance** : Performance < 0.5 pendant 5 minutes
- **ModuleLowConfidence** : Confiance < 0.3 pendant 3 minutes
- **ModuleHighErrorRate** : Taux d'erreur > 10%

#### Alertes API
- **HighErrorRate** : > 5% erreurs 5xx pendant 2 minutes
- **HighRequestLatency** : Latence P95 > 2s pendant 3 minutes
- **HighRequestVolume** : > 1000 req/min pendant 5 minutes
- **APIUnavailable** : API inaccessible pendant 1 minute

#### Alertes ZeroIA
- **ZeroIALowConfidence** : Confiance < 30% pendant 3 minutes
- **ZeroIAHighContradictions** : > 5 contradictions/min pendant 2 minutes
- **ZeroIACircuitBreakerOpen** : Circuit breaker ouvert
- **ZeroIAHighProcessingTime** : Temps traitement > 5s

#### Alertes AssistantIA
- **AssistantIAHighResponseTime** : Temps réponse > 10s
- **AssistantIAHighSecurityBlocks** : > 10 blocages/min
- **AssistantIARateLimitExceeded** : Rate limit dépassé
- **AssistantIAModelError** : Erreur modèle détectée

#### Alertes Sécurité
- **SecurityHighBlockRate** : > 20 blocages/min
- **SecurityRateLimitViolation** : Violation rate limit
- **SecurityAuthenticationFailure** : Échec authentification
- **SecurityAuthorizationFailure** : Échec autorisation

---

## 📈 Métriques de Performance

### Métriques Clés
- **Temps de réponse API** : < 2s (P95)
- **Disponibilité système** : 99.9%+
- **Couverture de tests** : 59.25%
- **Tests collectés** : 671
- **Métriques exposées** : 34

### Métriques de Qualité
- **Erreurs de linting** : 0
- **Warnings de sécurité** : 0
- **Pipeline CI** : 100% verte
- **Healthchecks** : Tous healthy

---

## 🔧 Configuration Avancée

### Prometheus Configuration
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'arkalia-api'
    static_configs:
      - targets: ['arkalia-api:8000']
    metrics_path: '/metrics'
    scrape_interval: 10s
```

### Grafana Dashboards
- **Dashboard Principal** : Monitoring global
- **Dashboard ZeroIA** : Métriques spécifiques ZeroIA
- **Dashboard Reflexia** : Métriques monitoring
- **Dashboard AssistantIA** : Métriques assistant
- **Dashboard Sécurité** : Métriques sécurité

### AlertManager Configuration
```yaml
route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'arkalia-team'

receivers:
  - name: 'arkalia-team'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/...'
        channel: '#arkalia-alerts'
```

---

## 🚀 Maintenance et Optimisation

### Tâches de Maintenance
```bash
# Vérification quotidienne
python scripts/ark-validate-monitoring.py

# Nettoyage des métriques anciennes
docker exec prometheus promtool tsdb clean --older-than 30d

# Sauvegarde des dashboards
python scripts/ark-backup-dashboards.py
```

### Optimisation des Performances
- **Rétention des métriques** : 30 jours
- **Compression des données** : Activée
- **Cache Grafana** : 5 minutes
- **Refresh des dashboards** : 30 secondes

### Monitoring de la Monitoring
- **Prometheus** : Métriques d'auto-monitoring
- **Grafana** : Dashboards de santé
- **AlertManager** : Alertes sur les alertes
- **Loki** : Logs de monitoring

---

## 🎯 Bonnes Pratiques

### Métriques
- **Nommage** : Préfixe `arkalia_` pour toutes les métriques
- **Labels** : Utilisation cohérente des labels
- **Documentation** : Chaque métrique documentée
- **Tests** : Validation des métriques

### Alertes
- **Seuils** : Seuils réalistes et testés
- **Groupement** : Alertes groupées logiquement
- **Escalade** : Processus d'escalade défini
- **Documentation** : Runbooks pour chaque alerte

### Dashboards
- **Organisation** : Panels logiquement organisés
- **Couleurs** : Palette de couleurs cohérente
- **Annotations** : Annotations pour les événements
- **Responsive** : Dashboards adaptatifs

---

## 🔍 Dépannage

### Problèmes Courants
1. **Prometheus ne scrape pas** : Vérifier la connectivité réseau
2. **Grafana ne charge pas** : Vérifier les permissions
3. **Alertes ne se déclenchent pas** : Vérifier la configuration
4. **Métriques manquantes** : Vérifier les endpoints

### Commandes de Diagnostic
```bash
# Vérifier Prometheus
curl http://localhost:9090/api/v1/status/targets

# Vérifier Grafana
curl http://localhost:3000/api/health

# Vérifier AlertManager
curl http://localhost:9093/api/v1/status

# Vérifier les métriques Arkalia
curl http://localhost:8000/metrics
```

---

*Dernière mise à jour : novembre 2025
*Version : v2.8.0*
*Mainteneur : Arkalia-LUNA Team*

# API Arkalia-LUNA Pro Enhanced v2.8.0

## État Actuel du Système (Mise à jour novembre 2025)

### CI/CD
- Résultats dynamiques selon le dernier run GitHub Actions
- Couverture : voir le rapport `coverage.xml` du pipeline (seuil requis : 28%)
- Temps d'exécution : variable selon la charge CI
- Healthcheck optimisé : Python urllib natif
- Artefacts uploadés : Conditionnel et robuste

Documentation complète de l'API REST d'Arkalia-LUNA Pro Enhanced.

**Version API** : `v2.8.0` | **Base URL** : `http://localhost:8000`

## ⚠️ Note importante

Ce document mélange historique et spécifications futures. La source de vérité runtime est l'application FastAPI principale dans `app/main.py`.

### Endpoints actuellement disponibles (runtime local)

- `GET /`
- `GET /health`
- `GET /status`
- `GET /metrics`
- `POST /zeroia/decision` (endpoint de compatibilité minimal)
- routes montées via routers :
  - préfixe `/assistantia`
  - préfixe `/reflexia`

Les routes `/api/v1/zeroia/...` décrites plus bas doivent être considérées comme **planifiées / non garanties en production** tant qu'elles ne sont pas exposées explicitement dans le runtime principal.

---

## Nouveautés Enhanced v2.8.0

### Endpoints Framework Enhanced

#### Orchestrator Enhanced
- `GET /api/v1/zeroia/orchestrator/status` - Status Orchestrator Enhanced
- `POST /api/v1/zeroia/orchestrator/run` - Exécution boucle Enhanced
- `GET /api/v1/zeroia/orchestrator/metrics` - Métriques performance

#### Circuit Breaker
- `GET /api/v1/zeroia/circuit-breaker/status` - État circuit breaker
- `POST /api/v1/zeroia/circuit-breaker/reset` - Reset circuit breaker
- `GET /api/v1/zeroia/circuit-breaker/metrics` - Métriques protection

#### Event Store Enhanced
- `GET /api/v1/zeroia/events` - Liste événements récents
- `POST /api/v1/zeroia/events` - Ajout nouvel événement
- `GET /api/v1/zeroia/events/analytics` - Analytics Event Store
- `GET /api/v1/zeroia/events/recovery-status` - Status auto-recovery

#### Error Recovery
- `GET /api/v1/zeroia/error-recovery/status` - Status Error Recovery
- `POST /api/v1/zeroia/error-recovery/test` - Test récupération
- `GET /api/v1/zeroia/graceful-degradation/status` - Status degradation

---

## ZeroIA Enhanced API

### Orchestrator Enhanced

#### `GET /api/v1/zeroia/orchestrator/status`
Status détaillé de l'Orchestrator Enhanced.

**Response** :
```json
{
  "status": "operational",
  "version": "enhanced-v2.8.0",
  "current_state": "idle",
  "last_execution": {
    "timestamp": "2024-12-29T20:51:00Z",
    "loops_completed": 5,
    "success_rate": 100.0,
    "duration_seconds": 1.7,
    "failures": 0
  },
  "circuit_breaker": {
    "state": "CLOSED",
    "failure_count": 0,
    "last_failure": null
  },
  "event_store": {
    "total_events": 11,
    "cache_status": "healthy",
    "auto_recovery_active": true
  }
}
```

#### `POST /api/v1/zeroia/orchestrator/run`
Exécution de la boucle Orchestrator Enhanced.

**Request** :
```json
{
  "max_loops": 5,
  "interval_seconds": 0.3,
  "mode": "quick"
}
```

**Response** :
```json
{
  "execution_id": "exec_20241229_205100",
  "status": "completed",
  "results": {
    "loops_executed": 5,
    "success_rate": 100.0,
    "duration_seconds": 1.7,
    "decisions_made": 5,
    "events_created": 11,
    "circuit_breaker_openings": 0
  },
  "performance": {
    "avg_loop_time": 0.34,
    "min_loop_time": 0.31,
    "max_loop_time": 0.38
  }
}
```

### Circuit Breaker API

#### `GET /api/v1/zeroia/circuit-breaker/status`
État détaillé du Circuit Breaker.

**Response** :
```json
{
  "state": "CLOSED",
  "failure_count": 0,
  "failure_threshold": 5,
  "timeout_seconds": 60,
  "success_threshold": 3,
  "last_failure_time": null,
  "last_success_time": "2024-12-29T20:51:00Z",
  "total_requests": 156,
  "successful_requests": 156,
  "failed_requests": 0,
  "success_rate": 100.0
}
```

### Event Store Enhanced API

#### `GET /api/v1/zeroia/events`
Liste des événements récents avec auto-recovery.

**Query Parameters** :
- `limit` : Nombre d'événements (défaut: 10)
- `event_type` : Filtrage par type d'événement

**Response** :
```json
{
  "events": [
    {
      "id": "evt_20241229_205100_001",
      "timestamp": "2024-12-29T20:51:00Z",
      "event_type": "DECISION_MADE",
      "data": {
        "decision": "normal",
        "confidence": 0.8,
        "reasoning": "System stable, no anomalies detected"
      },
      "metadata": {
        "source": "orchestrator_enhanced",
        "execution_id": "exec_20241229_205100"
      }
    }
  ],
  "total_count": 11,
  "cache_status": "healthy",
  "auto_recovery": {
    "enabled": true,
    "last_recovery": null,
    "recovery_count": 0
  }
}
```

#### `GET /api/v1/zeroia/events/analytics`
Analytics avancées de l'Event Store.

**Response** :
```json
{
  "summary": {
    "total_events": 11,
    "events_last_hour": 11,
    "events_last_24h": 11,
    "cache_size_mb": 0.049
  },
  "event_types": {
    "DECISION_MADE": 5,
    "SYSTEM_HEALTHY": 3,
    "CIRCUIT_BREAKER_CLOSED": 2,
    "ERROR_RECOVERY_SUCCESS": 1
  },
  "performance": {
    "avg_write_time_ms": 2.3,
    "avg_read_time_ms": 1.1,
    "cache_hit_rate": 0.85
  },
  "health": {
    "status": "excellent",
    "cache_corruption_count": 0,
    "auto_recovery_count": 0,
    "last_health_check": "2024-12-29T20:51:00Z"
  }
}
```

### Error Recovery API

#### `GET /api/v1/zeroia/error-recovery/status`
Status complet du système Error Recovery.

**Response** :
```json
{
  "status": "operational",
  "version": "enhanced-v2.7.1",
  "recovery_systems": {
    "sqlite_corruption": {
      "enabled": true,
      "status": "monitoring",
      "recoveries_performed": 0,
      "last_recovery": null
    },
    "cache_corruption": {
      "enabled": true,
      "status": "monitoring",
      "auto_cleanup": true,
      "cleanups_performed": 0
    },
    "typing_errors": {
      "enabled": true,
      "status": "resolved",
      "errors_fixed": 14,
      "last_fix": "2024-12-29T20:45:00Z"
    }
  },
  "graceful_degradation": {
    "enabled": true,
    "services_count": 15,
    "priority_levels": 5,
    "degraded_services": 0
  }
}
```

#### `GET /api/v1/zeroia/graceful-degradation/status`
Status détaillé du Graceful Degradation.

**Response** :
```json
{
  "status": "nominal",
  "services": {
    "critical": {
      "count": 3,
      "operational": 3,
      "services": ["system_monitoring", "error_recovery", "circuit_breaker"]
    },
    "high": {
      "count": 3,
      "operational": 3,
      "services": ["zeroia_core", "reflexia_core", "event_sourcing"]
    },
    "medium": {
      "count": 3,
      "operational": 3,
      "services": ["sandozia_intelligence", "assistantia_api", "prometheus_metrics"]
    },
    "low": {
      "count": 3,
      "operational": 3,
      "services": ["advanced_analytics", "ui_enhancements", "caching_layer"]
    },
    "optional": {
      "count": 3,
      "operational": 3,
      "services": ["debug_tools", "dev_utilities", "performance_profiling"]
    }
  },
  "degradation_level": "none",
  "last_degradation": null,
  "recovery_time_estimate": null
}
```

---

## Sandozia Intelligence API

### CrossModule Validation

#### `GET /api/v1/sandozia/validation/status`
Status validation croisée inter-modules.

**Response** :
```json
{
  "global_coherence_score": 0.98,
  "validations_performed": 156,
  "contradictions_detected": 0,
  "last_validation": "2024-12-29T20:51:00Z",
  "module_coherence": {
    "reflexia_zeroia": 0.99,
    "assistantia_sandozia": 0.97,
    "global_state_sync": 0.98
  }
}
```

### Behavior Analysis

#### `GET /api/v1/sandozia/behavior/analysis`
Analyse comportementale avancée.

**Response** :
```json
{
  "behavioral_health_score": 0.94,
  "anomalies_detected": 0,
  "patterns_analyzed": 45,
  "statistical_analysis": {
    "z_score_threshold": 2.0,
    "outliers_detected": 0,
    "trend_analysis": "stable"
  }
}
```

---

## Reflexia Decision API

### Decision Engine

#### `POST /api/v1/reflexia/decision`
Demande de décision au moteur Reflexia.

**Request** :
```json
{
  "context": {
    "system_status": "normal",
    "load": 0.45,
    "memory_usage": 0.62
  },
  "priority": "high",
  "timeout_seconds": 5
}
```

**Response** :
```json
{
  "decision": "monitor",
  "confidence": 0.85,
  "reasoning": "System metrics within normal range",
  "execution_time_ms": 234,
  "recommendations": [
    "Continue monitoring",
    "No immediate action required"
  ]
}
```

---

## AssistantIA Conversation API

### Chat Interface

#### `POST /api/v1/assistantia/chat`
Interface de conversation avec l'assistant IA.

**Request** :
```json
{
  "message": "Comment va le système Arkalia ?",
  "conversation_id": "conv_20241229_205100",
  "model": "llama3.2",
  "context": {
    "include_system_status": true,
    "include_metrics": true
  }
}
```

**Response** :
```json
{
  "response": "Le système Arkalia-LUNA Pro Enhanced v2.8.0 fonctionne correctement ! 🚀\n\n✅ Orchestrator Enhanced : Opérationnel\n✅ Tests : 671 tests collectés\n✅ Circuit Breaker : État fermé stable\n✅ Event Store : Auto-recovery opérationnel\n\nLes modules sont opérationnels et les performances sont bonnes.",
  "conversation_id": "conv_20241229_205100",
  "timestamp": "2024-12-29T20:51:00Z",
  "model_used": "llama3.2",
  "processing_time_ms": 1247,
  "system_context": {
    "orchestrator_status": "operational",
    "test_success_rate": 100.0,
    "circuit_breaker_state": "CLOSED"
  }
}
```

---

## Monitoring & Metrics API

### Global Health Check

#### `GET /api/v1/health`
Health check global du système Enhanced.

**Response** :
```json
{
  "status": "healthy",
  "version": "enhanced-v2.8.0",
  "timestamp": "2024-12-29T20:51:00Z",
  "components": {
    "orchestrator_enhanced": "operational",
    "circuit_breaker": "closed",
    "event_store": "healthy",
    "error_recovery": "monitoring",
    "graceful_degradation": "nominal",
    "sandozia_intelligence": "excellent",
    "reflexia_engine": "operational",
    "assistantia": "ready",
    "api_gateway": "healthy"
  },
  "metrics": {
    "uptime_seconds": 172800,
    "total_requests": 15647,
    "success_rate": 99.98,
    "avg_response_time_ms": 145,
    "test_success_rate": 100.0
  }
}
```

### Performance Metrics

#### `GET /api/v1/metrics/performance`
Métriques de performance détaillées.

**Response** :
```json
{
  "orchestrator_enhanced": {
    "total_executions": 234,
    "success_rate": 100.0,
    "avg_execution_time": 1.7,
    "last_24h_executions": 45
  },
  "circuit_breaker": {
    "total_requests": 15647,
    "failed_requests": 0,
    "success_rate": 100.0,
    "state_changes": 0
  },
  "event_store": {
    "total_events": 1247,
    "events_per_hour": 52,
    "cache_hit_rate": 0.85,
    "auto_recoveries": 0
  },
  "api_performance": {
    "requests_per_minute": 234,
    "avg_response_time": 145,
    "p95_response_time": 287,
    "p99_response_time": 456
  }
}
```

---

## Authentication & Security

### API Key Authentication

Toutes les requêtes API Enhanced nécessitent une authentification :

```bash
# Header requis
X-API-Key: <api_key>

# Exemple avec curl
API_KEY="<api_key>"
curl -H "X-API-Key: $API_KEY" \
     http://localhost:8000/api/v1/zeroia/orchestrator/status
```

### Rate Limiting

- **Standard** : 1000 req/min
- **Enhanced** : 5000 req/min
- **Monitoring** : 10000 req/min

---

## Exemples d'Utilisation

### Test Complet Enhanced

```bash
# Status global
curl http://localhost:8000/api/v1/health

# Exécution Orchestrator Enhanced
curl -X POST http://localhost:8000/api/v1/zeroia/orchestrator/run \
  -H "Content-Type: application/json" \
  -d '{"max_loops": 5, "mode": "quick"}'

# Vérification Circuit Breaker
curl http://localhost:8000/api/v1/zeroia/circuit-breaker/status

# Analytics Event Store
curl http://localhost:8000/api/v1/zeroia/events/analytics
```

### Intelligence Croisée

```bash
# Validation cross-module
curl http://localhost:8000/api/v1/sandozia/validation/status

# Analyse comportementale
curl http://localhost:8000/api/v1/sandozia/behavior/analysis

# Conversation avec AssistantIA
curl -X POST http://localhost:8001/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Status du système Enhanced ?", "include_metrics": true}'
```

---

## Documentation Interactive

### OpenAPI/Swagger

Documentation interactive disponible :
- **Swagger UI** : `http://localhost:8000/docs`
- **ReDoc** : `http://localhost:8000/redoc`
- **OpenAPI JSON** : `http://localhost:8000/openapi.json`

### Liens Utiles

- **API Locale** : `http://localhost:8000`
- **Health Check** : `http://localhost:8000/api/v1/health`
- **Métriques** : `http://localhost:8000/api/v1/metrics/performance`
- **Documentation** : `http://localhost:8000/docs`

---

## Métriques de Performance Actuelles

| Métrique | Valeur | Statut |
|----------|--------|--------|
| **Tests collectés** | 671 | ✅ |
| **Couverture** | 59.25% | ✅ >28% |
| **Temps CI** | 31.73s | ✅ Optimal |
| **Modules critiques** | 15/15 | ✅ Opérationnels |
| **Healthcheck** | Python urllib | ✅ Natif |
| **Artefacts** | Upload conditionnel | ✅ Robuste |

---

## Conclusion

L'API Arkalia-LUNA Pro Enhanced v2.8.0 offre :

- Framework Enhanced - Orchestrator, Circuit Breaker, Event Store
- Error Recovery - Gestion gracieuse des erreurs
- Intelligence Croisée - Validation et consensus multi-modules
- Performance - Tests automatisés, orchestrator opérationnel
- Documentation Complète - OpenAPI/Swagger intégré

*Dernière mise à jour : novembre 2025*

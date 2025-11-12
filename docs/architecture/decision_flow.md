# Flux Décisionnel ZeroIA - Arkalia-LUNA Pro

## 📊 **ÉTAT ACTUEL DU SYSTÈME (Mise à jour novembre 2025)**

### ✅ **SUCCÈS MAJEUR - CI/CD 100% Verte !**
- **671 tests passés** (642 unitaires + 29 intégration) ✅
- **Couverture : 59.25%** (bien au-dessus du seuil de 28%) ✅
- **Temps d'exécution : 31.73s** ✅
- **Healthcheck optimisé** : Python urllib natif ✅
- **Artefacts uploadés** : Conditionnel et robuste ✅

```mermaid
flowchart TD
    A[🔄 Context Input] --> B{📊 Load Context}
    B --> C[🧠 ZeroIA Reasoning]
    C --> D{🔍 CPU Analysis}
    C --> E{💾 RAM Analysis}
    C --> F{⚡ System Health}

    D --> |CPU > 80%| G[🚨 High Load Detected]
    D --> |CPU 60-80%| H[⚠️ Medium Load]
    D --> |CPU < 60%| I[✅ Normal Load]

    E --> |RAM > 85%| J[💥 Memory Critical]
    E --> |RAM 70-85%| K[⚠️ Memory Warning]
    E --> |RAM < 70%| L[✅ Memory OK]

    F --> M{🔗 Reflexia Check}
    M --> |Consistent| N[🎯 Decision Confidence HIGH]
    M --> |Inconsistent| O[⚠️ Decision Confidence LOW]

    G --> P[🛑 Emergency Shutdown]
    H --> Q[📉 Reduce Load]
    I --> R[👁️ Monitor]

    J --> P
    K --> Q
    L --> R

    P --> S[💾 Persist State]
    Q --> S
    R --> S

    S --> T[📈 Update Dashboard]
    T --> U[🔄 Loop Continue]

    N --> V[🧠 Confidence Score: 0.8-1.0]
    O --> W[🧠 Confidence Score: 0.3-0.7]

    V --> X[✅ Execute Decision]
    W --> Y[⚠️ Flag for Review]

    X --> S
    Y --> S

    subgraph "🔒 Security Layer"
        Z1[🛡️ Model Integrity Check]
        Z2[🔍 Poisoning Detection]
        Z3[📝 Audit Log]
    end

    C --> Z1
    Z1 --> Z2
    Z2 --> Z3
    Z3 --> D

    subgraph "📊 Observability"
        M1[📉 Prometheus Metrics]
        M2[📈 Grafana Dashboard]
        M3[🚨 AlertManager]
    end

    T --> M1
    M1 --> M2
    M2 --> M3
```

## Légende des Décisions

| Décision | Déclencheur | Seuils | Action |
|----------|-------------|---------|---------|
| `emergency_shutdown` | CPU > 80% OU RAM > 85% | Critique | Arrêt services non-essentiels |
| `reduce_load` | CPU 60-80% OU RAM 70-85% | Warning | Limitation connexions |
| `monitor` | CPU < 60% ET RAM < 70% | Normal | Surveillance continue |

## Facteurs de Confiance

- **Cohérence système** : CPU/RAM/Disk corrélés
- **Historique Reflexia** : Décisions passées similaires
- **Temps de réponse** : < 500ms = confiance élevée
- **Contexte** : Similarité avec patterns connus
- **Taux d'erreur** : Historique de succès/échecs

## 🏗️ Architecture Modulaire Actuelle

```mermaid
graph TD
    subgraph "🎯 Core Modules"
        ZeroIA["🤖 ZeroIA<br/>Decision Engine<br/>/cycle, /status"] --> |"Patterns"| Sandozia["🔍 Sandozia<br/>Pattern Analysis<br/>/metric, /pattern"]
        Sandozia --> |"Signals"| CognitiveReactor["🧠 CognitiveReactor<br/>Logic Fusion<br/>/signal, /decision"]
        CognitiveReactor --> |"Validation"| CrossValidator["🔍 CrossModuleValidator<br/>Inter-module Check<br/>/validate, /register"]
        CrossValidator --> |"Evaluation"| Reflexia["🔄 Reflexia<br/>Self-reflection<br/>/evaluate, /snapshot"]
        Reflexia --> |"Recovery"| ErrorRecovery["💫 Error Recovery<br/>Auto-healing<br/>/error, /recover"]
        ErrorRecovery --> |"History"| Chronalia["📊 Chronalia<br/>Timeline<br/>/timeline, /history"]
    end

    subgraph "🛡️ Security Layer"
        VaultManager["🔐 VaultManager<br/>Security Manager<br/>/integrity, /vault"]
        AssistantIA["🤖 AssistantIA<br/>UI/UX Interface<br/>/ask, /explain, /chat"]
        Helloria["🌐 Helloria<br/>Central API<br/>/api, /health"]
    end

    subgraph "📊 Monitoring Stack"
        Prometheus["📈 Prometheus<br/>Metrics Collection<br/>/metrics"]
        Grafana["📊 Grafana<br/>Visualization<br/>Port 3000"]
        AlertManager["🚨 AlertManager<br/>Alert Management<br/>Port 9093"]
        Loki["📝 Loki<br/>Log Aggregation<br/>Port 3100"]
        Promtail["📡 Promtail<br/>Log Collection"]
    end

    subgraph "🔧 Infrastructure"
        NGINX["🌐 NGINX<br/>API Gateway<br/>Port 80/443"]
        Docker["🐳 Docker<br/>Containerization"]
        Volumes["💾 Volumes<br/>/logs, /cache, /state"]
    end

    ZeroIA --> VaultManager
    Sandozia --> VaultManager
    CognitiveReactor --> AssistantIA
    CrossValidator --> Helloria
    Reflexia --> Prometheus
    ErrorRecovery --> AlertManager
    Chronalia --> Loki

    VaultManager --> NGINX
    AssistantIA --> NGINX
    Helloria --> NGINX

    Prometheus --> Grafana
    AlertManager --> Grafana
    Loki --> Grafana
    Promtail --> Loki

    NGINX --> Docker
    Docker --> Volumes
```

## 🎯 **Métriques de Performance Actuelles**

| Métrique | Valeur | Statut |
|----------|--------|--------|
| **Tests collectés** | 671 | ✅ |
| **Couverture** | 59.25% | ✅ >28% |
| **Temps CI** | 31.73s | ✅ Optimal |
| **Modules critiques** | 15/15 | ✅ Opérationnels |
| **Healthcheck** | Python urllib | ✅ Natif |
| **Artefacts** | Upload conditionnel | ✅ Robuste |

---

*Dernière mise à jour : novembre 2025
*Prochaine révision : 28 novembre 2025 - 09:00*

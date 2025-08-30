# 🧠 ZeroIA - Module de Décision Autonome

## 📋 Description
ZeroIA est le module de prise de décision autonome d'Arkalia-LUNA. Il utilise des algorithmes d'IA avancés pour prendre des décisions intelligentes en temps réel.

## 🚀 Fonctionnalités
- ✅ **Circuit Breaker** : Protection contre les surcharges
- ✅ **Error Recovery** : Récupération automatique d'erreurs
- ✅ **Graceful Degradation** : Dégradation gracieuse en cas de problème
- ✅ **Event Store** : Stockage et traçabilité des événements
- ✅ **Adaptive Thresholds** : Seuils adaptatifs
- ✅ **Métriques Prometheus** : Observabilité complète

## 🔧 Utilisation

### Initialisation
```python
from modules.zeroia.metrics import init_zeroia_metrics

# Initialiser les métriques
init_zeroia_metrics()
```

### Mise à jour des métriques
```python
from modules.zeroia.metrics import update_zeroia_metrics

# Mettre à jour les métriques
update_zeroia_metrics("decision_type", "success", 0.5, cognitive_score=0.85)
```

### Boucle de raisonnement
```python
from modules.zeroia.reason_loop_enhanced import reason_loop_enhanced

# Lancer la boucle de raisonnement
reason_loop_enhanced()
```

## 📊 Métriques Disponibles
- `zeroia_decisions_total` : Nombre total de décisions
- `zeroia_circuit_breaker_state` : État du circuit breaker
- `zeroia_error_recovery_attempts` : Tentatives de récupération
- `arkalia_cognitive_score` : Score cognitif du module

## 🧪 Tests
```bash
# Tests de performance
pytest tests/performance/test_zeroia_performance.py -v

# Tests unitaires
pytest tests/unit/zeroia/ -v

# Tests d'intégration
pytest tests/integration/test_zeroia_api.py -v
```

## 📁 Structure
```
modules/zeroia/
├── core.py                    # Logique principale
├── reason_loop_enhanced.py    # Boucle de raisonnement
├── circuit_breaker.py         # Circuit breaker pattern
├── error_recovery_system.py   # Système de récupération
├── graceful_degradation.py    # Dégradation gracieuse
├── event_store.py            # Stockage d'événements
├── metrics.py                # Métriques Prometheus
└── README.md                 # Ce fichier
```

## 🎯 Performance
- **Temps de décision** : < 1 seconde
- **Uptime** : 99.9%
- **Score cognitif** : 0.85/1.0
- **Tests de couverture** : 76%

## 🔗 Intégration
ZeroIA s'intègre avec tous les autres modules Arkalia-LUNA :
- **Reflexia** : Pour l'observation
- **Sandozia** : Pour l'intelligence croisée
- **Security** : Pour la sécurité
- **Monitoring** : Pour l'observabilité

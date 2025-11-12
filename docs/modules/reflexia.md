# Reflexia — Observateur cognitif réflexif Enhanced v2.8.0

Reflexia est le module de monitoring cognitif du kernel Arkalia-LUNA. Il fonctionne en mode API HTTP (port 8002) et prend en charge :

- Le monitoring avancé des ressources (CPU, RAM, latence)
- La synchronisation et la validation des décisions ZeroIA
- L'exposition d'un endpoint /metrics compatible Prometheus
- La détection des containers instables
- L'analyse comportementale des décisions
- La détection de contradictions avec ZeroIA
- Les métriques Prometheus intégrées

**Entrée/Sortie :**
- Dialogue avec ZeroIA et Sandozia
- Expose une API HTTP (GET /metrics, GET /health)
- 8 métriques Prometheus exposées
- Couverture tests : 74% (bon)

**Cas d'usage :**
- Supervision temps réel
- Détection d'anomalies
- Intégration Prometheus/Grafana
- Analyse comportementale
- Validation des décisions

**API HTTP publique** : http://localhost:8002/metrics

**Statut actuel** : ✅ Opérationnel avec Enhanced v2.8.0

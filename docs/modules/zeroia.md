# ZeroIA — Moteur de Décision Autonome Enhanced v2.6.0

ZeroIA est le module de décision autonome du kernel Arkalia-LUNA. Il fonctionne en mode daemon (pas d'API HTTP publique) et prend en charge :

- La prise de décision automatique (monitoring, réduction de charge, emergency shutdown)
- Le circuit breaker (protection contre les boucles d'échec)
- L'auto-récupération (error recovery) avec Error Recovery System v2.7.0
- L'intégrité du contexte et la cohérence des décisions
- Graceful Degradation avec services classés par priorité
- Adaptive Thresholds pour ajustement automatique des seuils
- Event Sourcing pour traçabilité complète

**Entrée/Sortie :**

- Interagit avec Reflexia et Sandozia via fichiers d'état et events
- Expose ses métriques via arkalia-api (port 8000) (pas directement)
- 12 métriques Prometheus exposées
- Couverture tests : 87% (excellent)

**Cas d'usage :**

- Surveillance continue
- Protection adaptative
- Décision rapide en cas d'anomalie
- Récupération automatique d'erreurs
- Dégradation gracieuse des services

**Pas d'API HTTP publique** : toute interaction passe par arkalia-api (port 8000) ou les fichiers d'état internes.

**Statut actuel** : ✅ Opérationnel avec Error Recovery System v2.7.0

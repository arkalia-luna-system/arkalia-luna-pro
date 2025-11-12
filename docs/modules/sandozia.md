# Sandozia — Intelligence croisée v2.8.0

Sandozia est le module d'intelligence croisée du kernel Arkalia-LUNA. Il fonctionne en mode daemon (pas d'API HTTP publique) et prend en charge :

- L'analyse avancée des états et décisions
- La validation de la cohérence inter-modules (ZeroIA, Reflexia)
- Le support à la prise de décision
- L'intelligence collaborative entre modules
- L'analyse comportementale avancée
- La validation croisée des décisions
- Les heatmaps cognitives et patterns détectés

**Entrée/Sortie :**
- Dialogue via fichiers d'état et events
- Expose ses métriques via arkalia-api (port 8000) (pas directement)
- 6 métriques Prometheus exposées
- Couverture tests : 92% (excellent)

**Cas d'usage :**
- Analyse croisée
- Détection de divergences
- Support décisionnel
- Intelligence collaborative
- Analyse comportementale avancée

**Pas d'API HTTP publique** : toute interaction passe par arkalia-api (port 8000) ou les fichiers d'état internes.

**Statut actuel** : Opérationnel avec v2.8.0

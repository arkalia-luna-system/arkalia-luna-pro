# Security Policy

## Supported Versions

Les branches supportées pour les correctifs de sécurité sont :

- `main`
- `develop`

## Reporting a Vulnerability

Pour signaler une vulnérabilité :

1. N'ouvrez pas d'issue publique.
2. Envoyez un rapport détaillé à `arkalia.luna.system@gmail.com`.
3. Incluez les étapes de reproduction, l'impact estimé et une proposition de mitigation si possible.

Objectifs de traitement :

- Accusé de réception sous 72h
- Qualification initiale sous 7 jours
- Correctif ou plan de remédiation priorisé selon la sévérité

## Security Controls in Repository

Ce dépôt active :

- scan SAST (CodeQL)
- scan de secrets (Gitleaks)
- scans dépendances (Dependabot, `pip-audit`, `safety`)
- scan statique Python (`bandit`)

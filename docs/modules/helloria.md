# Helloria — API Centrale FastAPI

Helloria est le module central de coordination cognitive de l'application Arkalia-LUNA. Il gère les interactions de base avec l'API et orchestre les requêtes entrantes et sortantes.

## Objectif du Module
Helloria sert de point central pour la coordination des tâches cognitives au sein du système Arkalia-LUNA avec FastAPI optimisé.

## Fonctionnalités
- API REST complète avec FastAPI
- Gestion des requêtes optimisée
- Documentation automatique (Swagger)
- Métriques Prometheus intégrées (34 métriques)
- Health endpoints automatiques (vérification Python urllib)
- Performance < 500ms

## Exemple de Requête
```python
import requests

response = requests.get("http://localhost:8000/")
print(response.json())
```

## Routes Exposées
- `GET /`: Retourne un message de bienvenue.
- `GET /status`: Retourne le statut opérationnel de Helloria.
- `GET /health`: Healthcheck optimisé avec Python urllib.
- `GET /metrics`: Métriques Prometheus (34 exposées).
- `GET /docs`: Documentation Swagger automatique.

## Métriques et Monitoring
- **34 métriques Prometheus** exposées
- **Healthcheck Python natif** (urllib.request)
- **Performance** < 500ms
- **Couverture tests** : 59.25% (global)

## Documentation Générale
Pour plus de détails, consultez la [documentation générale](https://arkalia-luna-system.github.io/arkalia-luna-pro/).

**Statut actuel** : ✅ Opérationnel avec FastAPI optimisé

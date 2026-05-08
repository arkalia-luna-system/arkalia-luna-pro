# Endpoints API Arkalia-LUNA Pro

## Vue d'ensemble

Cette page documente tous les endpoints API disponibles dans Arkalia-LUNA Pro v2.8.0.

## API Principale (Helloria)

### Base URL

```text
http://localhost:8000
```

### Endpoints Principaux

#### GET / - Page d'accueil

```http
GET /
```

**Description** : Page d'accueil de l'API
**Réponse** : HTML de la page d'accueil

#### GET /health - Health Check

```http
GET /health
```

**Description** : Vérification de l'état de santé
**Réponse** :

```json
{
  "status": "ok",
  "service": "arkalia-api"
}
```

#### GET /status - Statut détaillé

```http
GET /status
```

**Description** : Statut détaillé de tous les modules
**Réponse** :

```json
{
  "overall_status": "good",
  "components": {
    "arkalia_api (port 8000)": "healthy",
    "zeroia": "healthy",
    "reflexia": "healthy",
    "sandozia": "healthy",
    "cognitive_reactor": "healthy",
    "assistantia": "healthy"
  },
  "metrics": {
    "total_requests": 1234,
    "active_connections": 5,
    "uptime": "2d 5h 30m"
  }
}
```

#### GET /metrics - Métriques Prometheus

```http
GET /metrics
```

**Description** : Métriques au format Prometheus
**Réponse** : Métriques au format Prometheus

---

## ZeroIA - Moteur de Décision Autonome

### **Base URL ZeroIA**

```text
http://localhost:8000
```

### **Endpoints ZeroIA**

#### **POST /chat** - Interface de chat avec l'IA

**Endpoint** : `POST /chat`

**Description** : Interface de chat avec l'IA pour la prise de décision et l'assistance

**Port** : 8000 (Helloria) ou 8001 (AssistantIA)

#### **Note ZeroIA**

Le runtime principal expose actuellement un endpoint de compatibilité :

```http
POST /zeroia/decision
```

`/zeroia/status` n'est pas exposé par `app/main.py`.

#### **POST /zeroia/decision** - Prise de décision

```http
POST /zeroia/decision
Content-Type: application/json

{
  "context": {},
  "priority": "high"
}
```

**Description** : Demande une décision au moteur ZeroIA

---

## Reflexia - Observateur Cognitif

### **Base URL Reflexia**

```text
http://localhost:8002
```

### **Endpoints Reflexia**

#### **GET /reflexia/check** - Vérification réflexive

```http
GET /reflexia/check
```

**Description** : Retourne l'état des métriques système (CPU, RAM, latence)

**Réponse** :

```json
{
  "status": "ok",
  "metrics": {
    "cpu": 45.2,
    "ram": 67.8,
    "latency": 120.5
  }
}
```

#### **GET /reflexia/metrics** - Métriques Prometheus

```http
GET /reflexia/metrics
```

**Description** : Métriques au format Prometheus pour Reflexia

#### **GET /health** - Health Check Reflexia (service standalone)

```http
GET /health
```

**Description** : Vérification de l'état de santé de Reflexia sur le service standalone (port 8002).

Via l'API principale (port 8000), utiliser les routes montées sous `/reflexia` (ex: `/reflexia/check`, `/reflexia/metrics`).

---

## Sandozia - Intelligence Croisée

### **Note importante**

Sandozia fonctionne en mode **daemon** (pas d'API HTTP publique directe). Toute interaction passe par `arkalia-api` (port 8000) ou les fichiers d'état internes.

### **Accès via arkalia-api**

Les métriques et fonctionnalités de Sandozia sont accessibles via l'API centrale :

```http
GET http://localhost:8000/sandozia/health
```

**Réponse** :

```json
{
  "status": "active",
  "module": "sandozia"
}
```

### **Métriques**

Les métriques Sandozia sont exposées via Prometheus via `arkalia-api` :

```http
GET http://localhost:8000/metrics
```

---

## AssistantIA - Assistant IA

### **Base URL AssistantIA**

```text
http://localhost:8001
```

### **Endpoints AssistantIA**

#### **POST /api/v1/chat** - Conversation IA

```http
POST /api/v1/chat
Content-Type: application/json

{
  "message": "string",
  "model": "mistral:latest",
  "temperature": 0.7,
  "include_context": true
}
```

**Note** : AssistantIA utilise le prefix `/api/v1` sur le port 8001.

**Réponse** :

```json
{
  "response": "string",
  "confidence": 0.9,
  "suggestions": ["suggestion1", "suggestion2"],
  "timestamp": "2025-06-30T21:10:00Z"
}
```

#### **POST /chat** - Validation de prompt (intégrée)

La validation de prompt est intégrée dans l'endpoint `/chat` via le module de sécurité.

**Réponse** :

```json
{
  "valid": true,
  "risk_level": "low",
  "warnings": [],
  "timestamp": "2025-06-30T21:10:00Z"
}
```

---

## Monitoring - Métriques

### **Prometheus**

```text
http://localhost:9090/metrics
```

### **Grafana**

```text
http://localhost:3000
```

### **AlertManager**

```text
http://localhost:9093
```

### **Loki (Logs)**

```text
http://localhost:3100
```

---

## Sécurité

### **Authentification**

Tous les endpoints sensibles nécessitent une authentification via header :

```http
X-API-Key: <api_key>
```

### **Rate Limiting**

- **Limite** : 1000 requêtes par minute par IP
- **Headers** : `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`

### **CORS**

```http
Access-Control-Allow-Origin: http://localhost:5173
Access-Control-Allow-Methods: GET, POST, PUT, DELETE
Access-Control-Allow-Headers: Content-Type, X-API-Key
```

---

## Codes de Réponse

| Code | Description |
|------|-------------|
| 200 | Succès |
| 201 | Créé |
| 400 | Requête invalide |
| 401 | Non autorisé |
| 403 | Interdit |
| 404 | Non trouvé |
| 429 | Trop de requêtes |
| 500 | Erreur serveur |

---

## Exemples d'Utilisation

### **cURL - Health Check**

```bash
curl -X GET http://localhost:8000/health
```

### **cURL - Décision ZeroIA**

```bash
curl -X POST http://localhost:8000/zeroia/decision \
  -H "Content-Type: application/json" \
  -d '{
    "context": "High CPU usage detected",
    "options": ["scale_up", "optimize", "ignore"],
    "confidence_threshold": 0.8
  }'
```

### **cURL - Chat AssistantIA**

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Analysez cette situation et prenez une décision"}'
```

---

## Documentation Complète

- [API Documentation](api.md)
- [Métriques](metrics.md)
- [Configuration](../infrastructure/devops/index.md)

---

**Arkalia-LUNA Pro v2.8.0** - Documentation des endpoints API
**Dernière mise à jour : novembre 2025**

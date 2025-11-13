# 🚀 Démarrage Rapide

> Guide pour démarrer avec Arkalia-LUNA Pro en quelques minutes.

---

## 📦 Installation

### Prérequis

- Python 3.11 ou plus récent
- Docker et Docker Compose
- Git

### Démarrage

```bash
# 1. Cloner le projet
git clone https://github.com/arkalia-luna-system/arkalia-luna-pro.git
cd arkalia-luna-pro

# 2. Démarrer tous les services
docker-compose up -d

# 3. Vérifier que tout fonctionne
curl http://localhost:8000/health
```

---

## 🔗 Accès aux Services

Une fois démarré, accédez aux services :

| Service | URL | Description |
|---------|-----|-------------|
| **API principale** | http://localhost:8000 | API centrale |
| **Grafana** | http://localhost:3000 | Tableaux de bord |
| **Prometheus** | http://localhost:9090 | Métriques système |
| **Documentation API** | http://localhost:8000/docs | Documentation interactive |

> 💡 **Identifiants Grafana** : `admin` / `arkalia-secure-2025`

---

## 🎯 Premiers Pas

### Tester l'API

```bash
# Vérifier l'état du système
curl http://localhost:8000/status

# Envoyer un message à l'IA
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Bonjour"}'
```

### Lancer les Tests

```bash
# Tests complets
pytest tests/ -v

# Tests rapides
pytest tests/unit/ -v
```

---

## 🔧 Problèmes Courants

### Port déjà utilisé

```bash
# Trouver le processus
lsof -i :8000

# Arrêter le processus
kill -9 <PID>
```

### Redémarrer les services

```bash
# Arrêter et redémarrer
docker-compose down
docker-compose up -d
```

### Vérifier les logs

```bash
# Logs de tous les services
docker-compose logs

# Logs d'un service spécifique
docker-compose logs arkalia-api
```

---

## 📚 Prochaines Étapes

1. **Explorer les modules** : [Documentation des modules](../modules/zeroia.md)
2. **Utiliser l'API** : [Guide d'utilisation](../architecture/fonctionnement/utilisation.md)
3. **Comprendre l'architecture** : [Architecture du système](../architecture/overview.md)
4. **Contribuer** : [Guide de contribution](../credits/CONTRIBUTING.md)

---

<div align="right">

*Dernière mise à jour : novembre 2025*

</div>

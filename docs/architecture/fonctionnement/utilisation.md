# 📖 Utilisation d'Arkalia-LUNA Pro

> Guide complet pour utiliser Arkalia-LUNA Pro : dialoguer avec l'IA, surveiller le système et utiliser les fonctionnalités principales.

---

## 🚀 Démarrer le système

### Avec Docker (recommandé)

```bash
docker-compose up -d
```

### En local

```bash
uvicorn modules.helloria.core:app --reload
```

---

## 🌐 Utiliser l'API

### Vérifier l'état du système

```bash
curl http://localhost:8000/status
```

**Réponse** :

```json
{
  "status": "online",
  "modules": ["ZeroIA", "Reflexia", "Sandozia", "AssistantIA", "Security"],
  "containers": "healthy"
}
```

### Envoyer un message à l'IA

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Bonjour, comment ça va ?"}'
```

**Réponse** :

```json
{
  "response": "Bonjour ! Je vais bien, merci."
}
```

> 💡 **Note** : L'IA utilise Ollama en local (modèle mistral par défaut).

---

## 🔐 Sécurité

- Authentification par token (header `X-API-Token`)
- Monitoring avec Prometheus et Grafana
- Logs centralisés
- Audit de sécurité automatique

---

## 📚 Documentation API

Pour voir tous les endpoints disponibles et tester l'API interactivement :

- **Documentation interactive** : http://localhost:8000/docs
- **Documentation alternative** : http://localhost:8000/redoc

---

## 📝 Notes

- **Port par défaut** : 8000
- **Logs** : Toutes les interactions sont enregistrées dans les logs
- **IA locale** : Le système utilise Ollama pour l'IA locale

---

<div align="right">

*Dernière mise à jour : novembre 2025*

</div>

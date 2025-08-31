# 🐳 Guide de dépannage Docker - Arkalia-LUNA

## 🚨 **Problèmes courants et solutions**

### **1. Conteneur arkalia-api "unhealthy"**

#### **Symptômes :**
```
Container arkalia-api Error
dependency failed to start: container arkalia-api is unhealthy
```

#### **Causes possibles :**
- **Port incorrect** : Le service écoute sur `127.0.0.1` au lieu de `0.0.0.0`
- **Healthcheck trop strict** : L'endpoint `/health` n'est pas accessible
- **Dépendances manquantes** : Modules Python non trouvés
- **Timing** : Le service n'a pas le temps de démarrer avant le healthcheck

#### **Solutions :**

##### **A. Vérifier la configuration du port**
```python
# Dans run_arkalia_api.py, s'assurer que :
uvicorn.run(
    app,
    host="0.0.0.0",  # ✅ Correct pour Docker
    port=8000,
    # ...
)
```

##### **B. Vérifier l'endpoint /health**
```bash
# Tester localement
curl -f http://localhost:8000/health
# Doit retourner : {"status": "ok"}
```

##### **C. Ajuster les paramètres de healthcheck**
```yaml
# Dans docker-compose.yml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s      # ✅ Augmenter si nécessaire
  timeout: 15s       # ✅ Augmenter si nécessaire
  retries: 5         # ✅ Augmenter si nécessaire
  start_period: 120s # ✅ Augmenter si nécessaire
```

### **2. Dépendances circulaires entre services**

#### **Problème :**
Les services dépendent les uns des autres, créant des deadlocks.

#### **Solution :**
Démarrer les services dans l'ordre correct avec des délais :

```bash
# Utiliser le script de démarrage robuste
./docker-start.sh
```

**Ordre recommandé :**
1. `arkalia-api` (service principal)
2. `reflexia` (après que arkalia-api soit healthy)
3. `arkalia-sandozia` (après que reflexia soit healthy)
4. `arkalia-assistantia` (après que arkalia-api soit healthy)
5. `cognitive` (après que reflexia soit healthy)

### **3. Tests de healthcheck locaux**

#### **Script de test :**
```bash
./test_healthcheck.sh
```

#### **Tests manuels :**
```bash
# Test de l'endpoint /health
curl -f http://localhost:8000/health

# Test de l'endpoint /status
curl -f http://localhost:8000/status

# Test de l'endpoint racine
curl -f http://localhost:8000/
```

### **4. Logs et diagnostic**

#### **Voir les logs d'un service :**
```bash
docker-compose logs arkalia-api
docker-compose logs reflexia
docker-compose logs arkalia-sandozia
```

#### **Voir le statut des services :**
```bash
docker-compose ps
```

#### **Redémarrer un service spécifique :**
```bash
docker-compose restart arkalia-api
```

### **5. Nettoyage et redémarrage complet**

#### **Arrêter tous les services :**
```bash
docker-compose down --remove-orphans
```

#### **Nettoyer les images :**
```bash
docker-compose down --rmi all --volumes --remove-orphans
```

#### **Redémarrer depuis zéro :**
```bash
./docker-start.sh
```

### **6. Vérification de l'environnement**

#### **Dépendances système :**
```bash
# Vérifier que curl est installé dans le conteneur
docker exec arkalia-api which curl

# Vérifier les permissions des fichiers
docker exec arkalia-api ls -la /app
```

#### **Variables d'environnement :**
```bash
# Voir les variables d'environnement d'un conteneur
docker exec arkalia-api env
```

### **7. Scripts de démarrage**

#### **Script principal :**
- `docker-start.sh` : Démarrage robuste avec gestion des dépendances
- `test_healthcheck.sh` : Test des endpoints de santé

#### **Utilisation :**
```bash
# Rendre exécutables
chmod +x docker-start.sh test_healthcheck.sh

# Démarrer
./docker-start.sh

# Tester
./test_healthcheck.sh
```

## 🔧 **Configuration recommandée**

### **Healthchecks optimisés :**
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 45s      # Plus long pour éviter la surcharge
  timeout: 20s       # Plus long pour les services lents
  retries: 3         # Moins de tentatives
  start_period: 180s # Plus long pour le démarrage initial
```

### **Dépendances avec conditions :**
```yaml
depends_on:
  arkalia-api:
    condition: service_healthy
  reflexia:
    condition: service_healthy
```

## 📚 **Ressources supplémentaires**

- [Documentation Docker Compose](https://docs.docker.com/compose/)
- [Healthchecks Docker](https://docs.docker.com/engine/reference/builder/#healthcheck)
- [Troubleshooting Docker](https://docs.docker.com/config/daemon/#troubleshooting)

---

**💡 Conseil :** Utilisez toujours `./docker-start.sh` pour un démarrage fiable des services !

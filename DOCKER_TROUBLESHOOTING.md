# 🐳 Guide de dépannage Docker - Arkalia-LUNA

## 🚨 Problèmes identifiés et solutions

### ❌ **Problème principal : Conteneurs marqués comme "unhealthy"**

**Symptômes :**
- Build Docker réussi
- Conteneurs créés mais démarrage échoué
- Erreur : `dependency failed to start: container arkalia-api is unhealthy`

**Causes identifiées :**
1. **Healthchecks avec `curl`** : `curl` n'est pas installé dans les conteneurs
2. **Dépendances circulaires** : Services qui dépendent les uns des autres
3. **Timeouts trop courts** : Healthchecks qui échouent avant que les services soient prêts

## 🔧 **Solutions appliquées**

### 1. **Fichier Docker Compose corrigé** (`docker-compose-fixed.yml`)

**Améliorations :**
- ✅ Healthchecks avec Python au lieu de `curl`
- ✅ Dépendances ordonnées et logiques
- ✅ Timeouts et retries ajustés
- ✅ Gestion robuste des services

**Changements clés :**
```yaml
# Avant (problématique)
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]

# Après (corrigé)
healthcheck:
  test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8000/health', timeout=5)"]
  start_period: 60s  # Plus de temps pour le démarrage
```

### 2. **Script de démarrage robuste** (`scripts/docker-start-robust.sh`)

**Fonctionnalités :**
- 🚀 Démarrage séquentiel des services
- ⏳ Attente intelligente des healthchecks
- 🔍 Vérification des endpoints
- 📊 Monitoring du statut des services

**Ordre de démarrage :**
1. **arkalia-api** (service principal)
2. **reflexia** (dépend de l'API)
3. **autres services** (dépendent de ReflexIA)

### 3. **Variables d'environnement** (`docker.env`)

**Configuration :**
- Ports standardisés
- Environnements cohérents
- Timeouts configurables
- Ressources Docker optimisées

## 🚀 **Utilisation des corrections**

### **Option 1 : Utiliser le fichier corrigé directement**
```bash
# Démarrer avec le fichier corrigé
docker-compose -f docker-compose-fixed.yml up -d

# Vérifier le statut
docker-compose -f docker-compose-fixed.yml ps
```

### **Option 2 : Utiliser le script robuste (recommandé)**
```bash
# Rendre le script exécutable
chmod +x scripts/docker-start-robust.sh

# Lancer le démarrage robuste
./scripts/docker-start-robust.sh
```

### **Option 3 : Utiliser les variables d'environnement**
```bash
# Charger les variables d'environnement
export $(cat docker.env | xargs)

# Démarrer avec Docker Compose
docker-compose -f docker-compose-fixed.yml up -d
```

## 🔍 **Vérification et diagnostic**

### **Vérifier le statut des services**
```bash
# Statut général
docker-compose -f docker-compose-fixed.yml ps

# Logs d'un service spécifique
docker-compose -f docker-compose-fixed.yml logs arkalia-api

# Logs en temps réel
docker-compose -f docker-compose-fixed.yml logs -f reflexia
```

### **Tester les endpoints**
```bash
# API principale
curl -f http://localhost:8000/health

# AssistantIA
curl -f http://localhost:8001/api/v1/health

# ReflexIA
curl -f http://localhost:8002/health

# Cognitive Reactor
curl -f http://localhost:8003/health
```

### **Vérifier les ressources Docker**
```bash
# Utilisation des ressources
docker stats

# Espace disque
docker system df

# Nettoyage si nécessaire
docker system prune -f
```

## 🛠️ **Résolution des problèmes courants**

### **Problème : Service ne démarre pas**
```bash
# 1. Vérifier les logs
docker-compose -f docker-compose-fixed.yml logs <service-name>

# 2. Redémarrer le service
docker-compose -f docker-compose-fixed.yml restart <service-name>

# 3. Vérifier les dépendances
docker-compose -f docker-compose-fixed.yml ps
```

### **Problème : Healthcheck échoue**
```bash
# 1. Vérifier que le service écoute sur le bon port
docker exec -it <container-name> netstat -tlnp

# 2. Tester l'endpoint depuis l'intérieur du conteneur
docker exec -it <container-name> python -c "import requests; print(requests.get('http://localhost:8000/health'))"

# 3. Vérifier les variables d'environnement
docker exec -it <container-name> env | grep ARKALIA
```

### **Problème : Port déjà utilisé**
```bash
# 1. Identifier le processus qui utilise le port
lsof -i :8000

# 2. Arrêter le processus
kill -9 <PID>

# 3. Ou changer le port dans docker.env
echo "PORT_API=8001" >> docker.env
```

## 📚 **Documentation et ressources**

### **Fichiers de configuration**
- `docker-compose-fixed.yml` : Configuration Docker Compose corrigée
- `docker.env` : Variables d'environnement
- `scripts/docker-start-robust.sh` : Script de démarrage robuste

### **Commandes utiles**
```bash
# Arrêter tous les services
docker-compose -f docker-compose-fixed.yml down

# Arrêter et supprimer les volumes
docker-compose -f docker-compose-fixed.yml down -v

# Reconstruire les images
docker-compose -f docker-compose-fixed.yml build --no-cache

# Voir les logs de tous les services
docker-compose -f docker-compose-fixed.yml logs
```

### **Support et dépannage**
- Vérifiez que Docker est en cours d'exécution
- Assurez-vous d'avoir suffisamment de ressources (RAM, CPU)
- Vérifiez que les ports ne sont pas déjà utilisés
- Consultez les logs pour identifier les erreurs spécifiques

## 🎯 **Objectif final**

Avec ces corrections, Arkalia-LUNA devrait :
- ✅ Démarrer de manière robuste et fiable
- ✅ Gérer correctement les dépendances entre services
- ✅ Fournir des healthchecks fonctionnels
- ✅ Offrir un monitoring en temps réel
- ✅ Être prêt pour la production

---

*Guide créé le 31 août 2025 - Arkalia-LUNA v2.8.0* 🌕

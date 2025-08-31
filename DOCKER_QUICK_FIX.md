# 🚨 Résolution rapide des problèmes Docker - Arkalia-LUNA

## 🆘 **PROBLÈME IMMÉDIAT : Conteneurs "unhealthy"**

### **Solution 1 : Fichier ultra-robuste (RECOMMANDÉ)**
```bash
# Utiliser le fichier avec healthchecks simplifiés
docker-compose -f docker-compose-ultra-robust.yml up -d

# Vérifier le statut
docker-compose -f docker-compose-ultra-robust.yml ps
```

### **Solution 2 : Script ultra-robuste**
```bash
# Lancer le script de démarrage ultra-robuste
./scripts/docker-start-ultra-robust.sh
```

### **Solution 3 : Test local d'abord**
```bash
# Tester l'API localement avant Docker
python scripts/test_api_local.py
```

## 🔍 **Diagnostic rapide**

### **Vérifier les logs du conteneur problématique**
```bash
# Logs de l'API principale
docker-compose -f docker-compose-ultra-robust.yml logs arkalia-api

# Logs en temps réel
docker-compose -f docker-compose-ultra-robust.yml logs -f arkalia-api
```

### **Vérifier le statut des conteneurs**
```bash
# Statut général
docker-compose -f docker-compose-ultra-robust.yml ps

# Statut détaillé
docker-compose -f docker-compose-ultra-robust.yml ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
```

## 🛠️ **Corrections immédiates**

### **Redémarrer un service spécifique**
```bash
# Redémarrer l'API
docker-compose -f docker-compose-ultra-robust.yml restart arkalia-api

# Redémarrer tous les services
docker-compose -f docker-compose-ultra-robust.yml restart
```

### **Reconstruire les images**
```bash
# Reconstruire sans cache
docker-compose -f docker-compose-ultra-robust.yml build --no-cache

# Redémarrer après reconstruction
docker-compose -f docker-compose-ultra-robust.yml up -d
```

## 📋 **Différences entre les fichiers**

| Fichier | Healthchecks | Timeouts | Robustesse |
|---------|--------------|----------|------------|
| `docker-compose.yml` | ❌ curl (échoue) | ⏰ Courts | ❌ Faible |
| `docker-compose-fixed.yml` | ✅ Python requests | ⏰ Moyens | ✅ Moyenne |
| `docker-compose-ultra-robust.yml` | ✅ Python socket | ⏰ Très longs | 🚀 Maximale |

## 🎯 **Stratégie recommandée**

1. **Utiliser `docker-compose-ultra-robust.yml`** (healthchecks avec socket)
2. **Timeouts étendus** (5-10 minutes pour le démarrage)
3. **Démarrage séquentiel** avec le script ultra-robuste
4. **Tests manuels** des endpoints si nécessaire

## 🚀 **Commandes de démarrage**

### **Démarrage simple**
```bash
docker-compose -f docker-compose-ultra-robust.yml up -d
```

### **Démarrage avec logs**
```bash
docker-compose -f docker-compose-ultra-robust.yml up
```

### **Démarrage séquentiel robuste**
```bash
./scripts/docker-start-ultra-robust.sh
```

## 🔧 **Maintenance**

### **Nettoyer les conteneurs**
```bash
# Arrêter et supprimer
docker-compose -f docker-compose-ultra-robust.yml down

# Avec volumes
docker-compose -f docker-compose-ultra-robust.yml down -v
```

### **Vérifier les ressources**
```bash
# Utilisation des ressources
docker stats

# Espace disque
docker system df
```

---

**💡 Conseil : Commencez toujours par `docker-compose-ultra-robust.yml` !**

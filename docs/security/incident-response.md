# 🚨 Incident Response — Arkalia-LUNA

![Emergency](https://img.shields.io/badge/status-emergency_ready-red)
![Response](https://img.shields.io/badge/response-24h-orange)
![Recovery](https://img.shields.io/badge/recovery-automated-green)

**Guide de réponse aux incidents sécurité pour Arkalia-LUNA** — Procédures d'urgence, investigation et récupération automatisée.

---

## 🎯 Classification des Incidents

### **NIVEAU 1 - CRITIQUE 🔴**
*Système compromis, service totalement indisponible*

| Type d'Incident | Exemple | Impact | Temps Réponse |
|------------------|---------|--------|---------------|
| **Container Escape** | Accès root depuis Docker | 🔴 Host compromis | **Immédiat** |
| **LLM Poisoning** | Modèle Ollama corrompu | 🔴 Réponses malveillantes | **< 15 min** |
| **State Corruption Massive** | Tous fichiers TOML corrompus | 🔴 Système inutilisable | **< 30 min** |
| **Prompt Injection RCE** | Exécution code via AssistantIA | 🔴 Code execution | **Immédiat** |

### **NIVEAU 2 - ÉLEVÉ 🟧**
*Service dégradé, données potentiellement compromises*

| Type d'Incident | Exemple | Impact | Temps Réponse |
|------------------|---------|--------|---------------|
| **DoS Sophisticated** | Attaque coordonnée API | 🟧 Service inaccessible | **< 2h** |
| **Memory Exhaustion** | ZeroIA loop infini | 🟧 Performance dégradée | **< 1h** |
| **Log Injection** | Falsification logs audit | 🟧 Traçabilité compromise | **< 4h** |
| **Unauthorized Access** | Tentatives brute force | 🟧 Confidentialité menacée | **< 2h** |

### **NIVEAU 3 - MOYEN 🟨**
*Anomalie détectée, investigation requise*

| Type d'Incident | Exemple | Impact | Temps Réponse |
|------------------|---------|--------|---------------|
| **Performance Anomaly** | Latence inhabituelle | 🟨 Expérience dégradée | **< 24h** |
| **Configuration Drift** | Paramètres modifiés | 🟨 Dérive sécurité | **< 12h** |
| **Suspicious Patterns** | Comportement utilisateur bizarre | 🟨 Surveillance accrue | **< 24h** |

---

## 🚀 Procédures d'Urgence par Type d'Incident

### 🔴 **PROCÉDURE P1 : Container Escape**

#### **Détection automatique :**
```bash
# Surveillance en temps réel
auditd | grep -E "(docker|container)" | grep "syscall=execve"
ps aux | grep -v grep | grep -E "docker.*root"
```

#### **Actions immédiates (< 5 minutes) :**
```bash
#!/bin/bash
# Script ark-emergency-lockdown.sh

echo "🚨 CONTAINER ESCAPE DÉTECTÉ - LOCKDOWN IMMÉDIAT"

# 1. ARRÊT TOTAL containers
docker kill $(docker ps -q) 2>/dev/null
docker-compose down --remove-orphans --timeout 5

# 2. Isolation réseau
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT DROP
iptables -A OUTPUT -p tcp --dport 22 -j ACCEPT  # SSH admin uniquement

# 3. Sauvegarde états critiques
tar -czf /backup/emergency_$(date +%s).tar.gz \
  state/ \
  global_state/ \
  logs/ 2>/dev/null

# 4. Audit système
find /var/lib/docker -type f -newer /tmp/incident_start -ls > /tmp/docker_changes.log
netstat -tulpn > /tmp/network_state.log
ps auxf > /tmp/process_state.log

echo "✅ LOCKDOWN TERMINÉ - Investigation manuelle requise"
```

#### **Investigation (< 30 minutes) :**
```bash
# Analyse forensique rapide
journalctl -u docker --since "10 minutes ago" | grep -E "(exec|mount|capability)"
find /proc -name "status" -exec grep -l "docker" {} \; 2>/dev/null
lsof | grep docker | head -20
```

#### **Récupération contrôlée :**
```bash
# 1. Nettoyage environnement
docker system prune -af --volumes
rm -rf /var/lib/docker/tmp/*

# 2. Reconstruction sécurisée
git stash && git pull origin main
./scripts/ark-sec-check.sh --paranoid-mode
docker-compose build --no-cache --security-opt seccomp:default

# 3. Redémarrage graduel
docker-compose up -d --scale assistantia=0  # Démarre sans IA
./scripts/healthcheck_system.sh --full-validation
docker-compose up -d  # Démarre service complet si validation OK
```

---

### 🔴 **PROCÉDURE P2 : LLM Model Poisoning**

#### **Détection automatique :**
```bash
# Vérification intégrité modèles Ollama
find /var/lib/ollama/models -name "*.bin" -exec sha256sum {} \; > /tmp/model_checksums.txt
diff /tmp/model_checksums.txt /etc/arkalia/trusted_models.sha256
```

#### **Actions immédiates :**
```bash
#!/bin/bash
echo "🧠 LLM POISONING DÉTECTÉ - QUARANTINE MODÈLES"

# 1. Arrêt service IA immédiat
docker stop assistantia ollama

# 2. Isolation modèles suspects
mv /var/lib/ollama/models /var/lib/ollama/models.quarantine.$(date +%s)
mkdir -p /var/lib/ollama/models

# 3. Restauration modèles propres
if [ -f /backup/clean_models.tar.gz ]; then
    cd /var/lib/ollama && tar -xzf /backup/clean_models.tar.gz
    echo "✅ Modèles propres restaurés depuis backup"
else
    echo "❌ BACKUP MANQUANT - Téléchargement modèles depuis source officielle requis"
fi

# 4. Validation stricte avant redémarrage
ollama list 2>/dev/null || echo "⚠️ Ollama non disponible"
```

#### **Re-téléchargement sécurisé :**
```bash
# Procédure de re-téléchargement sécurisé modèles
ollama pull mistral:7b-instruct-v0.1-q4_0  # Version spécifique
ollama pull llama2:7b-chat-q4_0              # Version spécifique

# Validation checksums officiels
sha256sum /var/lib/ollama/models/manifests/registry.ollama.ai/library/mistral/7b-instruct-v0.1-q4_0
# Comparaison avec hashes officiel Ollama Registry
```

---

### 🟧 **PROCÉDURE P3 : Prompt Injection avec RCE**

#### **Détection en temps réel :**
```python
# Intégré dans modules/assistantia/security/prompt_validator.py
DANGEROUS_PATTERNS = [
    r'exec\s*\(',
    r'eval\s*\(',
    r'import\s+os',
    r'system\s*\(',
    r'subprocess\.',
    r'__import__',
    r'open\s*\(',
    r'file\s*\(',
]

def detect_rce_attempt(prompt: str) -> bool:
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, prompt, re.IGNORECASE):
            logger.critical(f"[SECURITY] RCE attempt detected: {pattern}")
            return True
    return False
```

#### **Actions automatiques :**
```bash
# Déclenchées automatiquement par AssistantIA
# 1. Blocage immédiat conversation
# 2. Journalisation détaillée
# 3. Alerte équipe sécurité
# 4. Quarantine session utilisateur

echo "🚨 RCE PROMPT INJECTION BLOQUÉ" | tee -a /var/log/arkalia/security.log
docker restart assistantia  # Restart clean état
```

---

## 🔄 Procédures de Rollback Automatisé

### **Rollback État ZeroIA**
```bash
#!/bin/bash
# scripts/zeroia_emergency_rollback.sh

echo "🔄 ROLLBACK ZEROIA EMERGENCY"

# 1. Arrêt ZeroIA
docker stop zeroia

# 2. Sauvegarde état actuel (corrompu)
cp state/zeroia_state.toml \
   /backup/corrupted_zeroia_$(date +%s).toml

# 3. Recherche backup valide le plus récent
BACKUP_FILE=$(find /backup -name "zeroia_state_backup_*.toml" -mtime -7 | sort -r | head -1)

if [ -f "$BACKUP_FILE" ]; then
    cp "$BACKUP_FILE" state/zeroia_state.toml
    echo "✅ Rollback depuis: $BACKUP_FILE"
else
    # Fallback : état par défaut minimal
    cat > state/zeroia_state.toml << EOF
[decision]
last_decision = "normal"
confidence_score = 0.5
justification = "emergency_rollback_default_state"
timestamp = "$(date -Iseconds)"

[metadata]
version = "emergency_fallback"
restore_time = "$(date -Iseconds)"
EOF
    echo "⚠️ Rollback vers état par défaut minimal"
fi

# 4. Validation état restauré
python -c "
import toml
try:
    state = toml.load('state/zeroia_state.toml')
    assert 'decision' in state
    assert 'last_decision' in state['decision']
    print('✅ État ZeroIA validé')
except Exception as e:
    print(f'❌ État invalide: {e}')
    exit(1)
"

# 5. Redémarrage contrôlé
if [ $? -eq 0 ]; then
    docker start zeroia
    sleep 5
    docker logs zeroia --tail 20
    echo "✅ ZeroIA redémarré avec succès"
else
    echo "❌ Validation échouée - intervention manuelle requise"
fi
```

### **Rollback Global Système**
```bash
#!/bin/bash
# scripts/ark_system_rollback.sh

echo "🔄 ROLLBACK SYSTÈME ARKALIA-LUNA COMPLET"

# 1. Arrêt tous services
docker-compose down

# 2. Restauration configs Git
git stash push -m "emergency_stash_$(date +%s)"
git checkout HEAD~1  # Rollback 1 commit
git checkout main

# 3. Restauration états modules depuis backup
./scripts/restore_all_states.sh --emergency

# 4. Validation intégrité complète
./scripts/ark-sec-check.sh --full-validation || {
    echo "❌ Validation sécurité échouée après rollback"
    exit 1
}

# 5. Redémarrage graduel sécurisé
docker-compose up -d reflexia  # Monitoring en premier
sleep 10
docker-compose up -d zeroia helloria  # Services core
sleep 10
docker-compose up -d assistantia  # IA en dernier

echo "✅ Rollback système terminé - surveillance accrue activée"
```

---

## 📊 Monitoring Post-Incident

### **Surveillance Renforcée (72h)**
```bash
# Activation monitoring paranoid mode
export ARKALIA_MONITORING_MODE="paranoid"
export ARKALIA_LOG_LEVEL="DEBUG"

# Métriques surveillance accrue
watch -n 30 'curl -s http://localhost:8000/metrics | grep -E "(error|security|anomaly)"'

# Logs temps réel toutes sources
tail -f logs/*.log modules/*/logs/*.log | grep -E "(ERROR|CRITICAL|SECURITY)"
```

### **Checklist Validation Post-Incident**
- [ ] ✅ Tous services opérationnels et stables
- [ ] ✅ Métriques système dans plages normales
- [ ] ✅ Logs ne montrent plus d'anomalies
- [ ] ✅ Tests fonctionnels automatisés passent
- [ ] ✅ Scan sécurité complet sans alertes
- [ ] ✅ Backup états critiques réalisé
- [ ] ✅ Documentation incident mise à jour
- [ ] ✅ Post-mortem planifié sous 48h

---

## 📋 Templates d'Escalade

### **Alert Équipe Critique**
```bash
# Script notification automatique
#!/bin/bash
INCIDENT_TYPE="$1"
SEVERITY="$2"
DETAILS="$3"

cat << EOF | mail -s "[ARKALIA URGENT] $INCIDENT_TYPE - $SEVERITY" arkalia.luna.system@gmail.com
🚨 INCIDENT ARKALIA-LUNA DÉTECTÉ

Severité: $SEVERITY
Type: $INCIDENT_TYPE
Heure: $(date -Iseconds)
Host: $(hostname)
IP: $(hostname -I | awk '{print $1}')

Détails:
$DETAILS

Actions automatiques déclenchées:
✅ Services critiques arrêtés
✅ États sauvegardés
✅ Logs préservés
✅ Monitoring renforcé activé

Investigation immédiate requise.

-- Arkalia-LUNA Security System
EOF
```

### **Template Rapport Post-Incident**
```markdown
# 📋 Rapport Post-Incident ARKALIA-LUNA

**Incident ID:** INC-$(date +%Y%m%d-%H%M%S)
**Date:** $(date -Iseconds)
**Severité:** [CRITIQUE/ÉLEVÉ/MOYEN]

## 🎯 Résumé Exécutif
[Description 2-3 phrases de l'incident]

## ⏱️ Chronologie
- **HH:MM** - Détection initiale
- **HH:MM** - Actions d'urgence déclenchées
- **HH:MM** - Investigation commencée
- **HH:MM** - Cause racine identifiée
- **HH:MM** - Solution déployée
- **HH:MM** - Service restauré
- **HH:MM** - Validation post-incident

## 🔍 Cause Racine
[Analyse technique détaillée]

## 🛠️ Actions Correctives Immédiates
- [ ] Action 1
- [ ] Action 2
- [ ] Action 3

## 🔄 Actions Préventives Long Terme
- [ ] Amélioration 1
- [ ] Amélioration 2
- [ ] Amélioration 3

## 📊 Impact
- **Durée d'indisponibilité:** X minutes
- **Services affectés:** [Liste]
- **Données compromises:** Aucune/[Détails]
- **Utilisateurs impactés:** [Nombre/Détails]

## 📚 Leçons Apprises
[Points clés pour amélioration]

---
*Rapport généré par Arkalia-LUNA Incident Response System*
```

---

## 🧪 Tests Procédures (Chaos Engineering)

### **Simulation Incident Contrôlée**
```bash
# tests/chaos/incident_simulation.py
def simulate_container_escape():
    """Simule un container escape pour tester procédures"""
    # Déclenche alertes sans réel risque

def simulate_prompt_injection():
    """Teste détection prompt injection"""
    # Envoie patterns suspects contrôlés

def simulate_state_corruption():
    """Corrompt temporairement fichier état test"""
    # Valide rollback automatique
```

### **Drill Équipe Sécurité (Mensuel)**
```bash
# Exercice incident response équipe
./scripts/ark_security_drill.sh --scenario container_escape --dry-run
./scripts/ark_security_drill.sh --scenario llm_poisoning --dry-run
./scripts/ark_security_drill.sh --scenario prompt_injection --dry-run
```

---

## 📞 Contacts d'Urgence

### **Escalade Immédiate**
- 🚨 **Incident CRITIQUE** : +33-XXX-XXX-XXX (24h/7j)
- 📧 **Email sécurisé** : arkalia.luna.system@gmail.com
- 💬 **notifications d'urgence** : #arkalia-security-emergency

### **Support Technique**
- 🔧 **DevOps On-Call** : arkalia.luna.system@gmail.com
- 🧠 **Expert IA** : arkalia.luna.system@gmail.com
- 🐳 **Infrastructure** : arkalia.luna.system@gmail.com

---

*Document d'urgence maintenu par Arkalia-LUNA Security Response Team*
*🚨 "Préparation, Réaction, Récupération" — Doctrine de Résilience Arkalia*

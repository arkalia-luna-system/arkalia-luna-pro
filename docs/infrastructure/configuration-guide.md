# 📋 Guide de Configuration - Arkalia-LUNA Pro

## Structure des Configurations

**Date :** 2025-11-13  
**Version :** 3.0.0-enhanced

---

## 🎯 PRINCIPE GÉNÉRAL

Arkalia-LUNA Pro utilise une **architecture de configuration hybride** :
- **Config centralisée** : `config/` pour configurations globales
- **Configs modulaires** : `modules/*/config/` pour configurations spécifiques aux modules

Cette approche permet :
- ✅ **Séparation des responsabilités** : Chaque module gère sa propre config
- ✅ **Isolation** : Modifications d'un module n'affectent pas les autres
- ✅ **Flexibilité** : Configuration globale + overrides par module
- ✅ **Maintenabilité** : Structure claire et organisée

---

## 📁 STRUCTURE DES CONFIGURATIONS

### 1. Configuration Globale (`config/`)

**Emplacement :** `/config/`

**Usage :** Configurations partagées entre tous les modules

**Fichiers typiques :**
- `config/zeroia_config.toml` : Configuration globale ZeroIA
- `config/pytest/*.ini` : Configurations pytest
- `config/docker/*.yml` : Configurations Docker

**Chargement :**
```python
from modules.core.config.config_manager import get_default_config_manager

config_manager = get_default_config_manager()
config = config_manager.load_toml_config(Path("config/zeroia_config.toml"))
```

---

### 2. Configurations Modulaires (`modules/*/config/`)

**Emplacement :** `/modules/{module}/config/`

**Usage :** Configurations spécifiques à chaque module

**Exemples :**
- `modules/zeroia/config/weights.toml` : Poids de décision ZeroIA
- `modules/reflexia/config/reflexia_config.toml` : Configuration ReflexIA
- `modules/sandozia/config/sandozia_config.toml` : Configuration Sandozia
- `modules/taskia/config/taskia_config.toml` : Configuration TaskIA

**Chargement :**
```python
from modules.core.config.config_manager import get_default_config_manager

config_manager = get_default_config_manager()
module_config = config_manager.get_module_config("sandozia")
# ou directement
config = config_manager.load_toml_config(Path("modules/sandozia/config/sandozia_config.toml"))
```

---

## 🔄 SYSTÈME DE CHARGEMENT CENTRALISÉ

### ConfigManager

**Emplacement :** `modules/core/config/config_manager.py`

**Fonctionnalités :**
- ✅ Chargement TOML avec cache
- ✅ Gestion des configurations par module
- ✅ Support des variables d'environnement
- ✅ Validation et fallback sur valeurs par défaut

**Méthodes principales :**
- `load_toml_config(file_path)` : Charge un fichier TOML avec cache
- `get_module_config(module_name)` : Récupère config d'un module
- `get_environment_config()` : Récupère config depuis variables d'environnement

**Exemple d'utilisation :**
```python
from modules.core.config.config_manager import get_default_config_manager

# Charger config globale
config_manager = get_default_config_manager()
global_config = config_manager.load_toml_config(Path("config/zeroia_config.toml"))

# Charger config module
sandozia_config = config_manager.get_module_config("sandozia")
```

---

## 📊 TABLEAU RÉCAPITULATIF

| Emplacement | Usage | Exemple | Chargement |
|-------------|-------|---------|------------|
| `config/` | Configurations globales | `config/zeroia_config.toml` | `ConfigManager.load_toml_config()` |
| `modules/zeroia/config/` | Config ZeroIA spécifique | `modules/zeroia/config/weights.toml` | `ConfigManager.get_module_config("zeroia")` |
| `modules/reflexia/config/` | Config ReflexIA spécifique | `modules/reflexia/config/reflexia_config.toml` | `ConfigManager.get_module_config("reflexia")` |
| `modules/sandozia/config/` | Config Sandozia spécifique | `modules/sandozia/config/sandozia_config.toml` | `ConfigManager.get_module_config("sandozia")` |
| `modules/taskia/config/` | Config TaskIA spécifique | `modules/taskia/config/taskia_config.toml` | `ConfigManager.get_module_config("taskia")` |

---

## 🎯 PRATIQUES RECOMMANDÉES

### 1. Utiliser ConfigManager pour tous les chargements TOML

✅ **BON :**
```python
from modules.core.config.config_manager import get_default_config_manager

config_manager = get_default_config_manager()
config = config_manager.load_toml_config(config_path)
```

❌ **MAUVAIS :**
```python
import toml
with open(config_path) as f:
    config = toml.load(f)  # Pas de cache, pas de gestion d'erreurs centralisée
```

### 2. Configurations par module dans `modules/*/config/`

✅ **BON :**
- `modules/sandozia/config/sandozia_config.toml` : Config Sandozia
- `modules/zeroia/config/weights.toml` : Poids ZeroIA

❌ **MAUVAIS :**
- `config/sandozia_config.toml` : Mélange configs globales et modulaires

### 3. Configurations globales dans `config/`

✅ **BON :**
- `config/zeroia_config.toml` : Config globale ZeroIA (si partagée)
- `config/pytest/pytest.ini` : Config pytest

---

## 🔧 MIGRATION VERS CONFIGMANAGER

### Avant (loaders dispersés)

```python
# modules/reflexia/utils/config_loader.py (ANCIEN)
import toml
def load_config():
    with open("modules/reflexia/config/reflexia_config.toml") as f:
        return toml.load(f)
```

### Après (ConfigManager centralisé)

```python
# modules/reflexia/utils/config_loader.py (NOUVEAU)
from modules.core.config.config_manager import get_default_config_manager

def load_config():
    config_manager = get_default_config_manager()
    return config_manager.load_toml_config(
        Path("modules/reflexia/config/reflexia_config.toml")
    )
```

**Avantages :**
- ✅ Cache automatique (performance)
- ✅ Gestion d'erreurs centralisée
- ✅ Support variables d'environnement
- ✅ Validation et fallback

---

## 📝 EXEMPLES CONCRETS

### Exemple 1 : Charger config Sandozia

```python
from pathlib import Path
from modules.core.config.config_manager import get_default_config_manager

config_manager = get_default_config_manager()
config_path = Path("modules/sandozia/config/sandozia_config.toml")
config = config_manager.load_toml_config(config_path)

# Utiliser la config
interval = config.get("monitoring", {}).get("interval_seconds", 30)
```

### Exemple 2 : Charger config module (méthode simplifiée)

```python
from modules.core.config.config_manager import get_default_config_manager

config_manager = get_default_config_manager()
sandozia_config = config_manager.get_module_config("sandozia")

# La méthode cherche automatiquement dans modules/sandozia/config/
```

### Exemple 3 : Variables d'environnement

```python
from modules.core.config.config_manager import get_default_config_manager

config_manager = get_default_config_manager()
env_config = config_manager.get_environment_config()

# Récupère config depuis variables d'environnement
# Ex: ZEROIA_CPU_THRESHOLD=80
```

---

## 🚨 NOTES IMPORTANTES

### Pourquoi configs dispersées ?

1. **Isolation des modules** : Chaque module peut avoir sa propre config sans conflit
2. **Déploiement modulaire** : Possibilité de déployer un module indépendamment
3. **Tests unitaires** : Facilite les tests avec configs mockées par module
4. **Maintenance** : Plus facile de trouver/modifier la config d'un module spécifique

### Quand utiliser `config/` vs `modules/*/config/` ?

- **`config/`** : Configurations partagées, globales, ou de déploiement
- **`modules/*/config/`** : Configurations spécifiques à un module

---

## 🔗 LIENS UTILES

- **ConfigManager** : Voir le code source dans `modules/core/config/config_manager.py`
- **Exemple ReflexIA** : Voir le code source dans `modules/reflexia/utils/config_loader.py`
- **Exemple Sandozia** : Voir le code source dans `modules/sandozia/core/sandozia_core.py`

---

**Dernière mise à jour :** 2025-11-13


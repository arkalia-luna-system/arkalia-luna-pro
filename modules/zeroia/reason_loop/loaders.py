"""
Loaders - Fonctions de chargement TOML et contexte
"""

import time
from pathlib import Path
from typing import Any

import toml

from core.ark_logger import ark_logger
from modules.zeroia.circuit_breaker import CognitiveOverloadError, DecisionIntegrityError

# === Chemins par défaut ===
CTX_PATH = Path("state/global_context.toml")
REFLEXIA_STATE = Path("state/reflexia_state.toml")

# === Cache TOML Enterprise optimisé pour performance Docker ===
_TOML_CACHE: dict[str, Any] = {}
_CACHE_TIMESTAMPS: dict[str, Any] = {}
_CACHE_MAX_AGE = 30  # Cache 30s pour Docker container


def create_default_context_enhanced() -> dict:
    """
    Crée un contexte par défaut enterprise pour éviter les warnings CPU/RAM.
    Optimisé pour containers Docker avec tous les modules Arkalia.
    Structure complète v3.0 avec tous les modules.

    Returns:
        dict: Contexte par défaut enterprise avec valeurs optimales
    """
    from datetime import datetime

    current_time = datetime.now().isoformat()
    return {
        "last_update": current_time,
        "system_status": "operational",
        "active_modules": [
            "reflexia",
            "zeroia",
            "assistantia",
            "sandozia",
            "helloria",
            "taskia",
            "nyxalia",
        ],
        "version": "3.0.0-enhanced",
        "status": {
            "cpu": 45.2,  # CPU par défaut : 45% (charge normale container)
            "ram": 62.8,  # RAM par défaut : 62% (charge normale container)
            "severity": "normal",
            "disk_usage": 78,
            "network_latency": 25,
            "load_avg": 1.2,
            "active_processes": 150,
            "container_health": "healthy",
        },
        "reflexia": {
            "status": "operational",
            "last_check": current_time,
            "module_active": True,
            "last_decision": "normal",
            "confidence": 0.85,
            "cycle_count": 626,
        },
        "modules": {
            "sandozia": {
                "status": "active",
                "intelligence_level": "adaptive",
                "health": "healthy",
            },
            "assistantia": {
                "status": "active",
                "response_time": "optimal",
                "health": "healthy",
                "port": 8001,
            },
            "helloria": {"status": "active", "api_ready": True, "health": "healthy"},
            "nyxalia": {
                "status": "active",
                "monitoring": "enabled",
                "health": "healthy",
            },
            "taskia": {"status": "active", "queue_size": 0, "health": "healthy"},
            "zeroia": {
                "status": "active",
                "reason_loop": "enhanced",
                "health": "healthy",
                "circuit_breaker": "closed",
            },
        },
        "metadata": {
            "initialized": current_time,
            "version": "3.0.0-enhanced",
            "source": "arkalia_global_context_v3",
            "container": "arkalia-luna-system",
            "environment": "production",
            "docker_compose": True,
        },
    }


def ensure_parent_dir(path: Path) -> None:
    """Assure que le répertoire parent existe"""
    target = path.parent if path.suffix else path
    target.mkdir(parents=True, exist_ok=True)


def load_toml_enhanced_cache(path: Path, max_age: int | None = None) -> dict:
    """
    Charge un fichier TOML avec cache intelligent Enterprise pour Docker.
    Optimisé pour haute performance avec tous les modules Arkalia.

    Args:
        path: Chemin vers le fichier TOML
        max_age: Âge maximum du cache (défaut: 30s pour Docker)

    Returns:
        dict: Contenu du fichier TOML

    Raises:
        DecisionIntegrityError: Si le fichier est invalide
        CognitiveOverloadError: Si erreur de chargement
    """
    if max_age is None:
        max_age = _CACHE_MAX_AGE

    path_str = str(path)
    current_time = time.time()

    # Vérifier cache valide (performance Docker)
    if (
        path_str in _TOML_CACHE
        and path_str in _CACHE_TIMESTAMPS
        and current_time - _CACHE_TIMESTAMPS[path_str] < max_age
    ):
        cached = _TOML_CACHE[path_str]
        if isinstance(cached, dict):
            return cached

    try:
        if not path.exists() or not path.read_text().strip():
            # Auto-création contexte Enterprise si manquant
            if "global_context" in path_str:
                default_context = create_default_context_enhanced()
                ensure_parent_dir(path)
                with open(path, "w") as f:
                    toml.dump(default_context, f)
                _TOML_CACHE[path_str] = default_context
                _CACHE_TIMESTAMPS[path_str] = current_time
                ark_logger.info(
                    f"✅ [ZeroIA Enhanced] Contexte par défaut créé: {path}",
                    extra={"arkalia_module": "zeroia"},
                )
                return default_context
            raise ValueError(f"TOML file {path} is empty or missing")

        data = toml.load(path)
        _TOML_CACHE[path_str] = data
        _CACHE_TIMESTAMPS[path_str] = current_time
        return data

    except toml.TomlDecodeError as e:
        raise DecisionIntegrityError(f"[TOML Enhanced] Format invalide dans {path}: {e}") from e
    except Exception as e:
        raise CognitiveOverloadError(
            f"[TOML Enhanced] Erreur lors du chargement de {path}: {e}"
        ) from e


def load_toml(path: Path) -> dict:
    """Charge un fichier TOML avec gestion d'erreurs robuste"""
    return load_toml_enhanced_cache(path)


def load_context(path: Path = CTX_PATH) -> dict:
    """Charge le contexte global avec protection circuit breaker"""
    from .initialization import initialize_components_with_recovery

    cb, es, _, _ = initialize_components_with_recovery()
    result = cb.call(load_toml, path)
    if isinstance(result, dict):
        return result
    return {}


def load_reflexia_state(path: Path = REFLEXIA_STATE) -> dict:
    """Charge l'état ReflexIA avec protection circuit breaker"""
    from .initialization import initialize_components_with_recovery

    cb, es, _, _ = initialize_components_with_recovery()
    result = cb.call(load_toml, path)
    if isinstance(result, dict):
        return result
    return {}


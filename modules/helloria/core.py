"""
Module core Helloria - API principale d'Arkalia-LUNA Pro.

Ce module expose l'API FastAPI principale avec les endpoints de santé
pour tous les modules IA (ZeroIA, Reflexia, Sandozia).
"""

import asyncio
import json
import os
import time
from pathlib import Path
from typing import Any

import psutil
from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse, PlainTextResponse

from core.ark_logger import ark_logger

# 📦 Import des routes externes (modules IA)
from modules.reflexia.core_api import router as reflexia_router

# from modules.zeroia.core import router as zeroia_router
# Module supprimé lors de la refactorisation

# from modules.monitoring.prometheus_metrics import get_metrics_summary  # Module supprimé

# 🚦 Router principal
router = APIRouter()


def require_api_key(x_api_key: str | None = Header(default=None, alias="X-API-Key")) -> None:
    """Protège les endpoints sensibles via clé API si configurée."""
    expected = os.getenv("ARKALIA_API_KEY", "").strip()
    if not expected:
        return
    if x_api_key != expected:
        raise HTTPException(status_code=401, detail="Unauthorized")


def _collect_system_metrics() -> tuple[float, Any, Any]:
    """Collecte les métriques système de manière synchrone."""
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    return cpu_percent, memory, disk


def _read_json_dashboard(path: Path) -> dict[str, Any]:
    """Lit un dashboard JSON local."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("invalid dashboard format")
    return data


# 🎯 Endpoint principal IA
@router.post("/chat", tags=["IA"], response_model=None)
async def chat(request: Request) -> dict[str, Any] | JSONResponse:
    """
    Endpoint principal pour le chat IA via Helloria.

    Traite un message utilisateur et génère une réponse IA.

    Args:
        request: Requête FastAPI contenant le JSON avec le message.

    Returns:
        dict: Réponse avec le texte généré.
        JSONResponse: Erreur 400 si message vide.

    Raises:
        Exception: Erreur interne si problème de traitement.

    Examples:
        >>> POST /chat
        >>> {"message": "Bonjour"}
        >>> {"réponse": "Tu as dit : 'Bonjour' (réponse IA à coder 🎯)"}
    """
    try:
        data = await request.json()
        prompt = data.get("message", "").strip()

        if not prompt:
            return JSONResponse(status_code=400, content={"error": "Aucun message reçu."})

        # Placeholder IA
        response_text = f"Tu as dit : '{prompt}' (réponse IA à coder 🎯)"
        return {"réponse": response_text}

    except json.JSONDecodeError as e:
        ark_logger.warning(f"Payload JSON invalide: {e}", extra={"arkalia_module": "helloria"})
        raise HTTPException(status_code=400, detail="Payload JSON invalide") from e
    except Exception as e:
        ark_logger.error(f"Erreur interne : {e}", extra={"arkalia_module": "helloria"})
        raise HTTPException(status_code=500, detail="Erreur interne Helloria") from e


# 🌐 Racine API
@router.get("/", tags=["Root"])
async def root() -> dict:
    """
    Endpoint racine de l'API Helloria.

    Retourne un message de confirmation que l'API est active.

    Returns:
        dict: Message de confirmation.

    Examples:
        >>> GET /
        >>> {"message": "Arkalia-LUNA API active"}
    """
    return {"message": "Arkalia-LUNA API active"}


# 📊 Endpoint statut détaillé
@router.get("/status", tags=["Status"])
async def status(_: None = Depends(require_api_key)) -> dict:
    """
    Statut détaillé de l'API avec métriques système.

    Retourne l'état de tous les modules et les métriques système (CPU, RAM, disque).

    Returns:
        dict: Statut complet avec métriques système et modules.

    Examples:
        >>> GET /status
        >>> {
        ...     "service": "arkalia-api",
        ...     "version": "2.8.0",
        ...     "status": "active",
        ...     "modules": {"assistantia": "active", ...},
        ...     "system": {"cpu_percent": 45.2, ...}
        ... }
    """
    # Métriques système
    cpu_percent, memory, disk = await asyncio.to_thread(_collect_system_metrics)

    return {
        "service": "arkalia-api",
        "version": "2.8.0",
        "status": "active",
        "uptime_seconds": time.time(),
        "modules": {
            "assistantia": "active",
            "reflexia": "active",
            "zeroia": "active",
            "helloria": "active",
        },
        "metrics": "available",
        "system": {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_used_gb": round(memory.used / (1024**3), 2),
            "memory_total_gb": round(memory.total / (1024**3), 2),
            "disk_usage_percent": disk.percent,
            "disk_used_gb": round(disk.used / (1024**3), 2),
            "disk_total_gb": round(disk.total / (1024**3), 2),
        },
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }


# 📊 Endpoint métriques Prometheus
@router.get("/metrics", tags=["Monitoring"])
async def metrics(_: None = Depends(require_api_key)) -> PlainTextResponse:
    """
    Endpoint Prometheus pour exposition des métriques Arkalia-LUNA.

    Retourne les métriques au format OpenMetrics/Prometheus standard pour le scraping.

    Returns:
        PlainTextResponse: Métriques Prometheus au format texte.

    Raises:
        Exception: Erreur si problème de génération des métriques.

    Examples:
        >>> GET /metrics
        >>> # arkalia_requests_total{method="GET"} 42
        >>> # arkalia_cpu_usage 45.2
    """
    try:
        # Version JSON simplifiée des métriques pour compatibilité
        metrics_data = _get_fallback_metrics()
        try:
            from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

            # Utilise l'instance globale déjà initialisée
            return PlainTextResponse(
                generate_latest().decode("utf-8"), media_type=CONTENT_TYPE_LATEST
            )
        except ImportError:
            prometheus_text = _convert_to_prometheus_format(metrics_data)
            return PlainTextResponse(prometheus_text, media_type="text/plain")
    except Exception as e:
        ark_logger.error(f"Erreur endpoint /metrics: {e}", extra={"arkalia_module": "helloria"})
        raise HTTPException(status_code=500, detail="Erreur métriques Helloria") from e


def _get_fallback_metrics() -> dict:
    """Métriques de base sans dépendances externes"""
    # Vérifications de base
    critical_files = {
        "utils/io_safe.py": Path("utils/io_safe.py").exists(),
        "modules/assistantia/security/prompt_validator.py": Path(
            "modules/assistantia/security/prompt_validator.py"
        ).exists(),
        "modules/zeroia/reason_loop.py": Path("modules/zeroia/reason_loop.py").exists(),
        "modules/reflexia/core.py": Path("modules/reflexia/core.py").exists(),
        "modules/sandozia/core/sandozia_core.py": Path(
            "modules/sandozia/core/sandozia_core.py"
        ).exists(),
        "modules/nyxalia/core.py": Path("modules/nyxalia/core.py").exists(),
        "modules/taskia/core.py": Path("modules/taskia/core.py").exists(),
    }

    # Lecture état ZeroIA si disponible (synchrone - fonction non async)
    zeroia_confidence = 0.0
    try:
        dashboard_path = Path("state/zeroia_dashboard.json")
        if dashboard_path.exists():
            with open(dashboard_path, encoding="utf-8") as f:
                dashboard = json.load(f)
                zeroia_confidence = dashboard.get("confidence", 0.0)
    except Exception:  # nosec B110
        pass

    # Lecture métriques ReflexIA si disponibles
    reflexia_cpu = 0.0
    reflexia_ram = 0.0
    try:
        import toml

        reflexia_path = Path("state/reflexia_state.toml")
        if reflexia_path.exists():
            reflexia_data = toml.load(reflexia_path)
            metrics = reflexia_data.get("metrics", {})
            reflexia_cpu = metrics.get("cpu", 0.0)
            reflexia_ram = metrics.get("ram", 0.0)
    except Exception:  # nosec B110
        pass

    # 🔥 NOUVELLES MÉTRIQUES - Modules supplémentaires
    # État Sandozia
    sandozia_active = 0
    try:
        sandozia_state = Path("state/sandozia")
        sandozia_active = 1 if sandozia_state.exists() else 0
    except Exception as e:
        # En cas d'erreur, on logge au lieu de passer silencieusement
        ark_logger.warning(
            f"Sandozia state check failed: {e}", extra={"arkalia_module": "helloria"}
        )

    # État AssistantIA
    assistantia_active = 0
    try:
        assistantia_state = Path("modules/assistantia/core.py")
        assistantia_active = 1 if assistantia_state.exists() else 0
    except Exception as e:
        ark_logger.warning(
            f"AssistantIA state check failed: {e}", extra={"arkalia_module": "helloria"}
        )

    # État Nyxalia
    nyxalia_active = 0
    try:
        nyxalia_state = Path("modules/nyxalia/core.py")
        nyxalia_active = 1 if nyxalia_state.exists() else 0
    except Exception as e:
        ark_logger.warning(f"Nyxalia state check failed: {e}", extra={"arkalia_module": "helloria"})

    # État Taskia
    taskia_active = 0
    try:
        taskia_state = Path("modules/taskia/core.py")
        taskia_active = 1 if taskia_state.exists() else 0
    except Exception as e:
        ark_logger.warning(f"Taskia state check failed: {e}", extra={"arkalia_module": "helloria"})

    return {
        "arkalia_system_health": 1 if all(critical_files.values()) else 0,
        "arkalia_critical_files_count": sum(critical_files.values()),
        "arkalia_zeroia_confidence": zeroia_confidence,
        "arkalia_reflexia_cpu_percent": reflexia_cpu,
        "arkalia_reflexia_ram_percent": reflexia_ram,
        "arkalia_sandozia_active": sandozia_active,
        "arkalia_assistantia_active": assistantia_active,
        "arkalia_nyxalia_active": nyxalia_active,
        "arkalia_taskia_active": taskia_active,
        "arkalia_api_uptime_seconds": time.time(),
        "arkalia_endpoints_available": 4,  # /, /chat, /metrics, /zeroia/status
    }


def _convert_to_prometheus_format(metrics_dict: dict) -> str:
    """Convertit un dict de métriques en format Prometheus"""
    lines = []

    for metric_name, value in metrics_dict.items():
        if isinstance(value, int | float):
            lines.append(f"# HELP {metric_name} Métrique Arkalia-LUNA")
            lines.append(f"# TYPE {metric_name} gauge")
            lines.append(f"{metric_name} {value}")
        elif isinstance(value, str):
            # Métriques textuelles converties en info
            lines.append(f"# HELP {metric_name}_info Information textuelle")
            lines.append(f"# TYPE {metric_name}_info gauge")
            lines.append(f'{metric_name}_info{{value="{value}"}} 1')

    return "\n".join(lines) + "\n"


# 🚀 Application FastAPI
app = FastAPI(
    title="Arkalia-LUNA API",
    version="v2.1.1",
    description="API principale des modules IA Arkalia",
)

# 🧩 Inclusion des routers
app.include_router(router)
app.include_router(reflexia_router)
# app.include_router(zeroia_router, prefix="/zeroia")  # Module supprimé


@app.get("/health")
def health() -> dict:
    """Endpoint de santé générale du système.

    Returns:
        dict: Statut de santé du système.
    """
    return {"status": "ok"}


@app.get("/zeroia/health", tags=["ZeroIA"])
def zeroia_health() -> dict:
    """Vérifie l'état de santé du module ZeroIA.

    Returns:
        dict: Statut de santé de ZeroIA.
    """
    try:
        from modules.zeroia import health_check

        return health_check()
    except Exception as e:
        ark_logger.error(f"Erreur ZeroIA health: {e}", extra={"arkalia_module": "helloria"})
        return {"status": "error", "error": "internal_error"}


@app.get("/reflexia/health", tags=["ReflexIA"])
def reflexia_health() -> dict:
    """Vérifie l'état de santé du module Reflexia.

    Returns:
        dict: Statut de santé de Reflexia.
    """
    try:
        # Vérification simple de l'état ReflexIA
        reflexia_state = Path("state/reflexia_state.toml")
        if reflexia_state.exists():
            return {"status": "active", "module": "reflexia"}
        else:
            return {"status": "inactive", "module": "reflexia"}
    except Exception as e:
        ark_logger.error(f"Erreur ReflexIA health: {e}", extra={"arkalia_module": "helloria"})
        return {"status": "error", "error": "internal_error"}


@app.get("/sandozia/health", tags=["Sandozia"])
def sandozia_health() -> dict:
    """Vérifie l'état de santé du module Sandozia.

    Returns:
        dict: Statut de santé de Sandozia.
    """
    try:
        # Vérification simple de l'état Sandozia
        sandozia_state = Path("state/sandozia")
        if sandozia_state.exists():
            return {"status": "active", "module": "sandozia"}
        else:
            return {"status": "inactive", "module": "sandozia"}
    except Exception as e:
        ark_logger.error(f"Erreur Sandozia health: {e}", extra={"arkalia_module": "helloria"})
        return {"status": "error", "error": "internal_error"}


@app.get("/zeroia/status", tags=["ZeroIA"])
async def zeroia_status() -> dict[str, Any]:
    """Récupère le statut détaillé du module ZeroIA (async optimisé).

    Returns:
        dict: Statut détaillé de ZeroIA depuis le dashboard.
    """
    try:
        dashboard_path = Path("state/zeroia_dashboard.json")
        if not dashboard_path.exists():
            return {"status": "error", "error": "dashboard file not found"}

        try:
            import aiofiles  # type: ignore

            async with aiofiles.open(dashboard_path, encoding="utf-8") as f:
                content = await f.read()
                data = json.loads(content)
                if isinstance(data, dict):
                    return data
                return {"status": "error", "error": "invalid dashboard format"}
        except ImportError:
            # Fallback sans bloquer l'event-loop
            data = await asyncio.to_thread(_read_json_dashboard, dashboard_path)
            return data
    except Exception as e:
        ark_logger.error(f"Erreur ZeroIA status: {e}", extra={"arkalia_module": "helloria"})
        return {"status": "error", "error": "internal_error"}


@app.post("/echo", tags=["Test"], response_model=None)
async def echo(request: Request) -> dict[str, Any] | JSONResponse:
    """Endpoint de test echo"""
    try:
        data = await request.json()
        message = data.get("message", "").strip()

        if not message:
            return JSONResponse(status_code=400, content={"error": "Message vide."})

        return {"echo": message}

    except Exception as e:
        ark_logger.error(f"Erreur endpoint /echo: {e}", extra={"arkalia_module": "helloria"})
        return JSONResponse(status_code=500, content={"error": "Erreur interne Helloria"})


def _get_metrics() -> dict:
    """Implementation of _get_metrics function"""
    return _get_fallback_metrics()

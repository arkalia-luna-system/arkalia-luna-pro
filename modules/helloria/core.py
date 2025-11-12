"""
Module core Helloria - API principale d'Arkalia-LUNA Pro.

Ce module expose l'API FastAPI principale avec les endpoints de santé
pour tous les modules IA (ZeroIA, Reflexia, Sandozia).
"""

import json
import logging
import time
from pathlib import Path
from typing import Any, Union

import psutil
from fastapi import APIRouter, FastAPI, Request, Response
from fastapi.responses import JSONResponse, PlainTextResponse

# 📦 Import des routes externes (modules IA)
from modules.reflexia.core_api import router as reflexia_router

# from modules.zeroia.core import router as zeroia_router  # Module supprimé lors de la refactorisation

# from modules.monitoring.prometheus_metrics import get_metrics_summary  # Module supprimé

# 🚦 Router principal
router = APIRouter()
logger = logging.getLogger(__name__)

# 🧾 Logging d'erreurs
logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="app_errors.log",
)


# 🎯 Endpoint principal IA
@router.post("/chat", tags=["IA"], response_model=None)
async def chat(request: Request) -> dict[str, Any] | JSONResponse:
    try:
        data = await request.json()
        prompt = data.get("message", "").strip()

        if not prompt:
            return JSONResponse(status_code=400, content={"error": "Aucun message reçu."})

        # Placeholder IA
        response_text = f"Tu as dit : '{prompt}' (réponse IA à coder 🎯)"
        return {"réponse": response_text}

    except Exception as e:
        logging.error(f"Erreur interne : {str(e)}")
        raise Exception(f"Erreur Helloria: {e}") from e


# 🌐 Racine API
@router.get("/", tags=["Root"])
async def root() -> dict:
    return {"message": "Arkalia-LUNA API active"}


# 📊 Endpoint statut détaillé
@router.get("/status", tags=["Status"])
async def status() -> dict:
    """Statut détaillé de l'API avec métriques système"""
    # Métriques système
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

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
async def metrics() -> PlainTextResponse:
    """
    Endpoint Prometheus pour exposition des métriques Arkalia-LUNA
    Format: OpenMetrics/Prometheus standard
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
        logging.error(f"Erreur endpoint /metrics: {e}")
        raise Exception(f"Erreur Helloria: {e}") from e


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

    # Lecture état ZeroIA si disponible
    zeroia_confidence = 0.0
    try:
        dashboard_path = Path("state/zeroia_dashboard.json")
        if dashboard_path.exists():
            with open(dashboard_path) as f:
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
        logger.warning(f"Sandozia state check failed: {e}")

    # État AssistantIA
    assistantia_active = 0
    try:
        assistantia_state = Path("modules/assistantia/core.py")
        assistantia_active = 1 if assistantia_state.exists() else 0
    except Exception as e:
        logger.warning(f"AssistantIA state check failed: {e}")

    # État Nyxalia
    nyxalia_active = 0
    try:
        nyxalia_state = Path("modules/nyxalia/core.py")
        nyxalia_active = 1 if nyxalia_state.exists() else 0
    except Exception as e:
        logger.warning(f"Nyxalia state check failed: {e}")

    # État Taskia
    taskia_active = 0
    try:
        taskia_state = Path("modules/taskia/core.py")
        taskia_active = 1 if taskia_state.exists() else 0
    except Exception as e:
        logger.warning(f"Taskia state check failed: {e}")

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
app.include_router(reflexia_router, prefix="/reflexia")
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
        return {"status": "error", "error": str(e)}


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
        return {"status": "error", "error": str(e)}


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
        return {"status": "error", "error": str(e)}


@app.get("/zeroia/status", tags=["ZeroIA"])
def zeroia_status() -> dict[str, Any]:
    """Récupère le statut détaillé du module ZeroIA.

    Returns:
        dict: Statut détaillé de ZeroIA depuis le dashboard.
    """
    try:
        with open("state/zeroia_dashboard.json") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
            return {"status": "error", "error": "invalid dashboard format"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


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
        return JSONResponse(status_code=500, content={"error": f"Erreur : {str(e)}"})


def _get_metrics() -> dict:
    """Implementation of _get_metrics function"""
    return _get_fallback_metrics()

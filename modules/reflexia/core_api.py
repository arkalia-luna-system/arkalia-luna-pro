"""
Module core_api.

Ce module fait partie du système Arkalia Luna Pro.
"""

# 📁 modules/reflexia/core_api.py

from fastapi import APIRouter, FastAPI
from fastapi.responses import JSONResponse, PlainTextResponse
from prometheus_client import CONTENT_TYPE_LATEST, Gauge, generate_latest

from .core import launch_reflexia_check

# Métriques Prometheus locales pour Reflexia
reflexia_cpu_usage = Gauge("reflexia_cpu_usage_percent", "Utilisation CPU reportée par ReflexIA")

reflexia_ram_usage = Gauge("reflexia_ram_usage_percent", "Utilisation RAM reportée par ReflexIA")

reflexia_latency = Gauge("reflexia_latency_ms", "Latence système reportée par ReflexIA")

# 🧩 Router Reflexia
router = APIRouter(
    prefix="/reflexia",
    tags=["Reflexia"],
)

app = FastAPI()
app.include_router(router)


def get_reflexia_status() -> dict:
    """
    Fonction testable indépendamment de l'API FastAPI.
    Retourne un dictionnaire avec les métriques du système.
    """
    result = launch_reflexia_check()
    return {"status": "ok", "metrics": result["metrics"]}


@router.get("/check")
async def check_reflexia_status():
    """
    ✅ Endpoint de vérification réflexive.
    Retourne l'état des métriques système (CPU, RAM, etc.)
    """
    try:
        return JSONResponse(content=get_reflexia_status())
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Erreur réflexive : {str(e)}"},
        )


@router.get("/metrics")
async def get_metrics():
    """
    📊 Endpoint métriques Prometheus pour Reflexia
    """
    try:
        # Collecter les métriques actuelles
        status_data = get_reflexia_status()
        metrics_data = status_data.get("metrics", {})

        # Mettre à jour les métriques Prometheus
        cpu = metrics_data.get("cpu", 0.0)
        ram = metrics_data.get("ram", 0.0)
        latency = metrics_data.get("latency", 0.0)

        reflexia_cpu_usage.set(cpu)
        reflexia_ram_usage.set(ram)
        reflexia_latency.set(latency)

        # Générer le format Prometheus
        prometheus_data = generate_latest()

        return PlainTextResponse(content=prometheus_data, media_type=CONTENT_TYPE_LATEST)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Erreur métriques : {str(e)}"},
        )


@app.get("/health")
async def health():
    try:
        return {"status": "ok", "service": "reflexia"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

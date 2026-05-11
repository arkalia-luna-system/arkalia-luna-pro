"""
Module core_api.

Ce module fait partie du système Arkalia Luna Pro.
"""

# 📁 modules/reflexia/core_api.py

import os
from typing import Any

from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException
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


def require_api_key(x_api_key: str | None = Header(default=None, alias="X-API-Key")) -> None:
    """Protège les endpoints sensibles via clé API si configurée."""
    expected = os.getenv("ARKALIA_API_KEY", "").strip()
    if not expected:
        return
    if x_api_key != expected:
        raise HTTPException(status_code=401, detail="Unauthorized")


def get_reflexia_status() -> dict:
    """
    Fonction testable indépendamment de l'API FastAPI.
    Retourne un dictionnaire avec les métriques du système.
    """
    result = launch_reflexia_check()
    return {"status": "ok", "metrics": result["metrics"]}


@router.get("/health", operation_id="reflexia_router_health")
async def reflexia_health() -> dict[str, str]:
    """
    Health check Reflexia sur le router monté sous /reflexia (API principale + CI).

    Returns:
        dict: Statut de santé du module Reflexia.
    """
    try:
        return {"status": "ok", "service": "reflexia", "module": "reflexia"}
    except Exception:
        return {"status": "unhealthy", "error": "internal_error"}


@router.get("/check")
async def check_reflexia_status(_: None = Depends(require_api_key)) -> JSONResponse:
    """
    Endpoint de vérification réflexive.

    Retourne l'état des métriques système (CPU, RAM, latence) collectées par Reflexia.

    Returns:
        JSONResponse: Statut avec métriques système.

    Examples:
        >>> GET /reflexia/check
        >>> {
        ...     "status": "ok",
        ...     "metrics": {
        ...         "cpu": 45.2,
        ...         "ram": 67.8,
        ...         "latency": 120.5
        ...     }
        ... }
    """
    try:
        return JSONResponse(content=get_reflexia_status())
    except Exception:
        return JSONResponse(
            status_code=500,
            content={"error": "internal_error"},
        )


@router.get("/metrics")
async def get_metrics(_: None = Depends(require_api_key)) -> PlainTextResponse | JSONResponse:
    """
    Endpoint métriques Prometheus pour Reflexia.

    Retourne les métriques Reflexia au format Prometheus pour le scraping.

    Returns:
        PlainTextResponse: Métriques Prometheus au format texte.
        JSONResponse: Erreur en JSON si problème.

    Examples:
        >>> GET /reflexia/metrics
        >>> # reflexia_cpu_usage_percent 45.2
        >>> # reflexia_ram_usage_percent 67.8
        >>> # reflexia_latency_ms 120.5
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
    except Exception:
        return JSONResponse(
            status_code=500,
            content={"error": "internal_error"},
        )


@app.get("/health")
async def health() -> dict[str, str]:
    """
    Health check pour le service Reflexia.

    Vérifie que le service Reflexia est opérationnel.

    Returns:
        dict: Statut de santé du service Reflexia.

    Examples:
        >>> GET /health
        >>> {"status": "ok", "service": "reflexia"}
    """
    try:
        return {"status": "ok", "service": "reflexia"}
    except Exception:
        return {"status": "unhealthy", "error": "internal_error"}

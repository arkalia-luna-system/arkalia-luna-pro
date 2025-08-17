#!/usr/bin/env python3

"""
🚀 Lancement du serveur FastAPI pour ReflexIA

Ce script démarre :
1. Le serveur FastAPI qui expose les endpoints de ReflexIA

Endpoints exposés :
- /health : État de santé du service
- /metrics : Métriques système
- /status : État actuel du système
- /snapshot : Dernier snapshot sauvegardé
"""

import uvicorn
from fastapi import FastAPI

from modules.reflexia.core import get_metrics, launch_reflexia_check

app = FastAPI(
    title="ReflexIA API",
    description="API REST pour le module réflexif d'Arkalia",
    version="2.6.0",
)


@app.get("/health")
async def health_check() -> dict:
    """Endpoint de santé pour le healthcheck Docker"""
    return {"status": "healthy"}


@app.get("/metrics")
async def get_system_metrics() -> dict:
    """Retourne les métriques système actuelles"""
    return get_metrics()


@app.get("/status")
async def get_system_status() -> dict:
    """Lance une vérification réflexive et retourne le statut"""
    return launch_reflexia_check()


if __name__ == "__main__":
    # Démarrer le serveur FastAPI
    uvicorn.run(
        app, host="0.0.0.0", port=8002
    )  # Interface accessible depuis l'extérieur du conteneur

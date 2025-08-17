#!/usr/bin/env python3

"""
🚀 Lancement du serveur FastAPI et de la boucle réflexive pour ReflexIA

Ce script démarre :
1. Le serveur FastAPI qui expose les endpoints de ReflexIA
2. La boucle réflexive qui surveille le système en continu

Endpoints exposés :
- /health : État de santé du service
- /metrics : Métriques système
- /status : État actuel du système
- /snapshot : Dernier snapshot sauvegardé
"""

import threading

import uvicorn
from fastapi import FastAPI

from modules.reflexia.core import get_metrics, launch_reflexia_check, launch_reflexia_loop

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


def run_reflexia_loop() -> None:
    """Lance la boucle réflexive dans un thread séparé"""
    launch_reflexia_loop()


if __name__ == "__main__":
    # Démarrer la boucle réflexive dans un thread séparé
    reflexia_thread = threading.Thread(target=run_reflexia_loop)
    reflexia_thread.daemon = True  # Le thread s'arrêtera quand le programme principal s'arrête
    reflexia_thread.start()

    # Démarrer le serveur FastAPI dans le thread principal
    uvicorn.run(
        app, host="127.0.0.1", port=8002
    )  # nosec B104 - Interface locale pour développement

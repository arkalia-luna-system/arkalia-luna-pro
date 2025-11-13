#!/usr/bin/env python3
# 🧠 modules/sandozia/core/sandozia_core.py
# SandoziaCore - Orchestrateur Intelligence Croisée

"""
SandoziaCore - Orchestrateur Principal Sandozia

⚠️ FICHIER DE COMPATIBILITÉ - Ce fichier réexporte depuis modules/sandozia/core/sandozia/
Pour de nouveaux imports, utilisez directement : from modules.sandozia.core.sandozia import ...

Refactorisé en sous-modules pour améliorer la maintenabilité :
- sandozia/metrics.py : SandoziaMetrics
- sandozia/snapshot.py : IntelligenceSnapshot
- sandozia/core.py : SandoziaCore
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Any

# Ajout FastAPI pour endpoint /metrics
from fastapi import FastAPI
from fastapi.responses import JSONResponse, PlainTextResponse
from prometheus_client import CONTENT_TYPE_LATEST, Gauge, generate_latest

from core.ark_logger import ark_logger

# Réexport depuis sous-modules
from .sandozia import IntelligenceSnapshot, SandoziaCore, SandoziaMetrics

# Alias pour compatibilité
__all__ = ["SandoziaCore", "SandoziaMetrics", "IntelligenceSnapshot", "app", "get_metrics", "main"]


# === Métriques Prometheus pour Sandozia ===
# Gestion simple des métriques avec try/except pour éviter les doublons


class MockGauge:
    """
    Classe MockGauge.

    Cette classe fait partie du système Arkalia Luna Pro.
    """

    def set(self, value: float) -> None:
        """
        Fonction set.

        Cette fonction fait partie du système Arkalia Luna Pro.
        """
        pass


sandozia_uptime: Gauge | MockGauge
sandozia_coherence_score: Gauge | MockGauge

try:
    sandozia_uptime = Gauge(
        "sandozia_uptime_seconds", "Temps de fonctionnement de Sandozia (secondes)"
    )
    sandozia_coherence_score = Gauge(
        "sandozia_coherence_score", "Score de cohérence inter-modules Sandozia"
    )
except ValueError:
    # Les métriques existent déjà, on crée des objets mock pour éviter les erreurs
    sandozia_uptime = MockGauge()
    sandozia_coherence_score = MockGauge()

# === FastAPI app ===
app = FastAPI()


@app.get("/metrics")
async def get_metrics() -> Any:
    """
    📊 Endpoint métriques Prometheus pour Sandozia
    """
    try:
        # Mettre à jour les métriques
        core = SandoziaCore()
        uptime = (
            (datetime.now() - core.metrics_history[0].timestamp).total_seconds()
            if core.metrics_history
            else 0
        )
        sandozia_uptime.set(uptime)
        if core.metrics_history:
            sandozia_coherence_score.set(core.metrics_history[-1].coherence_score)
        prometheus_data = generate_latest()
        return PlainTextResponse(content=prometheus_data, media_type=CONTENT_TYPE_LATEST)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Erreur métriques : {str(e)}"},
        )


# Fonction helper pour CLI
async def main() -> None:
    """Point d'entrée CLI pour Sandozia"""
    import argparse

    parser = argparse.ArgumentParser(description="Sandozia Intelligence Croisée")
    parser.add_argument("--start", action="store_true", help="Démarrer le monitoring")
    parser.add_argument("--status", action="store_true", help="Afficher le statut")
    parser.add_argument("--config", type=str, help="Chemin config custom")

    args = parser.parse_args()

    sandozia = SandoziaCore(config_path=Path(args.config) if args.config else None)

    if args.status:
        status = sandozia.get_current_status()
        ark_logger.info(json.dumps(status, indent=2, extra={"module": "core"}))
        return

    if args.start:
        ark_logger.info("🧠 Starting Sandozia Intelligence Croisée...", extra={"module": "core"})
        await sandozia.start_monitoring()

        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            ark_logger.info("\n🛑 Stopping Sandozia...", extra={"module": "core"})
            await sandozia.stop_monitoring()


if __name__ == "__main__":
    asyncio.run(main())

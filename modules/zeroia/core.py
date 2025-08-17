#!/usr/bin/env python3

"""
🧠 modules/zeroia/core.py
ZeroIA Core - Point d'entrée principal du système de raisonnement

Module core simplifié qui délègue aux composants enhanced spécialisés.
"""

from core.ark_logger import ark_logger
import asyncio
import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import toml
from fastapi import APIRouter, FastAPI
from fastapi.responses import JSONResponse, PlainTextResponse
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, generate_latest

from .circuit_breaker import CircuitBreaker
from .reason_loop_enhanced import (
    initialize_components_with_recovery,
    reason_loop_enhanced_with_recovery,
)

# Métriques Prometheus locales pour ZeroIA
zeroia_decisions_total = Counter(
    "zeroia_decisions_total",
    "Nombre total de décisions ZeroIA",
    ["decision_type", "confidence_level"],
)

zeroia_confidence_score = Gauge(
    "zeroia_confidence_score", "Score de confiance de la dernière décision ZeroIA"
)

zeroia_circuit_breaker_state = Gauge(
    "zeroia_circuit_breaker_state",
    "État du circuit breaker (0=closed, 1=open, 2=half_open)",
    ["state_name"],
)

zeroia_event_store_events = Gauge(
    "zeroia_event_store_events_total",
    "Nombre total d'événements dans l'event store",
    ["event_type"],
)

zeroia_decision_duration = Gauge(
    "zeroia_decision_duration_seconds",
    "Durée de la dernière décision en secondes",
)

logger = logging.getLogger(__name__)

# === ROUTER ZEROIA ===
router = APIRouter(prefix="/zeroia", tags=["ZeroIA"])

app = FastAPI()
app.include_router(router)


# === CORE ZEROIA ===
class ZeroIACore:
    """🧠 Core ZeroIA - Système de décision intelligent"""

    def __init__(self):
        self.circuit_breaker = CircuitBreaker()
        self.state_path = Path("state/zeroia_state.toml")
        self.dashboard_path = Path("state/zeroia_dashboard.json")

        # Initialisation
        self._ensure_state_files()
        self._load_state()

    def _ensure_state_files(self):
        """Assure l'existence des fichiers d'état"""
        self.state_path.parent.mkdir(exist_ok=True)

        if not self.state_path.exists():
            initial_state = {
                "last_decision": "unknown",
                "confidence_score": 0.0,
                "reasoning_loop_active": False,
                "circuit_breaker_state": "closed",
                "last_update": datetime.now().isoformat(),
            }
            toml.dump(initial_state, self.state_path)

        if not self.dashboard_path.exists():
            initial_dashboard = {
                "last_decision": "unknown",
                "confidence": 0.0,
                "reasoning_loop_active": False,
                "circuit_breaker_status": "closed",
                "last_update": datetime.now().isoformat(),
            }
            with open(self.dashboard_path, "w") as f:
                json.dump(initial_dashboard, f, indent=2)

    def _load_state(self):
        """Charge l'état depuis les fichiers"""
        try:
            if self.state_path.exists():
                self.state = toml.load(self.state_path)
            else:
                self.state = {}
        except Exception as e:
            logger.error(f"Erreur chargement état ZeroIA: {e}")
            self.state = {}

    def _save_state(self):
        """Sauvegarde l'état dans les fichiers"""
        try:
            toml.dump(self.state, self.state_path)

            # Mise à jour dashboard JSON
            dashboard_data = {
                "last_decision": self.state.get("last_decision", "unknown"),
                "confidence": self.state.get("confidence_score", 0.0),
                "reasoning_loop_active": self.state.get("reasoning_loop_active", False),
                "circuit_breaker_status": self.state.get("circuit_breaker_state", "closed"),
                "last_update": datetime.now().isoformat(),
            }
            with open(self.dashboard_path, "w") as f:
                json.dump(dashboard_data, f, indent=2)

        except Exception as e:
            logger.error(f"Erreur sauvegarde état ZeroIA: {e}")

    async def make_decision(self, context: str) -> dict[str, Any]:
        """Prend une décision basée sur le contexte"""
        try:
            # Vérifier circuit breaker
            if not self.circuit_breaker.can_execute():
                logger.warning("Circuit breaker ouvert - décision différée")
                return {"decision": "deferred", "confidence": 0.0, "reason": "circuit_breaker_open"}

            # Exécuter le reason loop
            start_time = time.time()
            decision_result = await self.reason_loop.process_context(context)
            duration = time.time() - start_time

            # Enregistrer métriques
            decision = decision_result.get("decision", "unknown")
            confidence = decision_result.get("confidence", 0.0)

            zeroia_decisions_total.labels(decision_type=decision, confidence_level=confidence).inc()
            zeroia_confidence_score.set(confidence)

            # Mettre à jour l'état
            self.state.update(
                {
                    "last_decision": decision,
                    "confidence_score": confidence,
                    "reasoning_loop_active": True,
                    "circuit_breaker_state": self.circuit_breaker.state.value,
                    "last_update": datetime.now().isoformat(),
                }
            )
            self._save_state()

            # Circuit breaker success
            self.circuit_breaker.record_success()

            return decision_result

        except Exception as e:
            logger.error(f"Erreur décision ZeroIA: {e}")
            self.circuit_breaker.record_failure()
            zeroia_decisions_total.labels(decision_type="error", confidence_level="high").inc()

            return {"decision": "error", "confidence": 0.0, "reason": str(e)}

    def get_status(self) -> dict[str, Any]:
        """Retourne le statut actuel de ZeroIA"""
        return {
            "status": "active",
            "last_decision": self.state.get("last_decision", "unknown"),
            "confidence": self.state.get("confidence_score", 0.0),
            "circuit_breaker": self.circuit_breaker.state.value,
            "reasoning_loop_active": self.state.get("reasoning_loop_active", False),
            "last_update": self.state.get("last_update", "unknown"),
        }


# Instance globale
zeroia_core = ZeroIACore()

# === ENDPOINTS API ===


@router.get("/status")
async def get_zeroia_status():
    """Retourne le statut de ZeroIA"""
    return zeroia_core.get_status()


@router.post("/decision")
async def make_decision(context: str):
    """Prend une décision basée sur le contexte"""
    result = await zeroia_core.make_decision(context)
    return result


@app.get("/health")
def health():
    """Health check"""
    return {"status": "ok", "module": "zeroia"}


@app.get("/metrics")
async def get_metrics():
    """
    📊 Endpoint métriques Prometheus pour ZeroIA
    """
    try:
        # Mettre à jour les métriques avec l'état actuel
        status = zeroia_core.get_status()
        confidence = status.get("confidence", 0.0)
        zeroia_confidence_score.set(confidence)

        # Générer le format Prometheus
        prometheus_data = generate_latest()

        return PlainTextResponse(content=prometheus_data, media_type=CONTENT_TYPE_LATEST)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Erreur métriques : {str(e)}"},
        )


@router.get("/metrics")
async def get_metrics():
    """
    📊 Endpoint métriques Prometheus pour ZeroIA
    """
    try:
        # Récupérer l'état actuel
        cb, es, _, _ = initialize_components_with_recovery()
        
        # Mettre à jour les métriques du circuit breaker
        cb_status = cb.get_status()
        state_name = cb_status["state"].value
        zeroia_circuit_breaker_state.labels(state_name=state_name).set(1)
        
        # Mettre à jour les métriques de l'event store
        analytics = es.get_analytics()
        for event_type, count in analytics.get("events_by_type", {}).items():
            zeroia_event_store_events.labels(event_type=event_type).set(count)
        
        # Lire le dashboard pour les métriques récentes
        dashboard_path = Path("state/zeroia_dashboard.json")
        if dashboard_path.exists():
            try:
                with open(dashboard_path) as f:
                    dashboard = json.load(f)
                
                confidence = dashboard.get("confidence", 0.0)
                zeroia_confidence_score.set(confidence)
                
                # Mettre à jour les métriques de décision
                decision = dashboard.get("last_decision", "unknown")
                if decision != "unknown":
                    zeroia_decisions_total.labels(
                        decision_type=decision,
                        confidence_level="high" if confidence > 0.7 else "medium" if confidence > 0.4 else "low"
                    ).inc()
                    
            except Exception as e:
                logger.warning(f"Erreur lecture dashboard: {e}")
        
        # Générer le format Prometheus
        prometheus_data = generate_latest()
        
        return PlainTextResponse(content=prometheus_data, media_type=CONTENT_TYPE_LATEST)
        
    except Exception as e:
        logger.error(f"Erreur métriques ZeroIA: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Erreur métriques : {str(e)}"},
        )


# Instance globale (singleton pattern simple)
_zeroia_core_instance: ZeroIACore | None = None


def get_zeroia_core() -> ZeroIACore:
    """
    Retourne l'instance singleton de ZeroIA Core

    Returns:
        ZeroIACore: Instance du core
    """
    global _zeroia_core_instance

    if _zeroia_core_instance is None:
        _zeroia_core_instance = ZeroIACore()

    return _zeroia_core_instance


def quick_decision(context_path: Path | None = None) -> tuple[str, float]:
    """
    Interface rapide pour une décision ZeroIA

    Args:
        context_path: Chemin vers le contexte (optionnel)

    Returns:
        tuple[str, float]: (décision, score_confiance)
    """
    core = get_zeroia_core()

    if not core.initialized:
        core.initialize()

    return core.run_decision_cycle(context_path)


def health_check() -> dict:
    """
    Vérifie l'état de santé du core ZeroIA

    Returns:
        Dict: État de santé détaillé
    """
    try:
        core = get_zeroia_core()
        return core.get_status()
    except Exception as e:
        return {"status": "critical_error", "error": str(e), "initialized": False}


if __name__ == "__main__":
    # Test rapide du core
    ark_logger.info("🧠 ZeroIA Core - Test de démarrage", extra={"module": "zeroia"})

    core = get_zeroia_core()

    if core.initialize():
        ark_logger.info("✅ Initialisation réussie", extra={"module": "zeroia"})

        decision, confidence = core.run_decision_cycle()
        ark_logger.info(f"🎯 Décision: {decision} (confiance: {confidence:.2f}, extra={"module": "zeroia"})")

        status = core.get_status()
        ark_logger.info(f"📊 État: {status['status']}", extra={"module": "zeroia"})
    else:
        ark_logger.info("❌ Échec initialisation", extra={"module": "zeroia"})

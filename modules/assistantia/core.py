"""
Module core.

Ce module fait partie du système Arkalia Luna Pro.
"""

import asyncio
import json
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import requests
from fastapi import APIRouter, BackgroundTasks, Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest
from pydantic import BaseModel, Field

from core.ark_logger import ark_logger

from .utils.ollama_connector import check_ollama_health
from .utils.ollama_connector import query_ollama as real_query_ollama
from .utils.processing import process_input


def _check_ollama_health() -> bool:
    return check_ollama_health()


# Métriques Prometheus locales pour AssistantIA
assistantia_prompts_total = Counter(
    "assistantia_prompts_total",
    "Nombre total de prompts traités par AssistantIA",
    ["status", "security_level", "model"],
)

assistantia_response_time = Histogram(
    "assistantia_response_time_seconds",
    "Temps de réponse AssistantIA",
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0],
)

assistantia_active_connections = Gauge(
    "assistantia_active_connections", "Nombre de connexions actives à AssistantIA"
)

assistantia_context_quality = Gauge(
    "assistantia_context_quality_score", "Score de qualité du contexte Arkalia (0-100)"
)

router = APIRouter()


class MessageInput(BaseModel):
    """
    Classe MessageInput.

    Cette classe fait partie du système Arkalia Luna Pro.
    """

    message: str = Field(..., min_length=1, max_length=2000, description="Message utilisateur")
    model: str | None = Field(default="mistral:latest", description="Modèle IA à utiliser")
    temperature: float | None = Field(
        default=0.7, ge=0.0, le=2.0, description="Température de génération"
    )
    include_context: bool | None = Field(default=True, description="Inclure le contexte Arkalia")


class ChatResponse(BaseModel):
    """
    Classe ChatResponse.

    Cette classe fait partie du système Arkalia Luna Pro.
    """

    response: str
    model_used: str
    processing_time: float
    context_quality: float
    arkalia_context: str | None = None


class HealthResponse(BaseModel):
    """
    Classe HealthResponse.

    Cette classe fait partie du système Arkalia Luna Pro.
    """

    status: str
    ollama_available: bool
    arkalia_modules: dict[str, str]
    uptime: str
    version: str = "2.8.0"


# Variables globales pour le suivi
startup_time = datetime.now()
active_connections = 0


def get_query_ollama() -> Callable[[str, str, float], str]:
    """
    Retourne une fonction de requête Ollama.

    Returns:
        Callable: Fonction lambda pour interroger Ollama avec prompt, model et température.
    """
    return lambda prompt, model, temp: real_query_ollama(prompt, model, temp)


async def get_arkalia_context() -> tuple[str, float]:
    """Récupère le contexte des autres modules Arkalia avec score de qualité"""
    context_parts = []
    quality_score = 0.0
    max_score = 100.0

    try:
        # État ZeroIA
        zeroia_dashboard = Path("state/zeroia_dashboard.json")
        if zeroia_dashboard.exists():
            try:
                with open(zeroia_dashboard) as f:
                    dashboard = json.load(f)
                status = dashboard.get("last_decision", "unknown")
                context_parts.append(f"ZeroIA: {status}")
                quality_score += 25.0 if status != "unknown" else 10.0
            except (json.JSONDecodeError, KeyError, OSError) as e:
                logger.warning(f"Erreur lecture ZeroIA: {e}")
                context_parts.append("ZeroIA: error")
                quality_score += 5.0
        else:
            context_parts.append("ZeroIA: inactive")
            quality_score += 2.0
    except Exception as e:
        logger.error(f"Erreur contexte ZeroIA: {e}")
        context_parts.append("ZeroIA: unavailable")

    try:
        # État Reflexia
        reflexia_state = Path("state/reflexia_state.toml")
        if reflexia_state.exists():
            try:
                import toml

                reflexia_data = toml.load(reflexia_state)
                status = reflexia_data.get("status", "unknown")
                context_parts.append(f"Reflexia: {status}")
                quality_score += 25.0 if status != "unknown" else 10.0
            except Exception as e:
                logger.warning(f"Erreur lecture Reflexia: {e}")
                context_parts.append("Reflexia: error")
                quality_score += 5.0
        else:
            context_parts.append("Reflexia: inactive")
            quality_score += 2.0
    except Exception as e:
        logger.error(f"Erreur contexte Reflexia: {e}")
        context_parts.append("Reflexia: unavailable")

    try:
        # État Sandozia
        sandozia_state = Path("state/sandozia")
        if sandozia_state.exists() and any(sandozia_state.iterdir()):
            context_parts.append("Sandozia: active")
            quality_score += 25.0
        else:
            context_parts.append("Sandozia: inactive")
            quality_score += 2.0
    except Exception as e:
        logger.error(f"Erreur contexte Sandozia: {e}")
        context_parts.append("Sandozia: unavailable")

    try:
        # État Cognitive Reactor
        cognitive_state = Path("state/cognitive_reactor_state.toml")
        if cognitive_state.exists():
            try:
                import toml

                cognitive_data = toml.load(cognitive_state)
                status = cognitive_data.get("status", "unknown")
                context_parts.append(f"Cognitive: {status}")
                quality_score += 25.0 if status != "unknown" else 10.0
            except Exception as e:
                logger.warning(f"Erreur lecture Cognitive: {e}")
                context_parts.append("Cognitive: error")
                quality_score += 5.0
        else:
            context_parts.append("Cognitive: inactive")
            quality_score += 2.0
    except Exception as e:
        logger.error(f"Erreur contexte Cognitive: {e}")
        context_parts.append("Cognitive: unavailable")

    # Normaliser le score de qualité
    final_quality = min(quality_score, max_score)
    assistantia_context_quality.set(final_quality)

    context_str = " | ".join(context_parts) if context_parts else "Système Arkalia-LUNA"
    return context_str, final_quality


@router.post("/chat", response_model=ChatResponse)
async def post_chat(
    data: MessageInput,
    background_tasks: BackgroundTasks,
    query_ollama: Callable[[str, str, float], str] = Depends(get_query_ollama),
) -> ChatResponse:
    """Endpoint principal pour le chat avec AssistantIA"""
    global active_connections

    # Gestion des connexions actives
    active_connections += 1
    assistantia_active_connections.set(active_connections)

    try:
        start_time = asyncio.get_event_loop().time()
        message = data.message.strip()

        if not message:
            raise HTTPException(status_code=400, detail="Message vide")

        # Vérifier la santé d'Ollama
        if not _check_ollama_health():
            raise HTTPException(status_code=503, detail="Service IA temporairement indisponible")

        # Récupérer le contexte Arkalia si demandé
        arkalia_context = None
        context_quality = 0.0
        if data.include_context:
            arkalia_context, context_quality = await get_arkalia_context()
            enriched_message = f"{message}\n\nContexte système Arkalia-LUNA: {arkalia_context}"
        else:
            enriched_message = message

        # Prétraiter le message
        processed_message = process_input(enriched_message)

        # Appeler Ollama
        response = query_ollama(processed_message, data.model, data.temperature)

        # Calculer le temps de traitement
        processing_time = asyncio.get_event_loop().time() - start_time
        assistantia_response_time.observe(processing_time)

        # Enregistrer métriques de succès
        assistantia_prompts_total.labels(
            status="success", security_level="medium", model=data.model
        ).inc()

        # Tâche en arrière-plan pour le logging
        background_tasks.add_task(
            log_chat_interaction, message, response, processing_time, data.model
        )

        return ChatResponse(
            response=response,
            model_used=data.model,
            processing_time=processing_time,
            context_quality=context_quality,
            arkalia_context=arkalia_context if data.include_context else None,
        )

    except HTTPException:
        # Re-raise HTTPException
        raise
    except requests.exceptions.Timeout:
        assistantia_prompts_total.labels(
            status="timeout", security_level="medium", model=data.model
        ).inc()
        raise HTTPException(status_code=504, detail="Délai de réponse dépassé") from None
    except Exception as e:
        logger.error(f"Erreur AssistantIA: {e}")
        assistantia_prompts_total.labels(
            status="error", security_level="medium", model=data.model
        ).inc()
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}") from e
    finally:
        # Décrémenter les connexions actives
        active_connections = max(0, active_connections - 1)
        assistantia_active_connections.set(active_connections)


async def log_chat_interaction(message: str, response: str, processing_time: float, model: str):
    """Log l'interaction en arrière-plan"""
    try:
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "message_length": len(message),
            "response_length": len(response),
            "processing_time": processing_time,
            "model": model,
        }

        # Écrire dans le log d'AssistantIA
        log_file = Path("logs/assistantia_chat.log")
        log_file.parent.mkdir(exist_ok=True)

        with open(log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

    except Exception as e:
        logger.error(f"Erreur logging AssistantIA: {e}")


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Endpoint de santé avec informations détaillées"""
    try:
        # Vérifier Ollama
        ollama_available = check_ollama_health()

        # Récupérer l'état des modules Arkalia
        arkalia_modules = {}
        context_str, _ = await get_arkalia_context()

        # Parser le contexte pour extraire les états
        for part in context_str.split(" | "):
            if ":" in part:
                module, status = part.split(":", 1)
                arkalia_modules[module.strip()] = status.strip()

        # Calculer l'uptime
        uptime = str(datetime.now() - startup_time)

        return HealthResponse(
            status="healthy" if ollama_available else "degraded",
            ollama_available=ollama_available,
            arkalia_modules=arkalia_modules,
            uptime=uptime,
        )

    except Exception as e:
        logger.error(f"Erreur health check: {e}")
        return HealthResponse(
            status="unhealthy", ollama_available=False, arkalia_modules={}, uptime="unknown"
        )


@router.get("/metrics")
async def get_metrics():
    """📊 Endpoint métriques Prometheus pour AssistantIA"""
    try:
        prometheus_data = generate_latest()
        return PlainTextResponse(content=prometheus_data, media_type=CONTENT_TYPE_LATEST)
    except Exception as e:
        logger.error(f"Erreur métriques: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Erreur métriques : {str(e)}"},
        )


@router.get("/models")
async def get_available_models():
    """Récupère la liste des modèles disponibles"""
    try:
        from .utils.ollama_connector import get_available_models

        models = get_available_models()
        if models:
            return {"models": models.get("models", [])}
        else:
            return {"models": [], "error": "Impossible de récupérer les modèles"}
    except Exception as e:
        logger.error(f"Erreur récupération modèles: {e}")
        return JSONResponse(
            status_code=500, content={"error": f"Erreur récupération modèles: {str(e)}"}
        )


# Configuration FastAPI
app = FastAPI(
    title="AssistantIA - Interface IA Arkalia-LUNA",
    description="Interface conversationnelle IA intégrée à l'écosystème Arkalia-LUNA",
    version="2.8.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifier les domaines autorisés
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion du router
app.include_router(router, prefix="/api/v1", tags=["assistantia"])


# Routes racine
@app.get("/")
async def root():
    return {
        "service": "AssistantIA",
        "version": "2.8.0",
        "status": "active",
        "docs": "/docs",
        "health": "/health",
        "metrics": "/metrics",
    }

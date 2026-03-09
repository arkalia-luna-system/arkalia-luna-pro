"""
Module core.

Ce module fait partie du système Arkalia Luna Pro.
"""

import asyncio
import json
import os
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any

import requests
from fastapi import APIRouter, BackgroundTasks, Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest
from pydantic import BaseModel, Field

from core.ark_logger import ark_logger
from modules.memoria.service import MemoryRecord, get_vector_memory_service

from .config import load_assistantia_config
from .utils.ollama_connector import check_ollama_health
from .utils.ollama_connector import query_ollama as real_query_ollama
from .utils.processing import process_input


def _check_ollama_health() -> bool:
    # Marquer la config comme chargée dès le premier accès pour les métriques
    try:
        load_assistantia_config()
        assistantia_config_loaded.set(1.0)
    except Exception:  # pragma: no cover - protection ultime
        assistantia_config_loaded.set(0.0)

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

assistantia_memoria_enabled = Gauge(
    "assistantia_memoria_enabled", "Indique si Memoria est activée pour AssistantIA (0/1)"
)

assistantia_config_loaded = Gauge(
    "assistantia_config_loaded", "Indique si la configuration AssistantIA a été chargée (0/1)"
)

router = APIRouter()


class MessageInput(BaseModel):
    """
    Modèle d'entrée pour les messages de chat.

    Attributes:
        message: Message utilisateur à traiter (1-2000 caractères).
        model: Modèle IA à utiliser (défaut: "mistral:latest").
        temperature: Température de génération (0.0-2.0, défaut: 0.7).
        include_context: Inclure le contexte Arkalia dans la requête (défaut: True).

    Examples:
        >>> input_data = MessageInput(
        ...     message="Bonjour, comment ça va ?",
        ...     model="mistral:latest",
        ...     temperature=0.7,
        ...     include_context=True
        ... )
    """

    message: str = Field(..., min_length=1, max_length=2000, description="Message utilisateur")
    model: str | None = Field(default="mistral:latest", description="Modèle IA à utiliser")
    temperature: float | None = Field(
        default=0.7, ge=0.0, le=2.0, description="Température de génération"
    )
    include_context: bool | None = Field(default=True, description="Inclure le contexte Arkalia")
    user_id: str | None = Field(
        default=None,
        description=(
            "Identifiant utilisateur ou session pour la mémoire longue. "
            "Si non fourni, un identifiant par défaut est utilisé."
        ),
    )


class ChatResponse(BaseModel):
    """
    Modèle de réponse pour les messages de chat.

    Attributes:
        response: Réponse générée par le modèle IA.
        model_used: Nom du modèle utilisé pour générer la réponse.
        processing_time: Temps de traitement en secondes.
        context_quality: Score de qualité du contexte Arkalia (0-100).
        arkalia_context: Contexte Arkalia utilisé si demandé, None sinon.

    Examples:
        >>> response = ChatResponse(
        ...     response="Bonjour ! Je vais bien, merci.",
        ...     model_used="mistral:latest",
        ...     processing_time=0.5,
        ...     context_quality=85.0,
        ...     arkalia_context="ZeroIA: active | Reflexia: monitoring"
        ... )
    """

    response: str
    model_used: str
    processing_time: float
    context_quality: float
    arkalia_context: str | None = None


class HealthResponse(BaseModel):
    """
    Modèle de réponse pour le health check.

    Attributes:
        status: Statut du service ("healthy", "degraded", "unhealthy").
        ollama_available: Indique si Ollama est disponible.
        arkalia_modules: État des modules Arkalia (nom -> statut).
        uptime: Temps de fonctionnement depuis le démarrage.
        version: Version de l'API (défaut: "2.8.0").

    Examples:
        >>> health = HealthResponse(
        ...     status="healthy",
        ...     ollama_available=True,
        ...     arkalia_modules={"ZeroIA": "active", "Reflexia": "monitoring"},
        ...     uptime="2:30:15",
        ...     version="2.8.0"
        ... )
    """

    status: str
    ollama_available: bool
    arkalia_modules: dict[str, str]
    uptime: str
    version: str = "2.8.0"


# Variables globales pour le suivi
startup_time = datetime.now()
active_connections = 0


# Variable au niveau module pour éviter B008 (Depends dans argument par défaut)
_query_ollama_func: Callable[[str, str, float], str] | None = None
_memoria_enabled: bool | None = None


def _create_query_ollama_func() -> Callable[[str, str, float], str]:
    """Crée la fonction de requête Ollama."""

    def query_func(prompt: str, model: str, temp: float) -> str:
        return real_query_ollama(prompt, model, temp)

    return query_func


def get_query_ollama() -> Callable[[str, str, float], str]:
    """
    Retourne une fonction de requête Ollama.

    Returns:
        Callable: Fonction pour interroger Ollama avec prompt, model et température.
    """
    global _query_ollama_func
    if _query_ollama_func is None:
        _query_ollama_func = _create_query_ollama_func()
    return _query_ollama_func


def is_memoria_enabled() -> bool:
    """
    Indique si la mémoire vectorielle Memoria est activée.
    """
    global _memoria_enabled
    if _memoria_enabled is None:
        value = os.getenv("MEMORIA_ENABLED")
        if value is not None:
            _memoria_enabled = value.lower() in {"1", "true", "yes", "on"}
        else:
            cfg = load_assistantia_config()
            _memoria_enabled = cfg.memoria.enabled

        assistantia_memoria_enabled.set(1.0 if _memoria_enabled else 0.0)

    return _memoria_enabled


async def get_arkalia_context() -> tuple[str, float]:
    """
    Récupère le contexte des autres modules Arkalia avec score de qualité.

    Collecte l'état de tous les modules Arkalia (ZeroIA, Reflexia, Sandozia,
    Cognitive Reactor) et calcule un score de qualité du contexte.

    Returns:
        tuple[str, float]: Tuple contenant :
            - Contexte formaté (str) : "Module1: status | Module2: status"
            - Score de qualité (float) : Score entre 0 et 100

    Examples:
        >>> context, quality = await get_arkalia_context()
        >>> print(context)  # "ZeroIA: active | Reflexia: monitoring"
        >>> print(quality)  # 85.0
    """
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
                ark_logger.warning(
                    f"Erreur lecture ZeroIA: {e}", extra={"arkalia_module": "assistantia"}
                )
                context_parts.append("ZeroIA: error")
                quality_score += 5.0
        else:
            context_parts.append("ZeroIA: inactive")
            quality_score += 2.0
    except Exception as e:
        ark_logger.error(f"Erreur contexte ZeroIA: {e}", extra={"arkalia_module": "assistantia"})
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
                ark_logger.warning(
                    f"Erreur lecture Reflexia: {e}", extra={"arkalia_module": "assistantia"}
                )
                context_parts.append("Reflexia: error")
                quality_score += 5.0
        else:
            context_parts.append("Reflexia: inactive")
            quality_score += 2.0
    except Exception as e:
        ark_logger.error(f"Erreur contexte Reflexia: {e}", extra={"arkalia_module": "assistantia"})
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
        ark_logger.error(f"Erreur contexte Sandozia: {e}", extra={"arkalia_module": "assistantia"})
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
                ark_logger.warning(
                    f"Erreur lecture Cognitive: {e}", extra={"arkalia_module": "assistantia"}
                )
                context_parts.append("Cognitive: error")
                quality_score += 5.0
        else:
            context_parts.append("Cognitive: inactive")
            quality_score += 2.0
    except Exception as e:
        ark_logger.error(f"Erreur contexte Cognitive: {e}", extra={"arkalia_module": "assistantia"})
        context_parts.append("Cognitive: unavailable")

    # Normaliser le score de qualité
    final_quality = min(quality_score, max_score)
    assistantia_context_quality.set(final_quality)

    context_str = " | ".join(context_parts) if context_parts else "Système Arkalia-LUNA"
    return context_str, final_quality


def _build_memoria_user_id(data: MessageInput) -> str:
    """
    Construit un identifiant utilisateur pour la mémoire longue.

    Pour l'instant, on utilise un ID explicite si fourni, sinon un identifiant
    global par défaut.
    """
    if data.user_id and data.user_id.strip():
        return data.user_id.strip()
    return "default_user"


def _format_memoria_context(memories: list[MemoryRecord]) -> str:
    """
    Formate les souvenirs Memoria pour injection dans le prompt.
    """
    if not memories:
        return ""

    lines: list[str] = []
    for idx, mem in enumerate(memories, start=1):
        title: str | None = None
        if hasattr(mem, "metadata") and isinstance(mem.metadata, dict):
            title = mem.metadata.get("title")  # type: ignore[assignment]
        if getattr(mem, "title", None):
            # Priorité au titre explicite
            title = mem.title  # type: ignore[assignment]
        header = f"[Souvenir {idx} - {mem.memory_type}]"
        if title:
            header += f" {title}"
        lines.append(header)
        lines.append(mem.content)
        lines.append("")  # ligne vide séparatrice

    return "\n".join(lines).strip()


@router.post("/chat", response_model=ChatResponse)
async def post_chat(
    data: MessageInput,
    background_tasks: BackgroundTasks,
    query_ollama: Callable[[str, str, float], str] = Depends(get_query_ollama),
) -> ChatResponse:
    """
    Endpoint principal pour le chat avec AssistantIA.

    Traite un message utilisateur et génère une réponse via le modèle IA configuré.
    Peut inclure le contexte Arkalia pour enrichir la réponse.

    Args:
        data: Données du message utilisateur (MessageInput).
        background_tasks: Tâches en arrière-plan pour le logging.
        query_ollama: Fonction d'interrogation Ollama (injection de dépendance).

    Returns:
        ChatResponse: Réponse générée avec métadonnées.

    Raises:
        HTTPException: 400 si message vide, 503 si Ollama indisponible,
                       504 si timeout, 500 en cas d'erreur interne.

    Examples:
        >>> POST /api/v1/chat
        >>> {
        ...     "message": "Bonjour, comment ça va ?",
        ...     "model": "mistral:latest",
        ...     "temperature": 0.7,
        ...     "include_context": true
        ... }
    """
    global active_connections

    # Gestion des connexions actives
    active_connections += 1
    assistantia_active_connections.set(active_connections)

    try:
        start_time = asyncio.get_event_loop().time()
        message = data.message.strip()

        if not message:
            raise HTTPException(status_code=400, detail="Message vide")

        # Vérifier la santé d'Ollama (mode dégradé possible)
        ollama_available = _check_ollama_health()

        # Récupérer le contexte Arkalia si demandé
        arkalia_context = None
        context_quality = 0.0
        if data.include_context:
            arkalia_context, context_quality = await get_arkalia_context()
            enriched_message = (
                f"{message}\n\nContexte système Arkalia-LUNA: {arkalia_context}"
            )
        else:
            enriched_message = message

        # Contexte mémoire vectorielle (Memoria) si activé
        memoria_context = ""
        memoria_user_id = _build_memoria_user_id(data)
        if is_memoria_enabled():
            try:
                memoria_service = get_vector_memory_service()
                memories = memoria_service.search_memory(
                    user_id=memoria_user_id,
                    query=message,
                    top_k=5,
                )
                memoria_context = _format_memoria_context(memories)
            except Exception as e:  # pragma: no cover - protection ultime
                ark_logger.error(
                    f"Erreur Memoria (search_memory): {e}",
                    extra={"arkalia_module": "assistantia"},
                )

        if memoria_context:
            enriched_message = (
                f"{enriched_message}\n\nSouvenirs pertinents (mémoire longue):\n"
                f"{memoria_context}"
            )

        # Prétraiter le message
        processed_message = process_input(enriched_message)

        # Valeurs par défaut pour model et temperature (config > payload > fallback)
        cfg = load_assistantia_config()
        model = data.model or cfg.default_model
        temperature = data.temperature if data.temperature is not None else cfg.default_temperature

        # Si Ollama est indisponible, répondre en mode dégradé sans erreur 503
        if not ollama_available:
            fallback_response = (
                "⚠️ Le moteur IA (Ollama) n'est pas disponible actuellement, "
                "je fonctionne donc en mode dégradé.\n\n"
                f"Message reçu: \"{message}\""
            )
            processing_time = asyncio.get_event_loop().time() - start_time
            assistantia_response_time.observe(processing_time)
            assistantia_prompts_total.labels(
                status="degraded", security_level="medium", model=model
            ).inc()

            background_tasks.add_task(
                log_chat_interaction, message, fallback_response, processing_time, model
            )
            if is_memoria_enabled():
                background_tasks.add_task(
                    save_memoria_interaction,
                    memoria_user_id,
                    message,
                    fallback_response,
                    arkalia_context,
                )

            return ChatResponse(
                response=fallback_response,
                model_used=model,
                processing_time=processing_time,
                context_quality=context_quality,
                arkalia_context=arkalia_context if data.include_context else None,
            )

        # Appeler Ollama
        response = query_ollama(processed_message, model, temperature)

        # Calculer le temps de traitement
        processing_time = asyncio.get_event_loop().time() - start_time
        assistantia_response_time.observe(processing_time)

        # Enregistrer métriques de succès
        assistantia_prompts_total.labels(
            status="success", security_level="medium", model=model
        ).inc()

        # Tâche en arrière-plan pour le logging
        background_tasks.add_task(
            log_chat_interaction, message, response, processing_time, model
        )

        # Tâche en arrière-plan pour la mémoire vectorielle (non bloquante)
        if is_memoria_enabled():
            background_tasks.add_task(
                save_memoria_interaction,
                memoria_user_id,
                message,
                response,
                arkalia_context,
            )

        return ChatResponse(
            response=response,
            model_used=model,
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
        ark_logger.error(f"Erreur AssistantIA: {e}", extra={"arkalia_module": "assistantia"})
        assistantia_prompts_total.labels(
            status="error", security_level="medium", model=data.model
        ).inc()
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}") from e
    finally:
        # Décrémenter les connexions actives
        active_connections = max(0, active_connections - 1)
        assistantia_active_connections.set(active_connections)


async def log_chat_interaction(
    message: str, response: str, processing_time: float, model: str
) -> None:
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
        ark_logger.error(
            f"Erreur logging AssistantIA: {e}", extra={"arkalia_module": "assistantia"}
        )


def save_memoria_interaction(
    user_id: str,
    message: str,
    response: str,
    arkalia_context: str | None,
) -> None:
    """
    Enregistre une interaction de chat complète dans la mémoire vectorielle.

    Cette fonction est prévue pour être appelée en tâche de fond.
    """
    try:
        memoria_service = get_vector_memory_service()

        # Contenu combiné message + réponse + contexte système
        parts: list[str] = [f"Utilisateur: {message}", f"Luna: {response}"]
        if arkalia_context:
            parts.append(f"Contexte système: {arkalia_context}")
        combined = "\n".join(parts)

        metadata = {
            "source": "assistantia_chat",
            "timestamp": datetime.now().isoformat(),
        }

        # Heuristique simple pour classer certaines interactions
        lower_msg = message.lower()
        if "memoire long terme" in lower_msg or "mémoire long terme" in lower_msg:
            memoria_service.add_project_memory(
                user_id=user_id,
                content=combined,
                metadata=metadata,
                title="Project idea (explicit)",
            )
        elif "note ça" in lower_msg or "note ca" in lower_msg:
            memoria_service.add_decision_memory(
                user_id=user_id,
                content=combined,
                metadata=metadata,
                title="Decision (explicit)",
            )
        else:
            memoria_service.add_memory(
                user_id=user_id,
                memory_type="chat",
                content=combined,
                metadata=metadata,
                title=None,
            )
    except Exception as e:  # pragma: no cover - protection ultime
        ark_logger.error(
            f"Erreur save_memoria_interaction: {e}",
            extra={"arkalia_module": "assistantia"},
        )


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """
    Endpoint de santé avec informations détaillées.

    Vérifie l'état du service AssistantIA et des dépendances (Ollama, modules Arkalia).

    Returns:
        HealthResponse: État de santé du service avec détails.

    Examples:
        >>> GET /api/v1/health
        >>> {
        ...     "status": "healthy",
        ...     "ollama_available": true,
        ...     "arkalia_modules": {"ZeroIA": "active"},
        ...     "uptime": "2:30:15",
        ...     "version": "2.8.0"
        ... }
    """
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
        ark_logger.error(f"Erreur health check: {e}", extra={"arkalia_module": "assistantia"})
        return HealthResponse(
            status="unhealthy", ollama_available=False, arkalia_modules={}, uptime="unknown"
        )


@router.get("/metrics", response_model=None)
async def get_metrics() -> PlainTextResponse | JSONResponse:
    """
    Endpoint métriques Prometheus pour AssistantIA.

    Retourne les métriques Prometheus au format texte pour le scraping.

    Returns:
        PlainTextResponse: Métriques Prometheus au format texte.
        JSONResponse: Erreur en JSON si problème.

    Examples:
        >>> GET /api/v1/metrics
        >>> # assistantia_prompts_total{status="success"} 42
        >>> # assistantia_response_time_seconds_bucket{le="0.5"} 35
    """
    try:
        prometheus_data = generate_latest()
        return PlainTextResponse(content=prometheus_data, media_type=CONTENT_TYPE_LATEST)
    except Exception as e:
        ark_logger.error(f"Erreur métriques: {e}", extra={"arkalia_module": "assistantia"})
        return JSONResponse(
            status_code=500,
            content={"error": f"Erreur métriques : {str(e)}"},
        )


@router.get("/models", response_model=None)
async def get_available_models() -> dict | JSONResponse:
    """
    Récupère la liste des modèles disponibles.

    Interroge Ollama pour obtenir la liste des modèles IA disponibles.

    Returns:
        dict: Dictionnaire contenant la liste des modèles.
        JSONResponse: Erreur en JSON si problème.

    Examples:
        >>> GET /api/v1/models
        >>> {
        ...     "models": [
        ...         {"name": "mistral:latest", "size": "4.1GB"},
        ...         {"name": "llama2:latest", "size": "3.8GB"}
        ...     ]
        ... }
    """
    try:
        from .utils.ollama_connector import get_available_models

        models = get_available_models()
        if models:
            return {"models": models.get("models", [])}
        else:
            return {"models": [], "error": "Impossible de récupérer les modèles"}
    except Exception as e:
        ark_logger.error(
            f"Erreur récupération modèles: {e}", extra={"arkalia_module": "assistantia"}
        )
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
async def root() -> dict:
    """
    Endpoint racine de l'application AssistantIA.

    Retourne les informations de base sur le service.

    Returns:
        dict: Informations du service (nom, version, endpoints).

    Examples:
        >>> GET /
        >>> {
        ...     "service": "AssistantIA",
        ...     "version": "2.8.0",
        ...     "status": "active",
        ...     "docs": "/docs",
        ...     "health": "/health",
        ...     "metrics": "/metrics"
        ... }
    """
    return {
        "service": "AssistantIA",
        "version": "2.8.0",
        "status": "active",
        "docs": "/docs",
        "health": "/health",
        "metrics": "/metrics",
    }

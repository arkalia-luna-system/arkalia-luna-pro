"""Module de métriques Prometheus pour Arkalia-LUNA"""

import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter
from fastapi.responses import JSONResponse, PlainTextResponse
from prometheus_client import CONTENT_TYPE_LATEST, CollectorRegistry, Counter, Gauge, Histogram, generate_latest

logger = logging.getLogger(__name__)

class ArkaliaMetrics:
    """Classe de gestion des métriques Prometheus"""

    def __init__(self, registry: CollectorRegistry | None = None) -> None:
        # Utiliser le registre fourni ou créer un nouveau
        self._registry = registry or CollectorRegistry()

        # Métriques système standardisées
        self.arkalia_system_uptime = Gauge(
            "arkalia_system_uptime_seconds",
            "Temps d'activité du système en secondes",
            registry=self._registry,
        )
        
        # Métriques communes par module (standard Prometheus)
        self.arkalia_module_name = Gauge(
            "arkalia_module_name",
            "Nom du module Arkalia",
            ["module"],
            registry=self._registry
        )
        
        self.arkalia_uptime_seconds = Gauge(
            "arkalia_uptime_seconds",
            "Temps de fonctionnement du module en secondes",
            ["module"],
            registry=self._registry
        )
        
        self.arkalia_last_successful_interaction_timestamp = Gauge(
            "arkalia_last_successful_interaction_timestamp",
            "Timestamp de la dernière interaction réussie",
            ["module"],
            registry=self._registry
        )
        
        self.arkalia_cognitive_score = Gauge(
            "arkalia_cognitive_score",
            "Score cognitif du module (0.0-1.0)",
            ["module"],
            registry=self._registry
        )

        self.arkalia_cpu_usage = Gauge(
            "arkalia_cpu_usage", "Utilisation CPU en pourcentage", registry=self._registry
        )

        self.arkalia_memory_usage = Gauge(
            "arkalia_memory_usage", "Utilisation mémoire en bytes", registry=self._registry
        )

        # Métriques des modules
        self.arkalia_modules_status = Gauge(
            "arkalia_modules_status",
            "Statut des modules (1=actif, 0=inactif)",
            ["module_name"],
            registry=self._registry,
        )

        # Métriques des requêtes
        self.arkalia_requests_total = Counter(
            "arkalia_requests_total",
            "Nombre total de requêtes",
            ["method", "endpoint", "status"],
            registry=self._registry,
        )

        self.arkalia_request_duration = Histogram(
            "arkalia_request_duration",
            "Durée des requêtes en secondes",
            ["method", "endpoint"],
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0],
            registry=self._registry,
        )

        # Métriques de sécurité
        self.arkalia_security_events = Counter(
            "arkalia_security_events_total",
            "Nombre total d'événements de sécurité",
            ["event_type", "severity"],
            registry=self._registry,
        )

        # Métriques de performance
        self.arkalia_performance_score = Gauge(
            "arkalia_performance_score",
            "Score de performance global (0-100)",
            registry=self._registry,
        )

        # Initialiser les métriques système
        self._update_system_metrics()

    def _update_system_metrics(self) -> None:
        """Met à jour les métriques système"""
        try:
            # Uptime (simulation - en production utiliser psutil)
            self.arkalia_system_uptime.set(time.time())
            
            # CPU et RAM (simulation - en production utiliser psutil)
            self.arkalia_cpu_usage.set(45.0)  # Valeur simulée
            self.arkalia_memory_usage.set(1024 * 1024 * 512)  # 512MB simulé
            
            # Performance score
            self.arkalia_performance_score.set(85.0)  # Score simulé
            
        except Exception as e:
            logger.error(f"Erreur mise à jour métriques système: {e}")

    def update_module_status(self, module_name: str, is_active: bool) -> None:
        """Met à jour le statut d'un module"""
        try:
            self.arkalia_modules_status.labels(module_name=module_name).set(1 if is_active else 0)
        except Exception as e:
            logger.error(f"Erreur mise à jour statut module {module_name}: {e}")

    def record_request(self, method: str, endpoint: str, status: int, duration: float) -> None:
        """Enregistre une requête"""
        try:
            self.arkalia_requests_total.labels(method=method, endpoint=endpoint, status=str(status)).inc()
            self.arkalia_request_duration.labels(method=method, endpoint=endpoint).observe(duration)
        except Exception as e:
            logger.error(f"Erreur enregistrement requête: {e}")

    def record_security_event(self, event_type: str, severity: str) -> None:
        """Enregistre un événement de sécurité"""
        try:
            self.arkalia_security_events.labels(event_type=event_type, severity=severity).inc()
        except Exception as e:
            logger.error(f"Erreur enregistrement événement sécurité: {e}")

    def get_registry(self) -> CollectorRegistry:
        """Retourne le registre de métriques"""
        return self._registry

    def generate_metrics(self) -> str:
        """Génère les métriques au format Prometheus"""
        try:
            # Mettre à jour les métriques système
            self._update_system_metrics()
            
            # Mettre à jour les statuts des modules
            self._update_module_statuses()
            
            # Générer le format Prometheus
            return generate_latest(self._registry).decode('utf-8')
        except Exception as e:
            logger.error(f"Erreur génération métriques: {e}")
            return ""

    def _update_module_statuses(self) -> None:
        """Met à jour les statuts de tous les modules"""
        modules = {
            "zeroia": "modules/zeroia/state/zeroia_state.toml",
            "reflexia": "state/reflexia_state.toml", 
            "assistantia": "modules/assistantia/core.py",
            "sandozia": "state/sandozia",
            "cognitive_reactor": "modules/cognitive_reactor/state/cognitive_reactor_state.toml",
            "security": "modules/security/core.py",
            "monitoring": "modules/monitoring/prometheus_metrics.py"
        }
        
        current_time = time.time()
        
        for module_name, module_path in modules.items():
            try:
                path = Path(module_path)
                is_active = path.exists()
                self.update_module_status(module_name, is_active)
                
                # Mettre à jour les métriques standardisées
                self.arkalia_module_name.labels(module=module_name).set(1)
                self.arkalia_uptime_seconds.labels(module=module_name).set(current_time)
                self.arkalia_last_successful_interaction_timestamp.labels(module=module_name).set(current_time)
                
                # Score cognitif simulé (en production, récupérer depuis le module)
                cognitive_scores = {
                    "zeroia": 0.85,
                    "reflexia": 0.78,
                    "assistantia": 0.82,
                    "sandozia": 0.75,
                    "cognitive_reactor": 0.88,
                    "security": 0.90,
                    "monitoring": 0.70
                }
                score = cognitive_scores.get(module_name, 0.5)
                self.arkalia_cognitive_score.labels(module=module_name).set(score)
                
            except Exception as e:
                logger.warning(f"Erreur vérification module {module_name}: {e}")
                self.update_module_status(module_name, False)


# Instance globale
metrics = ArkaliaMetrics()

# Router pour l'endpoint /metrics
router = APIRouter(tags=["Monitoring"])

@router.get("/metrics")
async def get_metrics():
    """
    📊 Endpoint métriques Prometheus pour le monitoring global
    """
    try:
        prometheus_data = metrics.generate_metrics()
        return PlainTextResponse(content=prometheus_data, media_type=CONTENT_TYPE_LATEST)
    except Exception as e:
        logger.error(f"Erreur endpoint métriques: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Erreur métriques : {str(e)}"},
        )

@router.get("/health")
async def health_check():
    """
    🏥 Endpoint de santé du monitoring
    """
    try:
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "metrics_collected": True,
            "modules_monitored": 7
        }
    except Exception as e:
        logger.error(f"Erreur health check: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "unhealthy", "error": str(e)}
        )

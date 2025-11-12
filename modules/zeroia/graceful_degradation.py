"""
📉 Graceful Degradation System Enterprise v2.7.0
Système de dégradation gracieuse pour Arkalia-LUNA

Fonctionnalités :
- Dégradation progressive des services
- Modes de fonctionnement adaptatifs
- Priorisation automatique des fonctionnalités
- Monitoring de santé en temps réel
- Récupération automatique
"""

import asyncio
import json
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from core.ark_logger import ark_logger


class ServicePriority(Enum):
    """Niveaux de priorité des services"""

    CRITICAL = "critical"  # Services critiques (monitoring, sécurité)
    HIGH = "high"  # Services haute priorité (core logic)
    MEDIUM = "medium"  # Services importants (analytics, reporting)
    LOW = "low"  # Services optionnels (UI enhancements, caching)
    OPTIONAL = "optional"  # Services non-essentiels (debug, dev tools)


class DegradationLevel(Enum):
    """Niveaux de dégradation"""

    NORMAL = "normal"  # Fonctionnement normal
    LIGHT_DEGRADATION = "light"  # Dégradation légère (95% services)
    MODERATE_DEGRADATION = "moderate"  # Dégradation modérée (80% services)
    HEAVY_DEGRADATION = "heavy"  # Dégradation lourde (60% services)
    EMERGENCY = "emergency"  # Mode urgence (40% services critiques)
    SURVIVAL = "survival"  # Mode survie (20% services essentiels)


class ServiceStatus(Enum):
    """États des services"""

    ACTIVE = "active"
    DEGRADED = "degraded"
    SUSPENDED = "suspended"
    DISABLED = "disabled"
    FAILED = "failed"


@dataclass
class ServiceDefinition:
    """Définition d'un service"""

    name: str
    priority: ServicePriority
    dependencies: list[str] = field(default_factory=list)
    health_check: Callable | None = None
    graceful_shutdown: Callable | None = None
    resource_cost: float = 1.0  # Coût en ressources (CPU/RAM)
    description: str = ""

    def __post_init__(self) -> None:
        if not self.description:
            self.description = f"Service {self.name}"


@dataclass
class ServiceMetrics:
    """Métriques d'un service"""

    name: str
    status: ServiceStatus
    last_health_check: datetime | None = None
    failure_count: int = 0
    last_failure: datetime | None = None
    uptime: float = 0.0
    resource_usage: float = 0.0
    response_time: float = 0.0


@dataclass
class DegradationMetrics:
    """Métriques du système de dégradation"""

    current_level: DegradationLevel
    active_services: int = 0
    degraded_services: int = 0
    suspended_services: int = 0
    disabled_services: int = 0
    total_resource_usage: float = 0.0
    system_health_score: float = 0.0
    last_level_change: datetime | None = None
    degradation_triggers: list[str] = field(default_factory=list)


class GracefulDegradationSystem:
    """
    Système de dégradation gracieuse Enterprise

    Architecture :
    - Dégradation progressive basée sur la priorité
    - Monitoring continu de la santé système
    - Récupération automatique quand possible
    - Métriques détaillées en temps réel
    """

    def __init__(self, config_path: str | None = None) -> None:
        self.services: dict[str, ServiceDefinition] = {}
        self.service_metrics: dict[str, ServiceMetrics] = {}
        self.degradation_metrics = DegradationMetrics(DegradationLevel.NORMAL)

        # Configuration des seuils
        self.thresholds = self._load_thresholds(config_path)

        # État du système
        self.current_level = DegradationLevel.NORMAL
        self.last_health_check = datetime.now()
        self.auto_recovery_enabled = True
        self.initialization_count = 0
        self.max_initializations = 3
        self.initialization_timeout = 120  # secondes
        self.last_initialization = datetime.now()
        self.initialization_cooldown = 30  # secondes

        # Callbacks
        self.degradation_callbacks: list[Callable] = []
        self.recovery_callbacks: list[Callable] = []

        # Métriques
        self.metrics = {
            "cpu_usage": 0.0,
            "memory_usage": 0.0,
            "response_time": 0.0,
            "error_count": 0,
            "service_count": 0,
        }

        # État de santé
        self.health_status = {
            "is_healthy": True,
            "last_error": None,
            "error_count": 0,
            "last_recovery": None,
        }

        # Configuration de la dégradation
        self.degradation_config = {
            "auto_recovery": True,
            "max_retries": 3,
            "retry_delay": 5,
            "cooldown_period": 30,
        }

        # Services par défaut
        if self.initialization_count < self.max_initializations:
            self._register_default_services()
            self.initialization_count += 1

        logger.info("📉 GracefulDegradationSystem initialisé")

    def _load_thresholds(self, config_path: str | None) -> dict[str, float]:
        """Charge les seuils de dégradation"""
        default_thresholds = {
            "cpu_usage": 80.0,  # % CPU pour déclencher dégradation
            "memory_usage": 85.0,  # % RAM pour déclencher dégradation
            "error_rate": 10.0,  # % erreurs pour déclencher dégradation
            "response_time": 5.0,  # Secondes max response time
            "failure_threshold": 5,  # Nombre d'échecs consécutifs
            "recovery_threshold": 70.0,  # % santé pour récupération auto
        }

        if config_path and Path(config_path).exists():
            try:
                with open(config_path) as f:
                    custom_thresholds = json.load(f)
                default_thresholds.update(custom_thresholds)
            except Exception as e:
                logger.warning(f"⚠️ Impossible de charger config: {e}")

        return default_thresholds

    def _register_default_services(self):
        """Enregistre les services par défaut d'Arkalia"""
        default_services = [
            # Services critiques
            ServiceDefinition(
                "system_monitoring",
                ServicePriority.CRITICAL,
                [],
                description="Monitoring système essentiel",
            ),
            ServiceDefinition(
                "error_recovery",
                ServicePriority.CRITICAL,
                [],
                description="Système de récupération d'erreurs",
            ),
            ServiceDefinition(
                "circuit_breaker",
                ServicePriority.CRITICAL,
                [],
                description="Circuit breaker protection",
            ),
            # Services haute priorité
            ServiceDefinition(
                "zeroia_core",
                ServicePriority.HIGH,
                ["system_monitoring"],
                description="Moteur de décision ZeroIA",
            ),
            ServiceDefinition(
                "reflexia_core",
                ServicePriority.HIGH,
                ["system_monitoring"],
                description="Système de réflexion Reflexia",
            ),
            ServiceDefinition(
                "event_sourcing",
                ServicePriority.HIGH,
                [],
                description="Event sourcing et audit",
            ),
            # Services priorité moyenne
            ServiceDefinition(
                "sandozia_intelligence",
                ServicePriority.MEDIUM,
                ["zeroia_core", "reflexia_core"],
                description="Intelligence croisée Sandozia",
            ),
            ServiceDefinition(
                "assistantia_api",
                ServicePriority.MEDIUM,
                ["zeroia_core"],
                description="API Assistant IA",
            ),
            ServiceDefinition(
                "prometheus_metrics",
                ServicePriority.MEDIUM,
                [],
                description="Métriques Prometheus",
            ),
            # Services priorité basse
            ServiceDefinition(
                "advanced_analytics",
                ServicePriority.LOW,
                ["event_sourcing"],
                description="Analytics avancées",
            ),
            ServiceDefinition(
                "ui_enhancements",
                ServicePriority.LOW,
                [],
                description="Améliorations interface",
            ),
            ServiceDefinition(
                "caching_layer", ServicePriority.LOW, [], description="Couche de cache"
            ),
            # Services optionnels
            ServiceDefinition(
                "debug_tools",
                ServicePriority.OPTIONAL,
                [],
                description="Outils de debug",
            ),
            ServiceDefinition(
                "dev_utilities",
                ServicePriority.OPTIONAL,
                [],
                description="Utilitaires développement",
            ),
        ]

        for service in default_services:
            self.register_service(service)

    def register_service(self, service: ServiceDefinition):
        """Enregistre un nouveau service"""
        self.services[service.name] = service
        self.service_metrics[service.name] = ServiceMetrics(
            name=service.name,
            status=ServiceStatus.ACTIVE,
            last_health_check=datetime.now(),
        )
        logger.info(f"📝 Service enregistré: {service.name} ({service.priority.value})")

    def unregister_service(self, service_name: str):
        """Désenregistre un service"""
        if service_name in self.services:
            del self.services[service_name]
            del self.service_metrics[service_name]
            logger.info(f"🗑️ Service désenregistré: {service_name}")

    async def assess_system_health(self) -> float:
        """Évalue la santé globale du système (0.0 à 1.0)"""
        if not self.services:
            return 0.0

        total_weight = 0.0
        weighted_health = 0.0

        # Calculer la santé pondérée par priorité
        priority_weights = {
            ServicePriority.CRITICAL: 5.0,
            ServicePriority.HIGH: 3.0,
            ServicePriority.MEDIUM: 2.0,
            ServicePriority.LOW: 1.0,
            ServicePriority.OPTIONAL: 0.5,
        }

        for service_name, service in self.services.items():
            metrics = self.service_metrics[service_name]
            weight = priority_weights[service.priority]

            # Calculer santé du service
            service_health = self._calculate_service_health(metrics)

            weighted_health += service_health * weight
            total_weight += weight

        if total_weight == 0:
            return 0.0

        overall_health = weighted_health / total_weight
        self.degradation_metrics.system_health_score = overall_health

        return overall_health

    def _calculate_service_health(self, metrics: ServiceMetrics) -> float:
        """Calcule la santé d'un service individuel"""
        if metrics.status == ServiceStatus.ACTIVE:
            health = 1.0
        elif metrics.status == ServiceStatus.DEGRADED:
            health = 0.7
        elif metrics.status == ServiceStatus.SUSPENDED:
            health = 0.3
        elif metrics.status == ServiceStatus.DISABLED:
            health = 0.1
        else:  # FAILED
            health = 0.0

        # Ajustement basé sur les métriques
        if metrics.failure_count > 0:
            failure_penalty = min(0.3, metrics.failure_count * 0.05)
            health -= failure_penalty

        if metrics.response_time > self.thresholds["response_time"]:
            response_penalty = min(
                0.2, (metrics.response_time - self.thresholds["response_time"]) * 0.1
            )
            health -= response_penalty

        return max(0.0, health)

    async def trigger_degradation(
        self, target_level: DegradationLevel, reason: str = "Manual trigger"
    ):
        """Déclenche une dégradation vers le niveau spécifié"""
        if target_level == self.current_level:
            return

        logger.warning(
            f"📉 Dégradation déclenchée: {self.current_level.value} → {target_level.value}"
        )
        logger.warning(f"   Raison: {reason}")

        old_level = self.current_level
        self.current_level = target_level

        # Mettre à jour les métriques
        self.degradation_metrics.current_level = target_level
        self.degradation_metrics.last_level_change = datetime.now()
        self.degradation_metrics.degradation_triggers.append(
            f"{datetime.now().isoformat()}: {reason}"
        )

        # Appliquer la dégradation
        await self._apply_degradation_level(target_level)

        # Exécuter les callbacks
        for callback in self.degradation_callbacks:
            try:
                await callback(old_level, target_level, reason)
            except Exception as e:
                logger.error(f"❌ Callback dégradation failed: {e}")

        # Recalculer les métriques
        await self._update_degradation_metrics()

    async def _apply_degradation_level(self, level: DegradationLevel):
        """Applique un niveau de dégradation"""
        # Définir quels services désactiver par niveau
        services_to_disable: set[str] = set()

        if level in [DegradationLevel.LIGHT_DEGRADATION]:
            # Désactiver seulement les services optionnels
            services_to_disable.update(self._get_services_by_priority(ServicePriority.OPTIONAL))

        elif level == DegradationLevel.MODERATE_DEGRADATION:
            services_to_disable.update(self._get_services_by_priority(ServicePriority.OPTIONAL))
            services_to_disable.update(self._get_services_by_priority(ServicePriority.LOW))

        elif level == DegradationLevel.HEAVY_DEGRADATION:
            services_to_disable.update(self._get_services_by_priority(ServicePriority.OPTIONAL))
            services_to_disable.update(self._get_services_by_priority(ServicePriority.LOW))
            # Dégrader services medium priorité
            medium_services = self._get_services_by_priority(ServicePriority.MEDIUM)
            for service_name in medium_services:
                await self._degrade_service(service_name)

        elif level == DegradationLevel.EMERGENCY:
            services_to_disable.update(self._get_services_by_priority(ServicePriority.OPTIONAL))
            services_to_disable.update(self._get_services_by_priority(ServicePriority.LOW))
            services_to_disable.update(self._get_services_by_priority(ServicePriority.MEDIUM))

        elif level == DegradationLevel.SURVIVAL:
            # Garder seulement les services critiques
            for priority in [
                ServicePriority.OPTIONAL,
                ServicePriority.LOW,
                ServicePriority.MEDIUM,
                ServicePriority.HIGH,
            ]:
                services_to_disable.update(self._get_services_by_priority(priority))

        # Appliquer les désactivations
        for service_name in services_to_disable:
            await self._suspend_service(service_name)

        logger.info(
            f"📉 Niveau {level.value} appliqué: {len(services_to_disable)} services suspendus"
        )

    def _get_services_by_priority(self, priority: ServicePriority) -> list[str]:
        """Retourne les services d'une priorité donnée"""
        return [name for name, service in self.services.items() if service.priority == priority]

    async def _suspend_service(self, service_name: str):
        """Suspend un service"""
        if service_name not in self.service_metrics:
            return

        metrics = self.service_metrics[service_name]
        service = self.services[service_name]

        # Appeler graceful shutdown si disponible
        if service.graceful_shutdown:
            try:
                await service.graceful_shutdown()
            except Exception as e:
                logger.error(f"❌ Graceful shutdown failed for {service_name}: {e}")

        metrics.status = ServiceStatus.SUSPENDED
        logger.info(f"⏸️ Service suspendu: {service_name}")

    async def _degrade_service(self, service_name: str):
        """Dégrade un service (mode réduit)"""
        if service_name not in self.service_metrics:
            return

        metrics = self.service_metrics[service_name]
        metrics.status = ServiceStatus.DEGRADED
        logger.info(f"📉 Service dégradé: {service_name}")

    async def attempt_recovery(self) -> bool:
        """Tente une récupération automatique"""
        if not self.auto_recovery_enabled:
            return False

        current_health = await self.assess_system_health()

        # Vérifier si récupération possible
        if current_health < self.thresholds["recovery_threshold"] / 100.0:
            return False

        # Essayer de monter d'un niveau
        target_level = self._get_recovery_level()
        if target_level == self.current_level:
            return False

        logger.info(
            f"🔄 Tentative de récupération: {self.current_level.value} → {target_level.value}"
        )

        # Réactiver les services progressivement
        await self._recover_to_level(target_level)

        # Vérifier que la récupération est stable
        await asyncio.sleep(2)
        new_health = await self.assess_system_health()

        if new_health >= self.thresholds["recovery_threshold"] / 100.0:
            self.current_level = target_level
            self.degradation_metrics.current_level = target_level
            self.degradation_metrics.last_level_change = datetime.now()

            # Exécuter callbacks de récupération
            for callback in self.recovery_callbacks:
                try:
                    await callback(self.current_level, target_level)
                except Exception as e:
                    logger.error(f"❌ Recovery callback failed: {e}")

            logger.info(f"✅ Récupération réussie vers {target_level.value}")
            return True
        else:
            # Rollback si récupération échoue
            await self._apply_degradation_level(self.current_level)
            logger.warning(f"⚠️ Récupération échouée, rollback vers {self.current_level.value}")
            return False

    def _get_recovery_level(self) -> DegradationLevel:
        """Détermine le niveau de récupération cible"""
        levels = [
            DegradationLevel.SURVIVAL,
            DegradationLevel.EMERGENCY,
            DegradationLevel.HEAVY_DEGRADATION,
            DegradationLevel.MODERATE_DEGRADATION,
            DegradationLevel.LIGHT_DEGRADATION,
            DegradationLevel.NORMAL,
        ]

        current_index = levels.index(self.current_level)
        if current_index < len(levels) - 1:
            return levels[current_index + 1]
        return self.current_level

    async def _recover_to_level(self, target_level: DegradationLevel):
        """Récupère vers un niveau de dégradation supérieur"""
        # Réactiver les services selon le niveau cible
        if target_level == DegradationLevel.NORMAL:
            # Réactiver tous les services
            for service_name in self.services:
                await self._reactivate_service(service_name)

        elif target_level == DegradationLevel.LIGHT_DEGRADATION:
            # Réactiver tout sauf optionnel
            for priority in [
                ServicePriority.CRITICAL,
                ServicePriority.HIGH,
                ServicePriority.MEDIUM,
                ServicePriority.LOW,
            ]:
                services = self._get_services_by_priority(priority)
                for service_name in services:
                    await self._reactivate_service(service_name)

        # etc. pour les autres niveaux...

    async def _reactivate_service(self, service_name: str):
        """Réactive un service"""
        if service_name not in self.service_metrics:
            return

        metrics = self.service_metrics[service_name]
        if metrics.status in [ServiceStatus.SUSPENDED, ServiceStatus.DEGRADED]:
            metrics.status = ServiceStatus.ACTIVE
            logger.info(f"✅ Service réactivé: {service_name}")

    async def _update_degradation_metrics(self):
        """Met à jour les métriques de dégradation"""
        active = degraded = suspended = disabled = 0
        total_resources = 0.0

        for metrics in self.service_metrics.values():
            if metrics.status == ServiceStatus.ACTIVE:
                active += 1
            elif metrics.status == ServiceStatus.DEGRADED:
                degraded += 1
            elif metrics.status == ServiceStatus.SUSPENDED:
                suspended += 1
            elif metrics.status == ServiceStatus.DISABLED:
                disabled += 1

            total_resources += metrics.resource_usage

        self.degradation_metrics.active_services = active
        self.degradation_metrics.degraded_services = degraded
        self.degradation_metrics.suspended_services = suspended
        self.degradation_metrics.disabled_services = disabled
        self.degradation_metrics.total_resource_usage = total_resources

    def get_system_status(self) -> dict[str, Any]:
        """Retourne l'état complet du système"""
        return {
            "degradation_level": self.current_level.value,
            "system_health": self.degradation_metrics.system_health_score,
            "services": {
                "active": self.degradation_metrics.active_services,
                "degraded": self.degradation_metrics.degraded_services,
                "suspended": self.degradation_metrics.suspended_services,
                "disabled": self.degradation_metrics.disabled_services,
                "total": len(self.services),
            },
            "resource_usage": self.degradation_metrics.total_resource_usage,
            "last_change": (
                self.degradation_metrics.last_level_change.isoformat()
                if self.degradation_metrics.last_level_change
                else None
            ),
            "auto_recovery": self.auto_recovery_enabled,
            "recent_triggers": self.degradation_metrics.degradation_triggers[-5:],  # 5 derniers
        }

    def get_service_details(self) -> dict[str, Any]:
        """Retourne les détails de tous les services"""
        services_detail: dict[str, Any] = {}

        for name, service in self.services.items():
            metrics = self.service_metrics[name]
            services_detail[name] = {
                "priority": service.priority.value,
                "status": metrics.status.value,
                "dependencies": service.dependencies,
                "description": service.description,
                "failure_count": metrics.failure_count,
                "last_health_check": (
                    metrics.last_health_check.isoformat() if metrics.last_health_check else None
                ),
                "resource_usage": metrics.resource_usage,
                "response_time": metrics.response_time,
            }

        return services_detail

    def add_degradation_callback(self, callback: Callable):
        """Ajoute un callback appelé lors de dégradations"""
        self.degradation_callbacks.append(callback)

    def add_recovery_callback(self, callback: Callable):
        """Ajoute un callback appelé lors de récupérations"""
        self.recovery_callbacks.append(callback)

    async def health_check(self) -> dict[str, Any]:
        """Vérification de santé du système de dégradation"""
        try:
            health_score = await self.assess_system_health()

            return {
                "status": "healthy" if health_score > 0.7 else "degraded",
                "health_score": health_score,
                "degradation_level": self.current_level.value,
                "services_count": len(self.services),
                "auto_recovery": self.auto_recovery_enabled,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def can_initialize(self) -> bool:
        """Vérifie si le système peut être initialisé"""
        now = datetime.now()

        # Vérifier le nombre d'initialisations
        if self.initialization_count >= self.max_initializations:
            return False

        # Vérifier le délai depuis la dernière initialisation
        if (now - self.last_initialization).total_seconds() < self.initialization_cooldown:
            return False

        return True

    def initialize(self) -> bool:
        """Initialise le système avec protection contre les boucles"""
        if not self.can_initialize():
            logger.warning("🚫 Initialisation bloquée (protection anti-boucle)")
            return False

        self.initialization_count += 1
        self.last_initialization = datetime.now()

        # Réinitialisation des métriques
        self.metrics = {
            "cpu_usage": 0.0,
            "memory_usage": 0.0,
            "response_time": 0.0,
            "error_count": 0,
            "service_count": 0,
        }

        # Réinitialisation de l'état de santé
        self.health_status = {
            "is_healthy": True,
            "last_error": None,
            "error_count": 0,
            "last_recovery": None,
        }

        return True


# Factory function
def create_graceful_degradation_system(
    config_path: str | None = None,
) -> GracefulDegradationSystem:
    """Factory pour créer un système de dégradation configuré"""
    return GracefulDegradationSystem(config_path)

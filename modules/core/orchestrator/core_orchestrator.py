#!/usr/bin/env python3
"""
🌟 CORE ORCHESTRATOR - Orchestrateur central Arkalia Luna Pro

Migration de la logique d'arkalia_master vers le module core centralisé.
Intégration avec les interfaces SOLID et les factories.
"""

import asyncio
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from core.ark_logger import ark_logger

from ..config import ConfigManager
from ..factories import ModuleFactory, ServiceFactory
from ..health import HealthMonitor
from ..interfaces import IModule, IOrchestrator


class CycleMode(Enum):
    """Modes de cycle adaptatifs"""

    URGENT = "urgent"  # 5s - Décisions critiques
    NORMAL = "normal"  # 30s - Opérations standard
    DEEP_ANALYSIS = "deep"  # 300s - Analyse approfondie
    MAINTENANCE = "maintenance"  # 1800s - Maintenance système
    COGNITIVE_BOOST = "cognitive"  # 60s - Mode réacteur cognitif


class ModuleStatus(Enum):
    """États des modules"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    OFFLINE = "offline"
    INITIALIZING = "initializing"
    RECOVERING = "recovering"
    COGNITIVE = "cognitive"


@dataclass
class CoreOrchestratorConfig:
    """Configuration de l'orchestrateur central"""

    # Cycles adaptatifs
    cycle_intervals: dict[CycleMode, float] = field(
        default_factory=lambda: {
            CycleMode.URGENT: 5.0,
            CycleMode.NORMAL: 30.0,
            CycleMode.DEEP_ANALYSIS: 300.0,
            CycleMode.MAINTENANCE: 1800.0,
            CycleMode.COGNITIVE_BOOST: 60.0,
        }
    )

    # Circuit breaker global
    global_failure_threshold: int = 10
    global_timeout: int = 60

    # Modules actifs
    enabled_modules: list[str] = field(
        default_factory=lambda: [
            "zeroia",
            "reflexia",
            "assistantia",
            "sandozia",
            "taskia",
            "helloria",
            "nyxalia",
            "security",
            "monitoring",
            "utils",
        ]
    )

    # Features avancées
    cognitive_mode_enabled: bool = True
    auto_recovery_enabled: bool = True
    temporal_analysis_enabled: bool = True
    cross_validation_enabled: bool = True

    # Performance
    max_concurrent_operations: int = 8
    health_check_interval: float = 45.0

    # Persistance
    state_file: Path = Path("state/core_orchestrator_state.toml")
    log_file: Path = Path("logs/core_orchestrator.log")


@dataclass
class ModuleWrapper:
    """Wrapper pour chaque module"""

    name: str
    instance: IModule
    status: ModuleStatus = ModuleStatus.INITIALIZING
    last_execution: datetime | None = None
    execution_count: int = 0
    error_count: int = 0
    last_error: str | None = None
    recovery_attempts: int = 0
    cognitive_score: float = 0.0

    def update_success(self):
        """Met à jour après exécution réussie"""
        self.last_execution = datetime.now()
        self.execution_count += 1
        self.status = ModuleStatus.HEALTHY
        self.cognitive_score = min(self.cognitive_score + 0.1, 1.0)

    def update_error(self, error: str):
        """Met à jour après erreur avec récupération"""
        self.error_count += 1
        self.last_error = error
        self.cognitive_score = max(self.cognitive_score - 0.2, 0.0)

        if self.error_count < 3:
            self.status = ModuleStatus.DEGRADED
        elif self.error_count < 8:
            self.status = ModuleStatus.CRITICAL
        else:
            self.status = ModuleStatus.RECOVERING

    def start_recovery(self):
        """Démarre la récupération du module"""
        self.recovery_attempts += 1
        self.status = ModuleStatus.RECOVERING


class CoreOrchestrator(IOrchestrator):
    """
    🌟 ORCHESTRATEUR CENTRAL ARKALIA LUNA PRO

    Migration de la logique d'arkalia_master vers le module core centralisé.
    Intégration avec les interfaces SOLID et les factories.
    """

    def __init__(self, config: CoreOrchestratorConfig | None = None) -> None:
        self.config = config or CoreOrchestratorConfig()
        self.current_cycle_mode = CycleMode.NORMAL
        self.is_running = False
        self.start_time = time.time()

        # Composants core
        self.config_manager = ConfigManager()
        self.health_monitor = HealthMonitor()
        self.module_factory = ModuleFactory()
        self.service_factory = ServiceFactory()

        # État orchestrateur
        self.cycle_count = 0
        self.total_operations = 0
        self.successful_operations = 0
        self.failed_operations = 0
        self.cognitive_events = 0
        self.recovery_events = 0

        # Modules wrappés
        self.modules: dict[str, ModuleWrapper] = {}

        # État global
        self.global_state: dict[str, Any] = {}
        self.cognitive_state: dict[str, Any] = {}

        # Tasks asyncio
        self.orchestration_task: asyncio.Task | None = None
        self.health_check_task: asyncio.Task | None = None
        self.cognitive_task: asyncio.Task | None = None

        ark_logger.info("🌟 CoreOrchestrator initialized", extra={"arkalia_module": "core"})

    async def initialize(self) -> bool:
        """Initialise l'orchestrateur et tous les modules"""
        ark_logger.info("🔌 Initializing Core Orchestrator...", extra={"arkalia_module": "core"})

        try:
            # Initialiser les composants core
            self.config_manager.initialize()
            self.health_monitor.initialize()

            # Initialiser les modules via factory
            await self._initialize_modules()

            # Démarrer les tasks de monitoring
            await self._start_monitoring_tasks()

            self.is_running = True
            ark_logger.info(
                "✅ Core Orchestrator initialized successfully", extra={"arkalia_module": "core"}
            )
            return True

        except Exception as e:
            ark_logger.error(
                f"❌ Failed to initialize Core Orchestrator: {e}", extra={"arkalia_module": "core"}
            )
            return False

    async def _initialize_modules(self) -> None:
        """Initialise tous les modules via la factory"""
        ark_logger.info(
            f"🔌 Initializing {len(self.config.enabled_modules)} modules...",
            extra={"arkalia_module": "core"},
        )

        for module_name in self.config.enabled_modules:
            try:
                # Créer le module via la factory
                module_instance = self.module_factory.create_module(module_name)

                if module_instance:
                    # Initialiser le module
                    if module_instance.initialize():
                        wrapper = ModuleWrapper(module_name, module_instance)
                        wrapper.update_success()
                        self.modules[module_name] = wrapper
                        ark_logger.info(
                            f"✅ {module_name} initialized successfully",
                            extra={"arkalia_module": "core"},
                        )
                    else:
                        ark_logger.warning(
                            f"⚠️ {module_name} failed to initialize",
                            extra={"arkalia_module": "core"},
                        )
                else:
                    ark_logger.warning(
                        f"⚠️ {module_name} not available", extra={"arkalia_module": "core"}
                    )

            except Exception as e:
                ark_logger.error(
                    f"❌ Error initializing {module_name}: {e}", extra={"arkalia_module": "core"}
                )

    async def _start_monitoring_tasks(self) -> None:
        """Démarre les tasks de monitoring"""
        # Task de health check
        self.health_check_task = asyncio.create_task(self._health_check_loop())

        # Task cognitive (si activé)
        if self.config.cognitive_mode_enabled:
            self.cognitive_task = asyncio.create_task(self._cognitive_loop())

    async def execute_cycle(self) -> dict[str, Any]:
        """Exécute un cycle d'orchestration"""
        cycle_start = time.time()
        self.cycle_count += 1

        ark_logger.info(
            f"🌟 CYCLE #{self.cycle_count} - Mode: {self.current_cycle_mode.value}",
            extra={"arkalia_module": "core"},
        )

        cycle_results: dict[str, Any] = {}
        operations_this_cycle = 0
        successful_this_cycle = 0

        # Exécuter tous les modules en parallèle
        tasks = []
        for module_name, wrapper in self.modules.items():
            if wrapper.status != ModuleStatus.OFFLINE:
                task = asyncio.create_task(self._execute_module(module_name, wrapper))
                tasks.append((module_name, task))

        # Attendre tous les résultats
        for module_name, task in tasks:
            try:
                result = await task
                cycle_results[module_name] = result
                operations_this_cycle += 1

                if result.get("status") == "success":
                    successful_this_cycle += 1
                    self.modules[module_name].update_success()
                else:
                    self.modules[module_name].update_error(result.get("error", "Unknown error"))

            except Exception as e:
                ark_logger.error(
                    f"❌ Error executing {module_name}: {e}", extra={"arkalia_module": "core"}
                )
                cycle_results[module_name] = {"status": "error", "error": str(e)}
                self.modules[module_name].update_error(str(e))

        # Mettre à jour les statistiques
        self.total_operations += operations_this_cycle
        self.successful_operations += successful_this_cycle
        self.failed_operations += operations_this_cycle - successful_this_cycle

        # Adapter le mode de cycle
        await self._adapt_cycle_mode(cycle_results, successful_this_cycle, operations_this_cycle)

        # Mettre à jour l'état global
        cycle_duration = time.time() - cycle_start
        cycle_results["_metadata"] = {
            "cycle_number": self.cycle_count,
            "cycle_mode": self.current_cycle_mode.value,
            "duration": cycle_duration,
            "operations": operations_this_cycle,
            "successful": successful_this_cycle,
        }

        return cycle_results

    async def _execute_module(self, module_name: str, wrapper: ModuleWrapper) -> dict[str, Any]:
        """Exécute un module spécifique"""
        try:
            # Vérifier la santé du module
            health_status = self.health_monitor.check_health()
            if health_status.get("status") != "ok":
                return {"status": "error", "error": "Module health check failed"}

            # Exécuter le module (utiliser health_check par défaut)
            result = wrapper.instance.health_check()

            return {"status": "success", "result": result, "execution_time": time.time()}

        except Exception as e:
            ark_logger.error(
                f"❌ Error executing {module_name}: {e}", extra={"arkalia_module": "core"}
            )
            return {"status": "error", "error": str(e)}

    async def _adapt_cycle_mode(self, cycle_results: dict, successful: int, total: int) -> None:
        """Adapte le mode de cycle selon les résultats"""
        success_rate = successful / total if total > 0 else 0

        # Logique d'adaptation du mode
        if success_rate < 0.3:
            self.current_cycle_mode = CycleMode.URGENT
        elif success_rate < 0.7:
            self.current_cycle_mode = CycleMode.NORMAL
        elif success_rate > 0.9:
            self.current_cycle_mode = CycleMode.DEEP_ANALYSIS
        else:
            self.current_cycle_mode = CycleMode.NORMAL

    async def _health_check_loop(self) -> None:
        """Boucle de vérification de santé"""
        while self.is_running:
            try:
                self.health_monitor.check_health()
                await asyncio.sleep(self.config.health_check_interval)
            except Exception as e:
                ark_logger.error(f"❌ Health check error: {e}", extra={"arkalia_module": "core"})
                await asyncio.sleep(5)

    async def _cognitive_loop(self) -> None:
        """Boucle cognitive (si activée)"""
        while self.is_running:
            try:
                # Logique cognitive simplifiée
                if self.current_cycle_mode == CycleMode.COGNITIVE_BOOST:
                    self.cognitive_events += 1
                    ark_logger.info(
                        f"🧠 Cognitive event #{self.cognitive_events}",
                        extra={"arkalia_module": "core"},
                    )

                await asyncio.sleep(60)  # Check toutes les minutes
            except Exception as e:
                ark_logger.error(f"❌ Cognitive loop error: {e}", extra={"arkalia_module": "core"})
                await asyncio.sleep(5)

    def get_status(self) -> dict[str, Any]:
        """Retourne le statut complet de l'orchestrateur"""
        return {
            "orchestrator": {
                "status": "running" if self.is_running else "stopped",
                "cycle_count": self.cycle_count,
                "current_mode": self.current_cycle_mode.value,
                "uptime": time.time() - self.start_time,
            },
            "modules": {
                name: {
                    "status": wrapper.status.value,
                    "execution_count": wrapper.execution_count,
                    "error_count": wrapper.error_count,
                    "last_execution": (
                        wrapper.last_execution.isoformat() if wrapper.last_execution else None
                    ),
                    "cognitive_score": wrapper.cognitive_score,
                }
                for name, wrapper in self.modules.items()
            },
            "statistics": {
                "total_operations": self.total_operations,
                "successful_operations": self.successful_operations,
                "failed_operations": self.failed_operations,
                "success_rate": (
                    self.successful_operations / self.total_operations
                    if self.total_operations > 0
                    else 0
                ),
                "cognitive_events": self.cognitive_events,
                "recovery_events": self.recovery_events,
            },
            "health": self.health_monitor.check_health(),
        }

    async def shutdown(self) -> None:
        """Arrête l'orchestrateur proprement"""
        ark_logger.info("🛑 Shutting down Core Orchestrator...", extra={"arkalia_module": "core"})

        self.is_running = False

        # Arrêter les tasks
        if self.health_check_task:
            self.health_check_task.cancel()
        if self.cognitive_task:
            self.cognitive_task.cancel()

        # Arrêter tous les modules
        for wrapper in self.modules.values():
            try:
                wrapper.instance.shutdown()
            except Exception as e:
                ark_logger.error(
                    f"❌ Error shutting down {wrapper.name}: {e}", extra={"arkalia_module": "core"}
                )

        ark_logger.info("✅ Core Orchestrator shutdown complete", extra={"arkalia_module": "core"})

    # === IMPLÉMENTATION DES MÉTHODES DE L'INTERFACE IORCHESTRATOR ===

    def register_module(self, name: str, module: IModule) -> bool:
        """Enregistrement d'un module"""
        try:
            if name in self.modules:
                ark_logger.warning(
                    f"Module déjà enregistré : {name}", extra={"arkalia_module": "core"}
                )
                return False

            wrapper = ModuleWrapper(name, module)
            self.modules[name] = wrapper
            ark_logger.info(f"✅ Module enregistré : {name}", extra={"arkalia_module": "core"})
            return True

        except Exception as e:
            ark_logger.error(
                f"❌ Erreur enregistrement module {name}: {e}", extra={"arkalia_module": "core"}
            )
            return False

    def unregister_module(self, name: str) -> bool:
        """Désenregistrement d'un module"""
        try:
            if name in self.modules:
                del self.modules[name]
                ark_logger.info(
                    f"✅ Module désenregistré : {name}", extra={"arkalia_module": "core"}
                )
                return True
            return False

        except Exception as e:
            ark_logger.error(
                f"❌ Erreur désenregistrement module {name}: {e}", extra={"arkalia_module": "core"}
            )
            return False

    def get_module(self, name: str) -> IModule | None:
        """Récupération d'un module"""
        wrapper = self.modules.get(name)
        return wrapper.instance if wrapper else None

    def list_modules(self) -> list[str]:
        """Liste des modules enregistrés"""
        return list(self.modules.keys())

    def initialize_all_modules(self) -> dict[str, bool]:
        """Initialisation de tous les modules"""
        results = {}
        for name, wrapper in self.modules.items():
            try:
                results[name] = wrapper.instance.initialize()
                if results[name]:
                    wrapper.update_success()
                else:
                    wrapper.update_error("Initialization failed")
            except Exception as e:
                ark_logger.error(
                    f"❌ Erreur init module {name}: {e}", extra={"arkalia_module": "core"}
                )
                results[name] = False
                wrapper.update_error(str(e))
        return results

    def shutdown_all_modules(self) -> dict[str, bool]:
        """Arrêt de tous les modules"""
        results = {}
        for name, wrapper in self.modules.items():
            try:
                results[name] = wrapper.instance.shutdown()
            except Exception as e:
                ark_logger.error(
                    f"❌ Erreur shutdown module {name}: {e}", extra={"arkalia_module": "core"}
                )
                results[name] = False
        return results

    def health_check_all(self) -> dict[str, dict[str, Any]]:
        """Vérification de santé de tous les modules"""
        results = {}
        for name, wrapper in self.modules.items():
            try:
                results[name] = wrapper.instance.health_check()
            except Exception as e:
                ark_logger.error(
                    f"❌ Erreur health check module {name}: {e}", extra={"arkalia_module": "core"}
                )
                results[name] = {"status": "error", "error": str(e)}
        return results

    def get_system_status(self) -> dict[str, Any]:
        """Statut global du système"""
        return {
            "modules": self.list_modules(),
            "health": self.health_monitor.check_health(),
            "config": self.config_manager.get_config(),
            "orchestrator": {
                "status": "running" if self.is_running else "stopped",
                "cycle_count": self.cycle_count,
                "current_mode": self.current_cycle_mode.value,
            },
        }


async def run_core_orchestrator(
    config: CoreOrchestratorConfig | None = None,
    max_cycles: int | None = None,
) -> None:
    """Fonction principale pour exécuter l'orchestrateur central"""
    orchestrator = CoreOrchestrator(config)

    try:
        # Initialiser
        if not await orchestrator.initialize():
            ark_logger.error(
                "❌ Failed to initialize orchestrator", extra={"arkalia_module": "core"}
            )
            return

        # Boucle principale
        cycle_count = 0
        while orchestrator.is_running:
            if max_cycles and cycle_count >= max_cycles:
                break

            # Exécuter un cycle
            await orchestrator.execute_cycle()
            cycle_count += 1

            # Attendre selon le mode de cycle
            interval = config.cycle_intervals[orchestrator.current_cycle_mode] if config else 30.0
            await asyncio.sleep(interval)

    except KeyboardInterrupt:
        ark_logger.info("🛑 Interruption utilisateur", extra={"arkalia_module": "core"})
    except Exception as e:
        ark_logger.error(f"❌ Orchestrator error: {e}", extra={"arkalia_module": "core"})
    finally:
        await orchestrator.shutdown()


if __name__ == "__main__":
    # Exécuter l'orchestrateur
    asyncio.run(run_core_orchestrator())

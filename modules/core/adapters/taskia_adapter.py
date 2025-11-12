#!/usr/bin/env python3
"""
🔗 TaskIA Adapter - Adaptateur SOLID pour TaskIA
🎯 Interface entre TaskIA existant et l'architecture SOLID
"""

from typing import Any

from core.ark_logger import ark_logger

from ..interfaces.module_interface import IModuleWithProcessing


class TaskIAAdapter(IModuleWithProcessing):
    """
    🔗 Adaptateur SOLID pour TaskIA
    🎯 Interface entre TaskIA existant et l'architecture SOLID
    """

    def __init__(self):
        self.name = "taskia"
        self.version = "1.0.0"
        self.enabled = False
        self._initialized = False

        # Statistiques de traitement
        self._processing_stats = {
            "total_tasks": 0,
            "successful_tasks": 0,
            "failed_tasks": 0,
            "average_processing_time": 0.0,
            "last_task": None,
        }

    def initialize(self) -> bool:
        """Initialise l'adaptateur TaskIA"""
        try:
            ark_logger.info("🔗 Initialisation TaskIA Adapter...", extra={"arkalia_module": "core"})

            # TaskIA est un module simple, pas besoin d'import complexe
            # Vérifier que le module est disponible
            try:
                from modules.taskia.core import taskia_main

                self._taskia_main = taskia_main
            except ImportError as e:
                ark_logger.error(
                    f"❌ Module TaskIA non disponible: {e}", extra={"arkalia_module": "core"}
                )
                return False

            self.enabled = True
            self._initialized = True

            ark_logger.info(
                "✅ TaskIA Adapter initialisé avec succès", extra={"arkalia_module": "core"}
            )
            return True

        except Exception as e:
            ark_logger.error(
                f"❌ Erreur initialisation TaskIA Adapter: {e}", extra={"arkalia_module": "core"}
            )
            return False

    def health_check(self) -> dict[str, Any]:
        """Vérification de santé de TaskIA"""
        try:
            if not self._initialized:
                return {
                    "status": "error",
                    "message": "TaskIA Adapter non initialisé",
                    "module": self.name,
                }

            # TaskIA est un module simple, health check basique
            health_data = {
                "status": "ok",
                "module": self.name,
                "version": self.version,
                "enabled": self.enabled,
                "processing_stats": self._processing_stats,
                "last_task": self._processing_stats["last_task"],
            }

            return health_data

        except Exception as e:
            ark_logger.error(
                f"❌ Erreur health check TaskIA Adapter: {e}", extra={"arkalia_module": "core"}
            )
            return {
                "status": "error",
                "message": str(e),
                "module": self.name,
            }

    def get_name(self) -> str:
        """Nom du module"""
        return self.name

    def get_version(self) -> str:
        """Version du module"""
        return self.version

    def is_enabled(self) -> bool:
        """État d'activation du module"""
        return self.enabled

    def shutdown(self) -> bool:
        """Arrêt propre du module"""
        try:
            ark_logger.info("🛑 Shutdown TaskIA Adapter...", extra={"arkalia_module": "core"})

            self.enabled = False
            self._initialized = False

            ark_logger.info("✅ TaskIA Adapter shutdown complet", extra={"arkalia_module": "core"})
            return True

        except Exception as e:
            ark_logger.error(
                f"❌ Erreur shutdown TaskIA Adapter: {e}", extra={"arkalia_module": "core"}
            )
            return False

    def process(self, data: dict[str, Any]) -> dict[str, Any]:
        """Traitement de données via TaskIA"""
        try:
            if not self._initialized:
                return {
                    "status": "error",
                    "message": "TaskIA Adapter non initialisé",
                    "summary": "",
                }

            # Extraire le contexte des données
            context = data.get("context", {})
            if not context:
                context = {"default": "empty_context"}

            # Appeler TaskIA pour l'analyse
            import time

            start_time = time.time()

            summary = self._taskia_main(context)

            processing_time = time.time() - start_time

            # Mettre à jour les statistiques
            self._update_processing_stats(processing_time, True)

            # Enrichir le résultat
            processed_result = {
                "status": "success",
                "module": self.name,
                "summary": summary,
                "processing_time": processing_time,
                "processing_stats": self._processing_stats,
            }

            ark_logger.info(
                f"✅ TaskIA summary généré (temps: {processing_time:.3f}s)",
                extra={"arkalia_module": "core"},
            )
            return processed_result

        except Exception as e:
            ark_logger.error(f"❌ Erreur traitement TaskIA: {e}", extra={"arkalia_module": "core"})

            # Mettre à jour les statistiques d'erreur
            self._update_processing_stats(0.0, False)

            return {
                "status": "error",
                "message": str(e),
                "summary": "",
                "module": self.name,
            }

    def get_processing_stats(self) -> dict[str, Any]:
        """Statistiques de traitement"""
        return {
            "module": self.name,
            "total_tasks": self._processing_stats["total_tasks"],
            "successful_tasks": self._processing_stats["successful_tasks"],
            "failed_tasks": self._processing_stats["failed_tasks"],
            "success_rate": (
                self._processing_stats["successful_tasks"] / self._processing_stats["total_tasks"]
                if self._processing_stats["total_tasks"] > 0
                else 0.0
            ),
            "average_processing_time": self._processing_stats["average_processing_time"],
            "last_task": self._processing_stats["last_task"],
        }

    def _update_processing_stats(self, processing_time: float, success: bool) -> None:
        """Met à jour les statistiques de traitement"""
        self._processing_stats["total_tasks"] += 1

        if success:
            self._processing_stats["successful_tasks"] += 1
        else:
            self._processing_stats["failed_tasks"] += 1

        # Mettre à jour le temps de traitement moyen
        total_successful = self._processing_stats["successful_tasks"]
        if total_successful > 0:
            current_avg = self._processing_stats["average_processing_time"]
            new_avg = ((current_avg * (total_successful - 1)) + processing_time) / total_successful
            self._processing_stats["average_processing_time"] = new_avg

        self._processing_stats["last_task"] = {
            "success": success,
            "processing_time": processing_time,
            "timestamp": "now",  # En production, utiliser datetime.now().isoformat()
        }

    def analyze_context(self, context: dict[str, Any]) -> dict[str, Any]:
        """Méthode spécifique pour l'analyse de contexte TaskIA"""
        return self.process({"context": context})


# Factory function pour créer l'adaptateur
def create_taskia_adapter() -> TaskIAAdapter:
    """Crée une instance de l'adaptateur TaskIA"""
    return TaskIAAdapter()

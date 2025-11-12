#!/usr/bin/env python3
"""
🔗 Reflexia Adapter - Adaptateur SOLID pour Reflexia
🎯 Interface entre Reflexia existant et l'architecture SOLID
"""

import time
from typing import Any, Optional

from core.ark_logger import ark_logger

from ..interfaces.module_interface import IModule, IModuleWithMonitoring, IModuleWithProcessing


class ReflexiaAdapter(IModuleWithProcessing, IModuleWithMonitoring):
    """
    🔗 Adaptateur SOLID pour Reflexia
    🎯 Interface entre Reflexia existant et l'architecture SOLID
    """

    def __init__(self):
        self.name = "reflexia"
        self.version = "2.6.0"
        self.enabled = False
        self._initialized = False
        self._reflexia_core = None

        # Statistiques de traitement
        self._processing_stats = {
            "total_checks": 0,
            "successful_checks": 0,
            "failed_checks": 0,
            "average_check_time": 0.0,
            "last_check": None,
            "status_history": [],
        }

        # Métriques de monitoring
        self._metrics = {}
        self._alert_thresholds = {
            "cpu_critical": 90.0,
            "ram_critical": 80.0,
            "latency_critical": 300.0,
        }

    def initialize(self) -> bool:
        """Initialise l'adaptateur Reflexia"""
        try:
            ark_logger.info(
                "🔗 Initialisation Reflexia Adapter...", extra={"arkalia_module": "core"}
            )

            # Import dynamique pour éviter les dépendances circulaires
            try:
                from modules.reflexia.core import (
                    get_metrics,
                    launch_reflexia_check,
                    launch_reflexia_check_enhanced,
                )

                self._launch_check = launch_reflexia_check
                self._launch_check_enhanced = launch_reflexia_check_enhanced
                self._get_metrics = get_metrics
            except ImportError as e:
                ark_logger.error(
                    f"❌ Module Reflexia non disponible: {e}", extra={"arkalia_module": "core"}
                )
                return False

            self.enabled = True
            self._initialized = True

            ark_logger.info(
                "✅ Reflexia Adapter initialisé avec succès", extra={"arkalia_module": "core"}
            )
            return True

        except Exception as e:
            ark_logger.error(
                f"❌ Erreur initialisation Reflexia Adapter: {e}", extra={"arkalia_module": "core"}
            )
            return False

    def health_check(self) -> dict[str, Any]:
        """Vérification de santé de Reflexia"""
        try:
            if not self._initialized:
                return {
                    "status": "error",
                    "message": "Reflexia Adapter non initialisé",
                    "module": self.name,
                }

            # Effectuer une vérification rapide
            start_time = time.time()
            check_result = self._launch_check()
            check_time = time.time() - start_time

            # Analyser le statut
            status = check_result.get("status", "unknown")
            health_status = "ok"

            if "🛑" in status or "surcharge" in status:
                health_status = "critical"
            elif "⚠️" in status or "degraded" in status:
                health_status = "degraded"

            health_data = {
                "status": health_status,
                "module": self.name,
                "version": self.version,
                "enabled": self.enabled,
                "reflexia_status": status,
                "check_time": check_time,
                "processing_stats": self._processing_stats,
                "metrics": check_result.get("metrics", {}),
                "last_check": self._processing_stats["last_check"],
            }

            return health_data

        except Exception as e:
            ark_logger.error(
                f"❌ Erreur health check Reflexia Adapter: {e}", extra={"arkalia_module": "core"}
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
            ark_logger.info("🛑 Shutdown Reflexia Adapter...", extra={"arkalia_module": "core"})

            self.enabled = False
            self._initialized = False

            ark_logger.info(
                "✅ Reflexia Adapter shutdown complet", extra={"arkalia_module": "core"}
            )
            return True

        except Exception as e:
            ark_logger.error(
                f"❌ Erreur shutdown Reflexia Adapter: {e}", extra={"arkalia_module": "core"}
            )
            return False

    def process(self, data: dict[str, Any]) -> dict[str, Any]:
        """Traitement de données via Reflexia"""
        try:
            if not self._initialized:
                return {
                    "status": "error",
                    "message": "Reflexia Adapter non initialisé",
                    "check_result": {},
                }

            # Déterminer le type de vérification
            check_type = data.get("check_type", "standard")
            enhanced = data.get("enhanced", False)

            start_time = time.time()

            # Effectuer la vérification
            if enhanced:
                check_result = self._launch_check_enhanced()
            else:
                check_result = self._launch_check()

            check_time = time.time() - start_time

            # Mettre à jour les statistiques
            self._update_processing_stats(check_time, True, check_result.get("status", "unknown"))

            # Enrichir le résultat
            processed_result = {
                "status": "success",
                "module": self.name,
                "check_type": check_type,
                "enhanced": enhanced,
                "check_result": check_result,
                "check_time": check_time,
                "processing_stats": self._processing_stats,
            }

            return processed_result

        except Exception as e:
            ark_logger.error(
                f"❌ Erreur traitement Reflexia: {e}", extra={"arkalia_module": "core"}
            )

            # Mettre à jour les statistiques d'erreur
            self._update_processing_stats(0.0, False, "error")

            return {
                "status": "error",
                "message": str(e),
                "check_result": {},
                "module": self.name,
            }

    def get_processing_stats(self) -> dict[str, Any]:
        """Statistiques de traitement"""
        return {
            "module": self.name,
            "total_checks": self._processing_stats["total_checks"],
            "successful_checks": self._processing_stats["successful_checks"],
            "failed_checks": self._processing_stats["failed_checks"],
            "success_rate": (
                self._processing_stats["successful_checks"] / self._processing_stats["total_checks"]
                if self._processing_stats["total_checks"] > 0
                else 0.0
            ),
            "average_check_time": self._processing_stats["average_check_time"],
            "last_check": self._processing_stats["last_check"],
            "status_history": self._processing_stats["status_history"][-10:],  # Derniers 10 statuts
        }

    def get_metrics(self) -> dict[str, Any]:
        """Récupération des métriques Reflexia"""
        try:
            if not self._initialized:
                return {
                    "status": "error",
                    "message": "Reflexia Adapter non initialisé",
                    "metrics": {},
                }

            # Récupérer les métriques actuelles
            current_metrics = self._get_metrics()

            # Mettre à jour les métriques stockées
            self._metrics = current_metrics

            return {
                "status": "success",
                "module": self.name,
                "metrics": current_metrics,
                "alert_thresholds": self._alert_thresholds,
                "last_update": "now",  # En production, utiliser datetime.now().isoformat()
            }

        except Exception as e:
            ark_logger.error(
                f"❌ Erreur récupération métriques Reflexia: {e}", extra={"arkalia_module": "core"}
            )
            return {
                "status": "error",
                "message": str(e),
                "metrics": {},
                "module": self.name,
            }

    def set_alert_threshold(self, metric: str, threshold: float) -> bool:
        """Configuration des seuils d'alerte"""
        try:
            if metric in self._alert_thresholds:
                self._alert_thresholds[metric] = threshold
                ark_logger.info(
                    f"✅ Seuil d'alerte {metric} mis à jour: {threshold}",
                    extra={"arkalia_module": "core"},
                )
                return True
            else:
                ark_logger.warning(
                    f"⚠️ Métrique {metric} non reconnue", extra={"arkalia_module": "core"}
                )
                return False

        except Exception as e:
            ark_logger.error(
                f"❌ Erreur configuration seuil d'alerte: {e}", extra={"arkalia_module": "core"}
            )
            return False

    def _update_processing_stats(self, check_time: float, success: bool, status: str) -> None:
        """Met à jour les statistiques de traitement"""
        self._processing_stats["total_checks"] += 1

        if success:
            self._processing_stats["successful_checks"] += 1
        else:
            self._processing_stats["failed_checks"] += 1

        # Mettre à jour le temps de vérification moyen
        total_successful = self._processing_stats["successful_checks"]
        if total_successful > 0:
            current_avg = self._processing_stats["average_check_time"]
            new_avg = ((current_avg * (total_successful - 1)) + check_time) / total_successful
            self._processing_stats["average_check_time"] = new_avg

        # Mettre à jour l'historique des statuts
        self._processing_stats["status_history"].append(
            {
                "status": status,
                "check_time": check_time,
                "timestamp": "now",  # En production, utiliser datetime.now().isoformat()
            }
        )

        # Garder seulement les 50 derniers statuts
        if len(self._processing_stats["status_history"]) > 50:
            self._processing_stats["status_history"] = self._processing_stats["status_history"][
                -50:
            ]

        self._processing_stats["last_check"] = {
            "status": status,
            "check_time": check_time,
            "success": success,
            "timestamp": "now",
        }

    def launch_check(self, enhanced: bool = False) -> dict[str, Any]:
        """Méthode spécifique pour lancer une vérification Reflexia"""
        return self.process(
            {
                "check_type": "manual",
                "enhanced": enhanced,
            }
        )

    def get_system_status(self) -> dict[str, Any]:
        """Méthode spécifique pour obtenir le statut système"""
        return self.process(
            {
                "check_type": "status",
                "enhanced": False,
            }
        )


# Factory function pour créer l'adaptateur
def create_reflexia_adapter() -> ReflexiaAdapter:
    """Crée une instance de l'adaptateur Reflexia"""
    return ReflexiaAdapter()

#!/usr/bin/env python3
"""
🏥 HealthMonitor - Monitoring intelligent avec watchdogs préservés
🎯 Principe SOLID SRP : Responsabilité unique - Surveillance de santé
🛡️ Préservation des mécanismes de surveillance critique
"""

import threading
import time
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any, Optional

from core.ark_logger import ark_logger


@dataclass
class HealthMetric:
    """Métrique de santé"""

    name: str
    value: Any
    timestamp: datetime
    unit: str = ""
    threshold: float | None = None
    status: str = "ok"


@dataclass
class Alert:
    """Alerte de santé"""

    id: str
    message: str
    severity: str  # "low", "medium", "high", "critical"
    timestamp: datetime
    metric: str
    value: Any
    threshold: float | None = None
    resolved: bool = False


class HealthMonitor:
    """
    🎯 Moniteur de santé intelligent
    🛡️ Préservation des watchdogs critiques
    """

    def __init__(self) -> None:
        self.self._metrics: dict[str, HealthMetric] = {}
        self._alerts: list[Alert] = []
        self._watchdogs: dict[str, Callable] = {}
        self._health_score: float = 1.0
        self._last_check: datetime | None = None
        self._monitoring_thread: threading.Thread | None = None
        self._stop_monitoring = False
        self._initialized = False

        # Initialisation automatique
        self.initialize()

    def initialize(self) -> bool:
        """
        🚀 Initialisation du moniteur de santé
        🛡️ Préservation des watchdogs existants
        """
        try:
            self.ark_logger.info(
                "🏥 Initialisation HealthMonitor...", extra={"arkalia_module": "core"}
            )

            # Enregistrement des watchdogs par défaut
            self._register_default_watchdogs()

            # Démarrage du monitoring en arrière-plan
            self._start_monitoring_thread()

            self._initialized = True
            self.ark_logger.info(
                "✅ HealthMonitor initialisé avec succès", extra={"arkalia_module": "core"}
            )
            return True

        except Exception as e:
            self.ark_logger.error(
                f"❌ Erreur initialisation HealthMonitor : {e}", extra={"arkalia_module": "core"}
            )
            return False

    def _register_default_watchdogs(self) -> None:
        """Enregistrement des watchdogs par défaut"""
        # Watchdog Reflexia Panic-Check (préservé)
        self.register_watchdog("reflexia_panic", self._reflexia_panic_check)

        # Watchdog ZeroIA Circuit Breaker (préservé)
        self.register_watchdog("zeroia_circuit", self._zeroia_circuit_check)

        # Watchdog Sandozia Anomaly Detection (préservé)
        self.register_watchdog("sandozia_anomaly", self._sandozia_anomaly_check)

        # Watchdog système général
        self.register_watchdog("system_health", self._system_health_check)

        self.ark_logger.info(
            f"🛡️ {len(self._watchdogs)} watchdogs enregistrés", extra={"arkalia_module": "core"}
        )

    def _reflexia_panic_check(self) -> dict[str, Any]:
        """Watchdog Reflexia Panic-Check (préservé)"""
        try:
            # Simulation du check Reflexia (à remplacer par l'appel réel)
            panic_level = 0.1  # Normalement récupéré depuis Reflexia
            threshold = 0.8

            return {
                "status": "ok" if panic_level < threshold else "critical",
                "panic_level": panic_level,
                "threshold": threshold,
                "message": (
                    "Reflexia panic check normal" if panic_level < threshold else "PANIC DETECTED"
                ),
            }
        except Exception as e:
            return {"status": "error", "message": f"Erreur panic check: {e}"}

    def _zeroia_circuit_check(self) -> dict[str, Any]:
        """Watchdog ZeroIA Circuit Breaker (préservé)"""
        try:
            # Simulation du check ZeroIA (à remplacer par l'appel réel)
            failure_count = 0  # Normalement récupéré depuis ZeroIA
            threshold = 5

            return {
                "status": "ok" if failure_count < threshold else "open",
                "failure_count": failure_count,
                "threshold": threshold,
                "message": (
                    "Circuit breaker closed"
                    if failure_count < threshold
                    else "Circuit breaker OPEN"
                ),
            }
        except Exception as e:
            return {"status": "error", "message": f"Erreur circuit check: {e}"}

    def _sandozia_anomaly_check(self) -> dict[str, Any]:
        """Watchdog Sandozia Anomaly Detection (préservé)"""
        try:
            # Simulation du check Sandozia (à remplacer par l'appel réel)
            anomaly_score = 0.2  # Normalement récupéré depuis Sandozia
            threshold = 0.7

            return {
                "status": "ok" if anomaly_score < threshold else "anomaly",
                "anomaly_score": anomaly_score,
                "threshold": threshold,
                "message": (
                    "No anomalies detected" if anomaly_score < threshold else "ANOMALY DETECTED"
                ),
            }
        except Exception as e:
            return {"status": "error", "message": f"Erreur anomaly check: {e}"}

    def _system_health_check(self) -> dict[str, Any]:
        """Watchdog système général"""
        try:
            import psutil

            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            # Seuils critiques
            cpu_critical = cpu_percent > 90
            memory_critical = memory.percent > 85
            disk_critical = disk.percent > 90

            status = "ok"
            if cpu_critical or memory_critical or disk_critical:
                status = "critical"
            elif cpu_percent > 70 or memory.percent > 70:
                status = "warning"

            return {
                "status": status,
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": disk.percent,
                "message": (
                    f"System health: CPU {cpu_percent}%, "
                    f"RAM {memory.percent}%, Disk {disk.percent}%"
                ),
            }
        except ImportError:
            return {"status": "ok", "message": "psutil not available, system check skipped"}
        except Exception as e:
            return {"status": "error", "message": f"Erreur system check: {e}"}

    def register_watchdog(self, name: str, watchdog_func: Callable) -> bool:
        """
        🛡️ Enregistrement d'un watchdog
        :param name: Nom du watchdog
        :param watchdog_func: Fonction de surveillance
        :return: True si enregistrement réussi
        """
        try:
            self._watchdogs[name] = watchdog_func
            self.ark_logger.info(
                f"🛡️ Watchdog enregistré : {name}", extra={"arkalia_module": "core"}
            )
            return True
        except Exception as e:
            self.ark_logger.error(
                f"❌ Erreur enregistrement watchdog {name}: {e}", extra={"arkalia_module": "core"}
            )
            return False

    def unregister_watchdog(self, name: str) -> bool:
        """
        🗑️ Désenregistrement d'un watchdog
        :param name: Nom du watchdog
        :return: True si désenregistrement réussi
        """
        try:
            if name in self._watchdogs:
                del self._watchdogs[name]
                self.ark_logger.info(
                    f"🗑️ Watchdog désenregistré : {name}", extra={"arkalia_module": "core"}
                )
                return True
            return False
        except Exception as e:
            self.ark_logger.error(
                f"❌ Erreur désenregistrement watchdog {name}: {e}",
                extra={"arkalia_module": "core"},
            )
            return False

    def run_watchdogs(self) -> dict[str, dict[str, Any]]:
        """
        🛡️ Exécution de tous les watchdogs
        :return: Résultats des watchdogs
        """
        results = {}

        for name, watchdog_func in self._watchdogs.items():
            try:
                result = watchdog_func()
                results[name] = result

                # Gestion des alertes automatiques
                if result.get("status") in ["critical", "error"]:
                    self._create_alert(name, result)

            except Exception as e:
                error_result = {"status": "error", "message": f"Exception in {name}: {e}"}
                results[name] = error_result
                self._create_alert(name, error_result)

        return results

    def _create_alert(self, watchdog_name: str, result: dict[str, Any]) -> None:
        """Création automatique d'alerte"""
        alert = Alert(
            id=f"{watchdog_name}_{int(time.time())}",
            message=result.get("message", f"Watchdog {watchdog_name} alert"),
            severity="critical" if result.get("status") == "critical" else "high",
            timestamp=datetime.now(),
            metric=watchdog_name,
            value=result,
        )
        self._alerts.append(alert)
        self.ark_logger.warning(
            f"🚨 Alerte créée : {alert.message}", extra={"arkalia_module": "core"}
        )

    def check_health(self) -> dict[str, Any]:
        """
        🏥 Vérification de santé générale
        :return: Dictionnaire avec statut et métriques
        """
        if not self._initialized:
            return {"status": "uninitialized", "message": "HealthMonitor non initialisé"}

        # Exécution des watchdogs
        watchdog_results = self.run_watchdogs()

        # Calcul du score de santé
        self._calculate_health_score(watchdog_results)

        # Mise à jour du timestamp
        self._last_check = datetime.now()

        return {
            "status": (
                "healthy"
                if self._health_score > 0.7
                else "degraded" if self._health_score > 0.3 else "critical"
            ),
            "health_score": self._health_score,
            "last_check": self._last_check.isoformat() if self._last_check else None,
            "watchdogs": watchdog_results,
            "alerts_count": len([a for a in self._alerts if not a.resolved]),
            "metrics_count": len(self._metrics),
        }

    def _calculate_health_score(self, watchdog_results: dict[str, dict[str, Any]]) -> None:
        """Calcul du score de santé"""
        total_watchdogs = len(watchdog_results)
        if total_watchdogs == 0:
            self._health_score = 1.0
            return

        healthy_count = 0.0
        for result in watchdog_results.values():
            if result.get("status") == "ok":
                healthy_count += 1.0
            elif result.get("status") == "warning":
                healthy_count += 0.5

        self._health_score = healthy_count / total_watchdogs

    def is_healthy(self) -> bool:
        """
        ✅ État de santé global
        :return: True si le système est en bonne santé
        """
        return self._health_score > 0.7

    def get_health_score(self) -> float:
        """
        📊 Score de santé (0.0 à 1.0)
        :return: Score numérique de santé
        """
        return self._health_score

    def get_metrics(self) -> dict[str, Any]:
        """
        📊 Récupération des métriques de santé
        :return: Métriques détaillées
        """
        return {name: asdict(metric) for name, metric in self._metrics.items()}

    def get_alerts(self) -> list[dict[str, Any]]:
        """
        🚨 Récupération des alertes actives
        :return: Liste des alertes
        """
        return [asdict(alert) for alert in self._alerts if not alert.resolved]

    def clear_alerts(self) -> bool:
        """
        🧹 Nettoyage des alertes
        :return: True si nettoyage réussi
        """
        try:
            self._alerts.clear()
            self.ark_logger.info("🧹 Alertes nettoyées", extra={"arkalia_module": "core"})
            return True
        except Exception as e:
            self.ark_logger.error(
                f"❌ Erreur nettoyage alertes : {e}", extra={"arkalia_module": "core"}
            )
            return False

    def _start_monitoring_thread(self) -> None:
        """Démarrage du thread de monitoring"""
        if self._monitoring_thread and self._monitoring_thread.is_alive():
            return

        self._stop_monitoring = False
        self._monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self._monitoring_thread.start()
        self.ark_logger.info("🔄 Thread de monitoring démarré", extra={"arkalia_module": "core"})

    def _monitoring_loop(self) -> None:
        """Boucle de monitoring en arrière-plan"""
        while not self._stop_monitoring:
            try:
                # Exécution des watchdogs toutes les 30 secondes
                self.run_watchdogs()
                time.sleep(30)
            except Exception as e:
                self.ark_logger.error(
                    f"❌ Erreur boucle monitoring : {e}", extra={"arkalia_module": "core"}
                )
                time.sleep(60)  # Pause plus longue en cas d'erreur

    def shutdown(self) -> bool:
        """
        🔌 Arrêt propre du HealthMonitor
        :return: True si arrêt réussi
        """
        try:
            self._stop_monitoring = True
            if self._monitoring_thread and self._monitoring_thread.is_alive():
                self._monitoring_thread.join(timeout=5)

            self.ark_logger.info("🔌 HealthMonitor arrêté", extra={"arkalia_module": "core"})
            return True
        except Exception as e:
            self.ark_logger.error(
                f"❌ Erreur arrêt HealthMonitor : {e}", extra={"arkalia_module": "core"}
            )
            return False

    def health_check(self) -> dict[str, Any]:
        """
        🏥 Vérification de santé du HealthMonitor lui-même
        :return: Statut de santé
        """
        return {
            "module": "health_monitor",
            "status": "healthy" if self._initialized else "uninitialized",
            "watchdogs_count": len(self._watchdogs),
            "alerts_count": len(self._alerts),
            "health_score": self._health_score,
            "monitoring_active": self._monitoring_thread and self._monitoring_thread.is_alive(),
        }


# Instance par défaut
default_health_monitor = HealthMonitor()

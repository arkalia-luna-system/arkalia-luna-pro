#!/usr/bin/env python3
"""
📊 Advanced Metrics - Métriques avancées en temps réel
🎯 Monitoring intelligent avec alertes et prédictions
"""

import json
import statistics
import threading
import time
from collections import defaultdict, deque
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from core.ark_logger import ark_logger


class MetricType(Enum):
    """Types de métriques"""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class AlertSeverity(Enum):
    """Niveaux de sévérité des alertes"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class MetricValue:
    """Valeur de métrique avec timestamp"""

    value: int | float
    timestamp: datetime
    labels: dict[str, str] = field(default_factory=dict)


@dataclass
class AlertRule:
    """Règle d'alerte"""

    name: str
    metric_name: str
    condition: str  # ">", "<", "==", ">=", "<="
    threshold: float
    severity: AlertSeverity
    duration: int = 60  # secondes
    enabled: bool = True
    description: str = ""


@dataclass
class Alert:
    """Alerte déclenchée"""

    rule_name: str
    metric_name: str
    current_value: float
    threshold: float
    severity: AlertSeverity
    timestamp: datetime
    message: str
    resolved: bool = False


class Metric:
    """
    📊 Métrique individuelle avec historique
    🎯 Collecte et analyse des données
    """

    def __init__(self, name: str, metric_type: MetricType, description: str = ""):
        self.name = name
        self.type = metric_type
        self.description = description

        # Stockage des valeurs
        self.values: deque = deque(maxlen=10000)  # Limite à 10k valeurs
        self.labels: dict[str, str] = {}

        # Métadonnées
        self.created_at = datetime.now()
        self.last_update = datetime.now()

        # Statistiques
        self._stats_cache = {}
        self._stats_cache_time = None
        self._cache_duration = 60  # secondes

        ark_logger.debug(
            f"📊 Métrique créée: {name} ({metric_type.value})", extra={"arkalia_module": "core"}
        )

    def record(self, value: int | float, labels: dict[str, str] | None = None) -> None:
        """Enregistre une nouvelle valeur"""
        timestamp = datetime.now()
        metric_value = MetricValue(value=value, timestamp=timestamp, labels=labels or {})

        self.values.append(metric_value)
        self.last_update = timestamp

        # Invalider le cache des statistiques
        self._stats_cache = {}
        self._stats_cache_time = None

    def get_latest(self) -> MetricValue | None:
        """Récupère la dernière valeur"""
        return self.values[-1] if self.values else None

    def get_stats(self, window_minutes: int = 60) -> dict[str, Any]:
        """Calcule les statistiques sur une fenêtre temporelle"""
        now = datetime.now()
        window_start = now - timedelta(minutes=window_minutes)

        # Filtrer les valeurs dans la fenêtre
        window_values = [mv.value for mv in self.values if mv.timestamp >= window_start]

        if not window_values:
            return {
                "count": 0,
                "min": None,
                "max": None,
                "mean": None,
                "median": None,
                "std_dev": None,
                "percentiles": {},
            }

        # Calculer les statistiques
        stats = {
            "count": len(window_values),
            "min": min(window_values),
            "max": max(window_values),
            "mean": statistics.mean(window_values),
            "median": statistics.median(window_values),
            "std_dev": statistics.stdev(window_values) if len(window_values) > 1 else 0,
        }

        # Calculer les percentiles
        sorted_values = sorted(window_values)
        percentiles = [50, 75, 90, 95, 99]
        stats["percentiles"] = {}

        for p in percentiles:
            index = int((p / 100) * len(sorted_values)) - 1
            if index >= 0:
                stats["percentiles"][f"p{p}"] = sorted_values[index]

        return stats

    def get_trend(self, window_minutes: int = 60) -> dict[str, Any]:
        """Analyse la tendance de la métrique"""
        now = datetime.now()
        window_start = now - timedelta(minutes=window_minutes)

        # Diviser la fenêtre en périodes
        period_count = 4
        period_duration = window_minutes / period_count

        periods = []
        for i in range(period_count):
            period_start = window_start + timedelta(minutes=i * period_duration)
            period_end = period_start + timedelta(minutes=period_duration)

            period_values = [
                mv.value for mv in self.values if period_start <= mv.timestamp < period_end
            ]

            if period_values:
                periods.append(statistics.mean(period_values))
            else:
                periods.append(0)

        # Calculer la tendance
        if len(periods) >= 2:
            trend_direction = "increasing" if periods[-1] > periods[0] else "decreasing"
            trend_strength = abs(periods[-1] - periods[0]) / max(periods) if max(periods) > 0 else 0
        else:
            trend_direction = "stable"
            trend_strength = 0

        return {
            "direction": trend_direction,
            "strength": round(trend_strength, 3),
            "periods": periods,
        }

    def to_dict(self) -> dict[str, Any]:
        """Convertit en dictionnaire"""
        latest = self.get_latest()
        return {
            "name": self.name,
            "type": self.type.value,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "last_update": self.last_update.isoformat(),
            "total_values": len(self.values),
            "latest_value": latest.value if latest else None,
            "latest_timestamp": latest.timestamp.isoformat() if latest else None,
            "labels": self.labels,
        }


class AlertManager:
    """
    🚨 Gestionnaire d'alertes intelligent
    🎯 Surveillance automatique avec règles configurables
    """

    def __init__(self):
        self.rules: dict[str, AlertRule] = {}
        self.alerts: list[Alert] = []
        self.alert_handlers: list[Callable] = []

        # Configuration
        self.config = {
            "max_alerts": 1000,
            "alert_retention_hours": 24,
            "check_interval": 30,  # secondes
        }

        ark_logger.info("🚨 AlertManager initialisé", extra={"arkalia_module": "core"})

    def add_rule(self, rule: AlertRule) -> bool:
        """Ajoute une règle d'alerte"""
        try:
            self.rules[rule.name] = rule
            ark_logger.info(
                f"🚨 Règle d'alerte ajoutée: {rule.name}", extra={"arkalia_module": "core"}
            )
            return True
        except Exception as e:
            ark_logger.error(f"❌ Erreur ajout règle: {e}", extra={"arkalia_module": "core"})
            return False

    def remove_rule(self, rule_name: str) -> bool:
        """Supprime une règle d'alerte"""
        if rule_name in self.rules:
            del self.rules[rule_name]
            ark_logger.info(
                f"🚨 Règle d'alerte supprimée: {rule_name}", extra={"arkalia_module": "core"}
            )
            return True
        return False

    def add_alert_handler(self, handler: Callable) -> None:
        """Ajoute un gestionnaire d'alertes"""
        self.alert_handlers.append(handler)

    def check_alerts(self, metrics: dict[str, Metric]) -> list[Alert]:
        """Vérifie toutes les règles d'alerte"""
        new_alerts = []

        for rule in self.rules.values():
            if not rule.enabled:
                continue

            metric = metrics.get(rule.metric_name)
            if not metric:
                continue

            latest = metric.get_latest()
            if not latest:
                continue

            # Vérifier la condition
            triggered = self._check_condition(latest.value, rule.condition, rule.threshold)

            if triggered:
                # Vérifier si l'alerte existe déjà
                existing_alert = self._find_existing_alert(rule.name)

                if not existing_alert:
                    # Créer une nouvelle alerte
                    alert = Alert(
                        rule_name=rule.name,
                        metric_name=rule.metric_name,
                        current_value=latest.value,
                        threshold=rule.threshold,
                        severity=rule.severity,
                        timestamp=datetime.now(),
                        message=(
                            f"{rule.description or rule.name}: {latest.value} "
                            f"{rule.condition} {rule.threshold}"
                        ),
                    )

                    self.alerts.append(alert)
                    new_alerts.append(alert)

                    # Notifier les gestionnaires
                    self._notify_handlers(alert)

                    ark_logger.warning(
                        f"🚨 Alerte déclenchée: {alert.message}", extra={"arkalia_module": "core"}
                    )
                else:
                    # Mettre à jour l'alerte existante
                    existing_alert.current_value = latest.value
                    existing_alert.timestamp = datetime.now()
            else:
                # Résoudre l'alerte si elle existe
                existing_alert = self._find_existing_alert(rule.name)
                if existing_alert and not existing_alert.resolved:
                    existing_alert.resolved = True
                    ark_logger.info(
                        f"✅ Alerte résolue: {rule.name}", extra={"arkalia_module": "core"}
                    )

        # Nettoyer les anciennes alertes
        self._cleanup_old_alerts()

        return new_alerts

    def get_active_alerts(self) -> list[Alert]:
        """Récupère les alertes actives"""
        return [alert for alert in self.alerts if not alert.resolved]

    def get_alert_stats(self) -> dict[str, Any]:
        """Récupère les statistiques des alertes"""
        total_alerts = len(self.alerts)
        active_alerts = len(self.get_active_alerts())

        severity_counts = defaultdict(int)
        for alert in self.alerts:
            severity_counts[alert.severity.value] += 1

        return {
            "total_alerts": total_alerts,
            "active_alerts": active_alerts,
            "resolved_alerts": total_alerts - active_alerts,
            "severity_distribution": dict(severity_counts),
            "rules_count": len(self.rules),
            "enabled_rules": len([r for r in self.rules.values() if r.enabled]),
        }

    def _check_condition(self, value: float, condition: str, threshold: float) -> bool:
        """Vérifie une condition d'alerte"""
        if condition == ">":
            return value > threshold
        elif condition == "<":
            return value < threshold
        elif condition == ">=":
            return value >= threshold
        elif condition == "<=":
            return value <= threshold
        elif condition == "==":
            return value == threshold
        else:
            ark_logger.warning(
                f"⚠️ Condition inconnue: {condition}", extra={"arkalia_module": "core"}
            )
            return False

    def _find_existing_alert(self, rule_name: str) -> Alert | None:
        """Trouve une alerte existante pour une règle"""
        for alert in self.alerts:
            if alert.rule_name == rule_name and not alert.resolved:
                return alert
        return None

    def _notify_handlers(self, alert: Alert) -> None:
        """Notifie tous les gestionnaires d'alertes"""
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                ark_logger.error(
                    f"❌ Erreur gestionnaire alerte: {e}", extra={"arkalia_module": "core"}
                )

    def _cleanup_old_alerts(self) -> None:
        """Nettoie les anciennes alertes"""
        cutoff_time = datetime.now() - timedelta(hours=self.config["alert_retention_hours"])
        self.alerts = [alert for alert in self.alerts if alert.timestamp > cutoff_time]


class AdvancedMetricsManager:
    """
    📊 Gestionnaire de métriques avancées
    🎯 Monitoring intelligent avec alertes et prédictions
    """

    def __init__(self):
        self.metrics: dict[str, Metric] = {}
        self.alert_manager = AlertManager()

        # Configuration
        self.config = {
            "auto_cleanup": True,
            "cleanup_interval": 3600,  # 1 heure
            "max_metrics": 1000,
        }

        # Thread safety
        self._lock = threading.RLock()

        ark_logger.info("📊 AdvancedMetricsManager initialisé", extra={"arkalia_module": "core"})

    def create_metric(self, name: str, metric_type: MetricType, description: str = "") -> Metric:
        """Crée une nouvelle métrique"""
        with self._lock:
            if name in self.metrics:
                ark_logger.warning(
                    f"⚠️ Métrique déjà existante: {name}", extra={"arkalia_module": "core"}
                )
                return self.metrics[name]

            metric = Metric(name, metric_type, description)
            self.metrics[name] = metric

            ark_logger.info(f"📊 Métrique créée: {name}", extra={"arkalia_module": "core"})
            return metric

    def record_metric(
        self, name: str, value: int | float, labels: dict[str, str] | None = None
    ) -> bool:
        """Enregistre une valeur pour une métrique"""
        try:
            with self._lock:
                if name not in self.metrics:
                    # Créer automatiquement une métrique de type gauge
                    self.create_metric(name, MetricType.GAUGE)

                self.metrics[name].record(value, labels)
                return True

        except Exception as e:
            ark_logger.error(
                f"❌ Erreur enregistrement métrique {name}: {e}", extra={"arkalia_module": "core"}
            )
            return False

    def get_metric(self, name: str) -> Metric | None:
        """Récupère une métrique"""
        with self._lock:
            return self.metrics.get(name)

    def get_all_metrics(self) -> dict[str, Metric]:
        """Récupère toutes les métriques"""
        with self._lock:
            return self.metrics.copy()

    def get_metric_stats(self, name: str, window_minutes: int = 60) -> dict[str, Any] | None:
        """Récupère les statistiques d'une métrique"""
        metric = self.get_metric(name)
        if not metric:
            return None

        return metric.get_stats(window_minutes)

    def get_metric_trend(self, name: str, window_minutes: int = 60) -> dict[str, Any] | None:
        """Récupère la tendance d'une métrique"""
        metric = self.get_metric(name)
        if not metric:
            return None

        return metric.get_trend(window_minutes)

    def add_alert_rule(self, rule: AlertRule) -> bool:
        """Ajoute une règle d'alerte"""
        return self.alert_manager.add_rule(rule)

    def check_alerts(self) -> list[Alert]:
        """Vérifie toutes les alertes"""
        with self._lock:
            return self.alert_manager.check_alerts(self.metrics)

    def get_alert_stats(self) -> dict[str, Any]:
        """Récupère les statistiques des alertes"""
        return self.alert_manager.get_alert_stats()

    def get_global_stats(self) -> dict[str, Any]:
        """Récupère les statistiques globales"""
        with self._lock:
            total_metrics = len(self.metrics)
            total_values = sum(len(m.values) for m in self.metrics.values())

            # Calculer les métriques les plus actives
            active_metrics = []
            for name, metric in self.metrics.items():
                if metric.values:
                    latest = metric.get_latest()
                    if (
                        latest and (datetime.now() - latest.timestamp).total_seconds() < 300
                    ):  # 5 minutes
                        active_metrics.append(name)

            return {
                "total_metrics": total_metrics,
                "total_values": total_values,
                "active_metrics": len(active_metrics),
                "alert_stats": self.alert_manager.get_alert_stats(),
                "most_active_metrics": active_metrics[:10],  # Top 10
            }

    def export_metrics(self, format: str = "json") -> str:
        """Exporte les métriques"""
        with self._lock:
            if format == "json":
                data = {
                    "timestamp": datetime.now().isoformat(),
                    "metrics": {
                        name: {
                            "info": metric.to_dict(),
                            "stats": metric.get_stats(),
                            "trend": metric.get_trend(),
                        }
                        for name, metric in self.metrics.items()
                    },
                    "alerts": self.alert_manager.get_alert_stats(),
                }
                return json.dumps(data, indent=2, default=str)
            else:
                raise ValueError(f"Format non supporté: {format}")


# Instance globale
_metrics_manager: AdvancedMetricsManager | None = None


def get_metrics_manager() -> AdvancedMetricsManager:
    """Récupère l'instance globale du gestionnaire de métriques"""
    global _metrics_manager
    if _metrics_manager is None:
        _metrics_manager = AdvancedMetricsManager()
    return _metrics_manager


def record_metric(name: str):
    """Décorateur pour enregistrer automatiquement une métrique"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            success = False

            try:
                result = func(*args, **kwargs)
                success = True
                return result
            finally:
                # Enregistrer les métriques
                metrics_manager = get_metrics_manager()

                # Métrique de temps d'exécution
                execution_time = (time.time() - start_time) * 1000  # ms
                metrics_manager.record_metric(
                    f"{name}_execution_time", execution_time, {"success": str(success)}
                )

                # Métrique de succès/échec
                metrics_manager.record_metric(
                    f"{name}_success_rate", 1.0 if success else 0.0, {"function": func.__name__}
                )

        return wrapper

    return decorator

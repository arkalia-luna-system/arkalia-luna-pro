#!/usr/bin/env python3
# 🧠 modules/sandozia/utils/metrics.py
# Utilitaires métriques Sandozia

"""
SandoziaMetrics - Utilitaires métriques pour Sandozia

Collecte et traite les métriques d'intelligence croisée :
- Métriques Prometheus
- Corrélations temporelles
- Agrégations cross-modules
- Export Grafana
"""

import json
import logging
import statistics
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Optional

from core.ark_logger import ark_logger

logger = logging.getLogger(__name__)


@dataclass
class MetricPoint:
    timestamp: datetime
    value: float
    labels: dict[str, str]

    def to_dict(self) -> dict:
        """
        Fonction to_dict.

        Cette fonction fait partie du système Arkalia Luna Pro.
        """
        return {
            "timestamp": self.timestamp.isoformat(),
            "value": self.value,
            "labels": self.labels,
        }


class SandoziaMetrics:
    """
    Collecteur et processeur de métriques Sandozia

    Fonctionnalités :
    - Collecte cross-modules
    - Calculs de corrélation
    - Agrégations temporelles
    - Export formats Grafana/Prometheus
    """

    def __init__(self, retention_hours: int = 24) -> None:
        """
        Fonction __init__.

        Cette fonction fait partie du système Arkalia Luna Pro.
        """
        self.retention_hours = retention_hours
        self.metrics_store: dict[str, list[MetricPoint]] = defaultdict(list)
        self.correlations_cache: dict[str, float] = {}
        logger.info("📊 SandoziaMetrics initialized")

    def add_metric(self, name: str, value: float, labels: dict[str, str] | None = None):
        labels = labels or {}
        timestamp = datetime.now()
        metric_point = MetricPoint(timestamp=timestamp, value=value, labels=labels)
        self.metrics_store[name].append(metric_point)
        # Nettoyer les anciennes métriques
        self._cleanup_old_metrics(name)

    def _cleanup_old_metrics(self, metric_name: str):
        cutoff = datetime.now() - timedelta(hours=self.retention_hours)
        self.metrics_store[metric_name] = [
            point for point in self.metrics_store[metric_name] if point.timestamp > cutoff
        ]

    def get_metric_values(self, name: str, time_window_minutes: int | None = None) -> list[float]:
        if name not in self.metrics_store:
            return []
        points = self.metrics_store[name]
        if time_window_minutes:
            cutoff = datetime.now() - timedelta(minutes=time_window_minutes)
            points = [p for p in points if p.timestamp > cutoff]
        return [p.value for p in points]

    def calculate_correlation(
        self, metric1: str, metric2: str, time_window_minutes: int = 60
    ) -> float | None:
        """Calcule la corrélation entre deux métriques"""
        values1 = self.get_metric_values(metric1, time_window_minutes)
        values2 = self.get_metric_values(metric2, time_window_minutes)
        if len(values1) < 3 or len(values2) < 3 or len(values1) != len(values2):
            return None
        try:
            mean1 = statistics.mean(values1)
            mean2 = statistics.mean(values2)
            numerator = sum(
                (x - mean1) * (y - mean2) for x, y in zip(values1, values2, strict=False)
            )
            sum_sq1 = sum((x - mean1) ** 2 for x in values1)
            sum_sq2 = sum((y - mean2) ** 2 for y in values2)
            denominator = (sum_sq1 * sum_sq2) ** 0.5
            if denominator == 0:
                return 0.0
            correlation = numerator / denominator
            cache_key = f"{metric1}_{metric2}_{time_window_minutes}"
            self.correlations_cache[cache_key] = correlation
            return correlation
        except Exception as e:
            logger.warning(f"⚠️ Correlation calculation failed: {e}")
            return None

    def get_metric_summary(self, name: str) -> dict[str, Any] | None:
        values = self.get_metric_values(name)
        if not values:
            return None
        return {
            "count": len(values),
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "min": min(values),
            "max": max(values),
            "stdev": statistics.stdev(values) if len(values) > 1 else 0.0,
            "latest": values[-1] if values else None,
            "first_timestamp": (
                self.metrics_store[name][0].timestamp.isoformat()
                if self.metrics_store[name]
                else None
            ),
            "last_timestamp": (
                self.metrics_store[name][-1].timestamp.isoformat()
                if self.metrics_store[name]
                else None
            ),
        }

    def export_prometheus_format(self) -> str:
        lines: list[Any] = []
        for metric_name, points in self.metrics_store.items():
            if not points:
                continue
            latest_point = points[-1]
            labels_str = ""
            if latest_point.labels:
                label_pairs = [f'{k}="{v}"' for k, v in latest_point.labels.items()]
                labels_str = "{" + ",".join(label_pairs) + "}"
            line = f"sandozia_{metric_name}{labels_str} {latest_point.value}"
            lines.append(line)
        return "\n".join(lines)

    def export_grafana_json(self) -> dict[str, Any]:
        series: list[Any] = []
        for metric_name, points in self.metrics_store.items():
            if not points:
                continue
            datapoints: list[Any] = []
            for point in points:
                timestamp_ms = int(point.timestamp.timestamp() * 1000)
                datapoints.append([point.value, timestamp_ms])
            series.append({"target": metric_name, "datapoints": datapoints})
        return {
            "series": series,
            "exported_at": datetime.now().isoformat(),
            "retention_hours": self.retention_hours,
        }

    def get_cross_module_health(self) -> dict[str, Any]:
        health_metrics: dict[str, Any] = {}
        modules = ["reflexia", "zeroia", "assistantia"]
        base_metrics = ["confidence_score", "response_time", "success_rate"]
        for module in modules:
            module_health: dict[str, Any] = {}
            for metric in base_metrics:
                metric_key = f"{module}_{metric}"
                summary = self.get_metric_summary(metric_key)
                if summary:
                    if metric == "confidence_score":
                        health_score = summary["mean"]
                    elif metric in ["response_time"]:
                        max_acceptable = 2.0
                        health_score = max(0.0, 1.0 - (summary["mean"] / max_acceptable))
                    elif metric == "success_rate":
                        health_score = summary["mean"]
                    else:
                        health_score = 0.0
                    module_health[metric] = {"score": health_score, "summary": summary}
            if module_health:
                scores = [m["score"] for m in module_health.values()]
                overall_score = statistics.mean(scores) if scores else 0.0
                health_metrics[module] = {
                    "overall_health": overall_score,
                    "metrics": module_health,
                }
        coherence_scores: list[Any] = []
        for module in modules:
            if module in health_metrics:
                coherence_scores.append(health_metrics[module]["overall_health"])
        if len(coherence_scores) >= 2:
            coherence_variance = statistics.variance(coherence_scores)
            coherence_score = max(0.0, 1.0 - coherence_variance)
        else:
            coherence_score = 0.0
        return {
            "timestamp": datetime.now().isoformat(),
            "modules": health_metrics,
            "cross_module_coherence": coherence_score,
            "available_correlations": len(self.correlations_cache),
            "total_metrics": len(self.metrics_store),
        }

    def get_all_metrics(self) -> dict[str, Any]:
        return {
            "metrics_count": len(self.metrics_store),
            "metrics_names": list(self.metrics_store.keys()),
            "retention_hours": self.retention_hours,
            "correlations_cached": len(self.correlations_cache),
            "oldest_metric": min(
                (points[0].timestamp for points in self.metrics_store.values() if points),
                default=datetime.now(),
            ).isoformat(),
            "latest_metric": max(
                (points[-1].timestamp for points in self.metrics_store.values() if points),
                default=datetime.now(),
            ).isoformat(),
        }


# Fonctions helper
def create_sandozia_metrics() -> SandoziaMetrics:
    return SandoziaMetrics(retention_hours=24)


def demo_metrics():
    import random
    import time

    metrics = create_sandozia_metrics()

    ark_logger.info("📊 Generating demo metrics...", extra={"arkalia_module": "utils"})

    # Générer des métriques synthétiques
    for _i in range(100):
        # Metrics Reflexia (démo uniquement)
        metrics.add_metric(
            "reflexia_confidence_score",
            random.uniform(0.7, 0.95),  # nosec B311
            {"module": "reflexia", "type": "confidence"},
        )

        # Metrics ZeroIA (démo uniquement)
        metrics.add_metric(
            "zeroia_confidence_score",
            random.uniform(0.6, 0.9),  # nosec B311
            {"module": "zeroia", "type": "confidence"},
        )

        # Response times (démo uniquement)
        metrics.add_metric(
            "reflexia_response_time",
            random.uniform(0.1, 0.8),  # nosec B311
            {"module": "reflexia", "type": "performance"},
        )

        time.sleep(0.01)

    # Analyser les résultats
    ark_logger.info("\n🔍 Analysis results:", extra={"arkalia_module": "utils"})

    # Corrélation entre confiances
    correlation = metrics.calculate_correlation(
        "reflexia_confidence_score", "zeroia_confidence_score"
    )
    if correlation:
        ark_logger.info(
            f"Corrélation confiance Reflexia-ZeroIA: {correlation:.3f}", extra={"arkalia_module": "utils"}
        )

    # Santé cross-modules
    health = metrics.get_cross_module_health()
    ark_logger.info(
        f"Cohérence inter-modules: {health['cross_module_coherence']:.3f}",
        extra={"arkalia_module": "utils"},
    )

    # Export Prometheus
    prometheus_data = metrics.export_prometheus_format()
    ark_logger.info(
        f"\n📤 Prometheus export ({len(prometheus_data.split())} metrics):",
        extra={"arkalia_module": "utils"},
    )
    ark_logger.info(
        prometheus_data[:200] + "..." if len(prometheus_data) > 200 else prometheus_data,
        extra={"arkalia_module": "utils"},
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    demo_metrics()


class MetricsCollector:
    """
    Collecteur de métriques Sandozia

    Collecte et analyse :
    - Métriques de performance
    - Métriques cognitives
    - Métriques de cohérence
    - Tendances temporelles
    """

    def __init__(self, config: dict | None = None) -> None:
        """
        Fonction __init__.

        Cette fonction fait partie du système Arkalia Luna Pro.
        """
        self.config = config or {
            "collection_interval": 60,  # secondes
            "retention_days": 7,
            "alert_thresholds": {
                "cpu_usage": 80.0,
                "memory_usage": 85.0,
                "error_rate": 5.0,
            },
        }
        self.metrics_buffer: dict[str, list[dict]] = {}
        self.alerts: list[dict] = []
        logger.info("📊 MetricsCollector initialized")

    def collect_module_metrics(self, module_name: str, metrics: dict) -> None:
        """
        Collecte les métriques d'un module

        Args:
            module_name: Nom du module
            metrics: Métriques du module
        """
        timestamp = datetime.now()
        metric_entry = {
            "timestamp": timestamp,
            "module": module_name,
            "metrics": metrics,
        }

        if module_name not in self.metrics_buffer:
            self.metrics_buffer[module_name] = []

        self.metrics_buffer[module_name].append(metric_entry)

        # Limiter la taille du buffer
        max_entries = 1000
        if len(self.metrics_buffer[module_name]) > max_entries:
            self.metrics_buffer[module_name] = self.metrics_buffer[module_name][-max_entries:]

        # Vérifier les alertes
        self._check_alerts(module_name, metrics, timestamp)

    def _check_alerts(self, module_name: str, metrics: dict, timestamp: datetime) -> None:
        """
        Vérifie les alertes basées sur les métriques

        Args:
            module_name: Nom du module
            metrics: Métriques du module
            timestamp: Timestamp de la collecte
        """
        thresholds = self.config["alert_thresholds"]

        for metric_name, threshold in thresholds.items():
            if metric_name in metrics:
                value = metrics[metric_name]
                if isinstance(value, int | float) and value > threshold:
                    alert = {
                        "timestamp": timestamp,
                        "module": module_name,
                        "metric": metric_name,
                        "value": value,
                        "threshold": threshold,
                        "severity": "warning",
                    }
                    self.alerts.append(alert)
                    logger.warning(f"⚠️ Alert: {module_name}.{metric_name} = {value} > {threshold}")

    def get_module_metrics(self, module_name: str, hours: int = 24) -> list[dict]:
        """
        Récupère les métriques d'un module

        Args:
            module_name: Nom du module
            hours: Nombre d'heures à récupérer

        Returns:
            list[dict]: Métriques du module
        """
        if module_name not in self.metrics_buffer:
            return []

        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            entry for entry in self.metrics_buffer[module_name] if entry["timestamp"] > cutoff_time
        ]

    def get_system_summary(self) -> dict[str, Any]:
        """
        Récupère un résumé des métriques système

        Returns:
            dict: Résumé des métriques
        """
        summary = {
            "modules": list(self.metrics_buffer.keys()),
            "total_metrics": sum(len(entries) for entries in self.metrics_buffer.values()),
            "alerts_count": len(self.alerts),
            "timestamp": datetime.now().isoformat(),
        }

        # Calculer les moyennes par module
        module_averages = {}
        for module_name, entries in self.metrics_buffer.items():
            if not entries:
                continue

            # Calculer les moyennes des métriques numériques
            numeric_metrics: dict[str, list[float]] = {}
            for entry in entries:
                for metric_name, value in entry["metrics"].items():
                    if isinstance(value, int | float):
                        if metric_name not in numeric_metrics:
                            numeric_metrics[metric_name] = []
                        numeric_metrics[metric_name].append(value)

            averages = {}
            for metric_name, values in numeric_metrics.items():
                if values:
                    averages[metric_name] = sum(values) / len(values)

            module_averages[module_name] = averages

        summary["module_averages"] = module_averages
        return summary

    def get_alerts(self, hours: int = 24) -> list[dict]:
        """
        Récupère les alertes récentes

        Args:
            hours: Nombre d'heures à récupérer

        Returns:
            list[dict]: Alertes récentes
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [alert for alert in self.alerts if alert["timestamp"] > cutoff_time]

    def clear_old_data(self, days: int | None = None) -> None:
        """
        Nettoie les anciennes données

        Args:
            days: Nombre de jours à conserver
        """
        if days is None:
            days = self.config["retention_days"]

        cutoff_time = datetime.now() - timedelta(days=days)

        # Nettoyer les métriques
        for module_name in self.metrics_buffer:
            self.metrics_buffer[module_name] = [
                entry
                for entry in self.metrics_buffer[module_name]
                if entry["timestamp"] > cutoff_time
            ]

        # Nettoyer les alertes
        self.alerts = [alert for alert in self.alerts if alert["timestamp"] > cutoff_time]

        logger.info(f"🧹 Cleaned data older than {days} days")

    def export_metrics(self, format_type: str = "json") -> str:
        """
        Exporte les métriques

        Args:
            format_type: Type de format (json, csv)

        Returns:
            str: Métriques exportées
        """
        if format_type == "json":
            return json.dumps(self.metrics_buffer, indent=2, default=str)
        elif format_type == "csv":
            # Format CSV simplifié
            csv_lines = ["timestamp,module,metric,value"]
            for module_name, entries in self.metrics_buffer.items():
                for entry in entries:
                    for metric_name, value in entry["metrics"].items():
                        csv_lines.append(
                            f"{entry['timestamp']},{module_name},{metric_name},{value}"
                        )
            return "\n".join(csv_lines)
        else:
            raise ValueError(f"Format non supporté: {format_type}")

    def get_metrics_trends(
        self, module_name: str, metric_name: str, hours: int = 24
    ) -> dict[str, Any]:
        """
        Calcule les tendances d'une métrique

        Args:
            module_name: Nom du module
            metric_name: Nom de la métrique
            hours: Nombre d'heures à analyser

        Returns:
            dict: Tendances de la métrique
        """
        metrics = self.get_module_metrics(module_name, hours)
        if not metrics:
            return {"trend": "no_data", "values": []}

        values = []
        for entry in metrics:
            if metric_name in entry["metrics"]:
                value = entry["metrics"][metric_name]
                if isinstance(value, int | float):
                    values.append(value)

        if not values:
            return {"trend": "no_numeric_data", "values": []}

        # Calculer la tendance
        if len(values) >= 2:
            trend = "increasing" if values[-1] > values[0] else "decreasing"
            if abs(values[-1] - values[0]) < 0.01:
                trend = "stable"
        else:
            trend = "insufficient_data"

        return {
            "trend": trend,
            "values": values,
            "min": min(values),
            "max": max(values),
            "average": sum(values) / len(values),
        }

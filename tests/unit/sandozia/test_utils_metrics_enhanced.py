#!/usr/bin/env python3
# 📊 tests/unit/sandozia/test_utils_metrics_enhanced.py
# Tests pour modules/sandozia/utils/metrics.py (imports corrigés)

import importlib.util
from datetime import datetime
from pathlib import Path

# Ajout dynamique du module sandozia.utils.metrics
metrics_path = Path(__file__).resolve().parents[3] / "modules" / "sandozia" / "utils" / "metrics.py"
spec = importlib.util.spec_from_file_location("sandozia.utils.metrics", str(metrics_path))
if spec is not None and spec.loader is not None:
    metrics = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(metrics)
    SandoziaMetrics = metrics.SandoziaMetrics
    MetricPoint = metrics.MetricPoint
    create_sandozia_metrics = metrics.create_sandozia_metrics
    demo_metrics = metrics.demo_metrics
else:
    raise ImportError(
        f"Impossible d'importer le module sandozia.utils.metrics depuis {metrics_path}"
    )


def test_metric_point_creation() -> None:
    timestamp = datetime.now()
    labels = {"module": "test", "version": "1.0"}
    point = MetricPoint(timestamp=timestamp, value=42.5, labels=labels)

    assert point.timestamp == timestamp
    assert point.value == 42.5
    assert point.labels == labels


def test_metric_point_to_dict() -> None:
    timestamp = datetime.now()
    labels = {"module": "test"}
    point = MetricPoint(timestamp=timestamp, value=100.0, labels=labels)

    data = point.to_dict()
    assert data["timestamp"] == timestamp.isoformat()
    assert data["value"] == 100.0
    assert data["labels"] == labels


def test_sandozia_metrics_initialization() -> None:
    metrics = SandoziaMetrics(retention_hours=48)
    assert metrics.retention_hours == 48
    assert len(metrics.metrics_store) == 0
    assert len(metrics.correlations_cache) == 0


def test_add_metric() -> None:
    metrics = SandoziaMetrics()
    metrics.add_metric("cpu_usage", 75.5, {"module": "zeroia"})

    assert "cpu_usage" in metrics.metrics_store
    assert len(metrics.metrics_store["cpu_usage"]) == 1
    assert metrics.metrics_store["cpu_usage"][0].value == 75.5


def test_get_metric_values() -> None:
    metrics = SandoziaMetrics()
    metrics.add_metric("test_metric", 10.0)
    metrics.add_metric("test_metric", 20.0)
    metrics.add_metric("test_metric", 30.0)

    values = metrics.get_metric_values("test_metric")
    assert values == [10.0, 20.0, 30.0]


def test_get_metric_summary() -> None:
    metrics = SandoziaMetrics()
    metrics.add_metric("test_metric", 10.0)
    metrics.add_metric("test_metric", 20.0)
    metrics.add_metric("test_metric", 30.0)

    summary = metrics.get_metric_summary("test_metric")
    assert summary is not None
    assert summary["count"] == 3
    assert summary["mean"] == 20.0
    assert summary["min"] == 10.0
    assert summary["max"] == 30.0


def test_export_prometheus_format() -> None:
    metrics = SandoziaMetrics()
    metrics.add_metric("cpu_usage", 75.5, {"module": "zeroia"})

    prometheus_data = metrics.export_prometheus_format()
    assert "sandozia_cpu_usage" in prometheus_data
    assert "75.5" in prometheus_data


def test_export_grafana_json() -> None:
    metrics = SandoziaMetrics()
    metrics.add_metric("cpu_usage", 75.5)

    grafana_data = metrics.export_grafana_json()
    assert "series" in grafana_data
    assert "exported_at" in grafana_data
    assert "retention_hours" in grafana_data


def test_create_sandozia_metrics() -> None:
    metrics = create_sandozia_metrics()
    assert isinstance(metrics, SandoziaMetrics)


def test_demo_metrics() -> None:
    # Test que demo_metrics() s'exécute sans erreur
    demo_metrics()
    assert True  # Si on arrive ici, pas d'exception

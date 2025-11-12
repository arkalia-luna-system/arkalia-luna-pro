#!/usr/bin/env python3
# 🧠 tests/unit/sandozia/test_analyzer_behavior_enhanced.py
# Tests pour modules/sandozia/analyzer/behavior.py (imports corrigés)

import importlib.util
import sys
from datetime import datetime
from pathlib import Path

import pytest

# Ajout dynamique du module sandozia.analyzer.behavior
behavior_path = (
    Path(__file__).resolve().parents[3] / "modules" / "sandozia" / "analyzer" / "behavior.py"
)
spec = importlib.util.spec_from_file_location("sandozia.analyzer.behavior", str(behavior_path))
if spec is not None and spec.loader is not None:
    behavior = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(behavior)
    BehaviorAnalyzer = behavior.BehaviorAnalyzer
    BehaviorPattern = behavior.BehaviorPattern
else:
    raise ImportError(
        f"Impossible d'importer le module sandozia.analyzer.behavior depuis {behavior_path}"
    )


def test_behavior_pattern_creation() -> None:
    timestamp = datetime.now()
    pattern = BehaviorPattern(
        pattern_type="test_pattern",
        severity="medium",
        description="Test pattern description",
        affected_modules=["zeroia", "reflexia"],
        confidence=0.8,
        first_detected=timestamp,
        last_detected=timestamp,
        occurrences=5,
        metadata={"test": "data"},
    )

    assert pattern.pattern_type == "test_pattern"
    assert pattern.severity == "medium"
    assert pattern.confidence == 0.8
    assert len(pattern.affected_modules) == 2


def test_behavior_pattern_to_dict() -> None:
    timestamp = datetime.now()
    pattern = BehaviorPattern(
        pattern_type="test_pattern",
        severity="high",
        description="Test description",
        affected_modules=["zeroia"],
        confidence=0.9,
        first_detected=timestamp,
        last_detected=timestamp,
        occurrences=3,
        metadata={"key": "value"},
    )

    data = pattern.to_dict()
    assert data["pattern_type"] == "test_pattern"
    assert data["severity"] == "high"
    assert data["confidence"] == 0.9
    assert data["occurrences"] == 3


def test_behavior_analyzer_initialization() -> None:
    analyzer = BehaviorAnalyzer()
    assert analyzer.config is not None
    assert "window_size_minutes" in analyzer.config
    assert "anomaly_threshold" in analyzer.config
    assert len(analyzer.pattern_history) == 0


def test_behavior_analyzer_custom_config() -> None:
    custom_config = {
        "window_size_minutes": 120,
        "anomaly_threshold": 3.0,
        "pattern_min_occurrences": 5,
        "confidence_threshold": 0.8,
        "max_pattern_history": 1000,
    }
    analyzer = BehaviorAnalyzer(custom_config)
    assert analyzer.config == custom_config


def test_add_metric_sample() -> None:
    analyzer = BehaviorAnalyzer()
    timestamp = datetime.now()

    analyzer.add_metric_sample("zeroia", "cpu_usage", 75.5, timestamp)

    key = "zeroia.cpu_usage"
    assert key in analyzer.metrics_buffer
    assert len(analyzer.metrics_buffer[key]) == 1
    assert analyzer.metrics_buffer[key][0]["value"] == 75.5


def test_add_decision_event() -> None:
    analyzer = BehaviorAnalyzer()
    decision_data = {"action": "monitor", "confidence": 0.8}

    analyzer.add_decision_event("zeroia", decision_data)

    assert len(analyzer.decision_history) == 1
    event = analyzer.decision_history[0]
    assert event["module"] == "zeroia"
    assert event["data"] == decision_data


def test_detect_statistical_anomalies_empty() -> None:
    analyzer = BehaviorAnalyzer()
    anomalies = analyzer.detect_statistical_anomalies()
    assert len(anomalies) == 0


def test_detect_performance_regression_empty() -> None:
    analyzer = BehaviorAnalyzer()
    regressions = analyzer.detect_performance_regression()
    assert len(regressions) == 0


def test_analyze_behavior() -> None:
    analyzer = BehaviorAnalyzer()
    analysis = analyzer.analyze_behavior()

    assert "patterns_detected" in analysis
    assert "behavioral_health_score" in analysis
    assert "patterns_by_severity" in analysis
    assert "patterns_by_type" in analysis
    assert "affected_modules" in analysis
    assert "patterns_detail" in analysis
    assert "metrics_monitored" in analysis
    assert "decisions_analyzed" in analysis
    assert "baseline_stats_available" in analysis
    assert "timestamp" in analysis


def test_get_pattern_history() -> None:
    analyzer = BehaviorAnalyzer()
    history = analyzer.get_pattern_history()
    assert isinstance(history, list)


def test_get_metrics_summary() -> None:
    analyzer = BehaviorAnalyzer()
    summary = analyzer.get_metrics_summary()
    assert isinstance(summary, dict)

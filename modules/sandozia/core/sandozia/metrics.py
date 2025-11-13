"""
SandoziaMetrics - Métriques de performance Sandozia
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class SandoziaMetrics:
    """Métriques de performance Sandozia"""

    timestamp: datetime
    coherence_score: float
    cross_validation_passed: int
    anomalies_detected: int
    reasoning_alignment: float
    modules_active: list[str]
    total_correlations: int
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    response_time: float = 0.0
    throughput: float = 0.0
    error_rate: float = 0.0

    def to_dict(self) -> dict:
        """
        Fonction to_dict.

        Cette fonction fait partie du système Arkalia Luna Pro.
        """
        return {
            "timestamp": self.timestamp.isoformat(),
            "coherence_score": self.coherence_score,
            "cross_validation_passed": self.cross_validation_passed,
            "anomalies_detected": self.anomalies_detected,
            "reasoning_alignment": self.reasoning_alignment,
            "modules_active": self.modules_active,
            "total_correlations": self.total_correlations,
            "cpu_usage": self.cpu_usage,
            "memory_usage": self.memory_usage,
            "response_time": self.response_time,
            "throughput": self.throughput,
            "error_rate": self.error_rate,
        }

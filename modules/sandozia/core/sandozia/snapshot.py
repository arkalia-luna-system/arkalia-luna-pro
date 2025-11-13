"""
IntelligenceSnapshot - Snapshot de l'intelligence actuelle
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class IntelligenceSnapshot:
    """Snapshot de l'intelligence actuelle"""

    reflexia_state: dict
    zeroia_state: dict
    assistant_state: dict
    helloria_state: dict
    nyxalia_state: dict
    taskia_state: dict
    cognitive_state: dict
    coherence_analysis: dict
    behavioral_patterns: list[dict]
    recommendations: list[str]
    cognitive_level: int = 0
    decision_confidence: float = 0.0
    learning_progress: float = 0.0
    adaptation_rate: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        """
        Fonction to_dict.

        Cette fonction fait partie du système Arkalia Luna Pro.
        """
        return {
            "reflexia_state": self.reflexia_state,
            "zeroia_state": self.zeroia_state,
            "assistant_state": self.assistant_state,
            "helloria_state": self.helloria_state,
            "nyxalia_state": self.nyxalia_state,
            "taskia_state": self.taskia_state,
            "cognitive_state": self.cognitive_state,
            "coherence_analysis": self.coherence_analysis,
            "behavioral_patterns": self.behavioral_patterns,
            "recommendations": self.recommendations,
            "cognitive_level": self.cognitive_level,
            "decision_confidence": self.decision_confidence,
            "learning_progress": self.learning_progress,
            "adaptation_rate": self.adaptation_rate,
            "timestamp": self.timestamp.isoformat(),
        }

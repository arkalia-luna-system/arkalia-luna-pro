from typing import Any


def process_stimulus_payload(stimulus: dict[str, Any]) -> dict[str, Any]:
    """Pure helper to keep CognitiveReactor.process_stimulus focused."""
    result: dict[str, Any] = {"processed": True}
    severity = stimulus.get("severity", "low")
    result["severity"] = severity

    if stimulus.get("type") == "system_alert":
        result["reaction"] = "stimulus_processed_low"
        result["cognitive_score"] = 0.7
        return result

    if severity == "high":
        result["reaction"] = "stimulus_processed_high"
        result["immediate_action"] = "emergency_protocol"
        return result

    if stimulus.get("type") == "zeroia_decision":
        result["reaction"] = "zeroia_decision_processed"
        result["zeroia_integration"] = True
        return result

    if stimulus.get("source") == "reflexia":
        result["reaction"] = "reflexia_processed"
        return result

    if "type" not in stimulus or "source" not in stimulus:
        result["warning"] = "incomplete_stimulus"
        return result

    result["reaction"] = f"stimulus_processed_{severity}"
    return result

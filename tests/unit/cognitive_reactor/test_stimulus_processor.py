from modules.cognitive_reactor.stimulus_processor import process_stimulus_payload


def test_process_stimulus_payload_high_severity() -> None:
    result = process_stimulus_payload({"type": "alert", "source": "monitor", "severity": "high"})
    assert result["processed"] is True
    assert result["immediate_action"] == "emergency_protocol"


def test_process_stimulus_payload_reflexia_path() -> None:
    result = process_stimulus_payload({"type": "notice", "source": "reflexia"})
    assert result["reaction"] == "reflexia_processed"

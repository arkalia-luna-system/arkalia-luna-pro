from modules.zeroia.reason_loop_enhanced import decide_protected


def test_decide_emergency_from_reflexia() -> None:
    ctx = {
        "status": {"cpu": 51.1, "severity": "critical"},
        "reflexia": {"last_snapshot": "🛑 surcharge CPU"},
    }
    # decide_protected retourne (decision, confidence)
    decision, confidence = decide_protected(ctx)
    # Avec CPU 51.1 et severity critical, la décision devrait être emergency_shutdown
    assert decision == "emergency_shutdown"
    assert confidence > 0.0

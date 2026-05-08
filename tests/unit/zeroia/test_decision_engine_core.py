from modules.zeroia.decision_engine import DecisionEngine


def test_should_process_decision_blocks_recent_repetition() -> None:
    engine = DecisionEngine()
    engine.min_decision_interval = 60

    first = engine.should_process_decision("normal")
    second = engine.should_process_decision("normal")

    assert first is True
    assert second is False


def test_decide_protected_returns_error_for_invalid_context() -> None:
    engine = DecisionEngine()

    decision, score = engine.decide_protected(  # pyright: ignore[reportUnknownMemberType]
        {"status": {"cpu": "bad", "ram": 50}}
    )

    assert decision == "error"
    assert score == 0.0


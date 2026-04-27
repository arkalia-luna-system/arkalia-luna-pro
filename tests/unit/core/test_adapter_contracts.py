from modules.core.adapters.sandozia_adapter import SandoziaAdapter
from modules.core.adapters.zeroia_adapter import ZeroIAAdapter


def test_zeroia_adapter_contract_exposes_decision_fields() -> None:
    adapter = ZeroIAAdapter()
    assert adapter.initialize() is True

    result = adapter.process({"context": "contract_test"})
    assert result["status"] == "success"
    assert "decision" in result
    assert "confidence" in result


def test_sandozia_adapter_health_and_core_processing_contract() -> None:
    adapter = SandoziaAdapter()
    assert adapter.initialize() is True

    health = adapter.health_check()
    assert health["module"] == "sandozia"
    assert health["status"] in {"ok", "degraded", "error"}

    processed = adapter.process_core({"payload": "contract_test"})
    assert processed["status"] in {"success", "error"}

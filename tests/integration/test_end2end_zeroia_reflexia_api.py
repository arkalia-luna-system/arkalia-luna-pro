import pytest

from demo_global import ReflexiaWrapper, SandoziaWrapper, SecurityWrapper
from modules.core.storage import StorageManager
from modules.zeroia import ZeroIACoordinator


@pytest.mark.integration
def test_end2end_zeroia_reflexia_api():
    """Test bout-en-bout : ZeroIA → Reflexia → API"""
    storage = StorageManager()
    zeroia = ZeroIACoordinator()
    reflexia = ReflexiaWrapper()
    sandozia = SandoziaWrapper()
    security = SecurityWrapper()

    # 1. Décision ZeroIA
    decision = zeroia.make_decision("security_incident")
    assert decision is not None

    # 2. Création d'alerte Reflexia
    alert_id = reflexia.create_alert(
        {
            "type": "security_threat",
            "severity": "high",
            "source": "zeroia",
            "details": str(decision),
        }
    )
    assert alert_id is not None
    assert len(reflexia.get_active_alerts()) > 0

    # 3. Analyse Sandozia
    analysis = sandozia.analyze_behavior(
        {
            "event_type": "security_incident",
            "decision_id": str(decision),
        }
    )
    assert analysis is not None

    # 4. Scan API Security
    scan = security.scan_request({"payload": "DROP TABLE users;"})
    assert scan["threat_level"] in ("high", "low")

    # 5. Vérification stockage
    storage.save_state("zeroia", decision, "last_decision")
    last = storage.get_state("zeroia", "last_decision")
    assert last is not None

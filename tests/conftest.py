"""Configuration globale des tests pour Arkalia-LUNA"""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# Ajouter le répertoire racine au path Python
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


# Mock des modules manquants
class MockZeroIACore:
    """Mock pour ZeroIACore"""

    def __init__(self) -> None:
        self.version = "2.8.0"
        self.status = "active"

    def get_status(self) -> dict[str, str]:
        return {"status": "active", "version": self.version}


class MockSandoziaCore:
    """Mock pour SandoziaCore"""

    def __init__(self) -> None:
        self.version = "2.8.0"
        self.status = "active"

    def get_status(self) -> dict[str, str]:
        return {"status": "active", "version": self.version}


# Mock des modules qui n'existent pas
sys.modules["modules.zeroia.reason_loop"] = MagicMock()
sys.modules["modules.sandozia.core.cognitive_reactor"] = MagicMock()


# Configuration pytest
def pytest_configure(config: pytest.Config) -> None:
    """Configuration pytest"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "performance: marks tests as performance tests")
    config.addinivalue_line("markers", "security: marks tests as security tests")
    config.addinivalue_line("markers", "chaos: marks tests as chaos tests")


@pytest.fixture(scope="session")
def mock_modules() -> dict[str, MockZeroIACore | MockSandoziaCore]:
    """Fixture pour mocker les modules manquants"""
    return {
        "zeroia_core": MockZeroIACore(),
        "sandozia_core": MockSandoziaCore(),
    }

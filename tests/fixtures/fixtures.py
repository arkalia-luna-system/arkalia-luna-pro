# 📄 tests/common/fixtures.py
# Fixtures partagées pour tous les tests

from collections.abc import Generator
from pathlib import Path

import pytest

from tests.fixtures.__test_helpers import ensure_test_toml, ensure_zeroia_state_file


@pytest.fixture(scope="session")
def test_data_dir() -> Path:
    """Répertoire temporaire pour les données de test."""
    return Path("tests/data")


@pytest.fixture(scope="session")
def mock_config() -> dict:
    """Configuration de test standard."""
    return {"test_mode": True, "debug": True, "timeout": 5}


@pytest.fixture(autouse=True)
def setup_test_environment() -> None:
    """Setup automatique de l'environnement de test."""
    ensure_test_toml()
    ensure_zeroia_state_file()


@pytest.fixture
def clean_state_files() -> Generator[None, None, None]:
    """Nettoie les fichiers d'état après les tests."""
    yield
    # Cleanup après les tests
    state_files = [
        "state/zeroia_state.toml",
        "state/reflexia_state.toml",
    ]
    for file_path in state_files:
        if Path(file_path).exists():
            Path(file_path).write_text("")

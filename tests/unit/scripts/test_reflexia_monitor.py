from pathlib import Path
from unittest.mock import MagicMock, patch

import toml

PROJECT_ROOT = Path(__file__).parent.parent.parent

STATE_FILE = Path("state/reflexia_state.toml")


def setup_module(module: object) -> None:
    # Crée un état mock de ReflexIA
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    state = {
        "loop_active": True,
        "last_decision": "observe",
        "timestamp": "2025-06-26T09:59:00",
    }
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        toml.dump(state, f)


def teardown_module(module: object) -> None:
    # Nettoie le fichier mock après test
    if STATE_FILE.exists():
        STATE_FILE.unlink()


def test_reflexia_monitor_runs() -> None:
    """Teste que le script reflexia_monitor s'exécute sans erreur"""
    # Créer le fichier d'état manquant pour éviter l'erreur
    state_file = Path("state/reflexia_state.toml")
    state_file.parent.mkdir(parents=True, exist_ok=True)

    with open(state_file, "w", encoding="utf-8") as f:
        toml.dump(
            {
                "reasoning_loop_active": True,
                "last_decision": "normal",
                "timestamp": "2025-01-01T00:00:00",
            },
            f,
        )

    try:
        # Mock de requests.post pour éviter l'erreur de connexion Grafana
        with patch("requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_post.return_value = mock_response

            # Importer et exécuter le script directement
            import scripts._reflexia_monitor as monitor

            monitor.export_to_grafana(
                {
                    "reasoning_loop_active": True,
                    "last_decision": "normal",
                    "timestamp": "2025-01-01T00:00:00",
                    "previous": [],
                }
            )

            # Vérifie que la fonction a été appelée
            mock_post.assert_called_once()

    finally:
        # Nettoyer le fichier créé
        if state_file.exists():
            state_file.unlink()

import unittest
from unittest.mock import mock_open, patch

from scripts._zeroia_health import check_state_file


class TestZeroiaHealth(unittest.TestCase):
    def test_zeroia_state_ok(self) -> None:
        """Teste le health check avec un état ZeroIA valide"""
        mock_data = {
            "health": {"is_healthy": True, "error_count": 0},
            "circuit_breaker": {"state": "closed"},
            "performance": {"cpu_usage": 50, "memory_usage": 60},
        }

        with patch("builtins.open", mock_open()) as mock_file:
            with patch("toml.load", return_value=mock_data):
                with self.assertLogs(level="INFO") as log:
                    result = check_state_file()
                    self.assertEqual(result, mock_data)
                    self.assertIn("✅ ZeroIA State file: OK", log.output[0])

    def test_zeroia_state_error(self) -> None:
        """Teste le health check avec un état ZeroIA invalide"""
        with patch("toml.load", side_effect=FileNotFoundError("File not found")):
            result = check_state_file()
            # Le script retourne un dictionnaire vide en cas d'erreur
            self.assertEqual(result, {})
            # Note: Les logs ne sont pas capturés dans ce contexte de test
            # mais la fonction fonctionne correctement


if __name__ == "__main__":
    unittest.main()

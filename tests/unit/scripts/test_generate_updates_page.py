import subprocess
import unittest
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

from scripts._generate_updates_page import main as run


class TestGenerateUpdatesPage(unittest.TestCase):
    @patch("subprocess.run")
    def test_run_success(self, mock_subprocess_run) -> None:
        # Mock the subprocess.run to simulate git log output
        mock_result = MagicMock()
        mock_result.stdout = "abc123 - Fix bug (2023-10-01)\n"
        mock_subprocess_run.return_value = mock_result

        # Run the function
        run()

        # Check that the file was created with the expected content
        output_file = Path("docs/releases/dernieres_updates.md")
        self.assertTrue(output_file.exists())
        with output_file.open("r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("# 🔄 Dernières mises à jour", content)
            self.assertIn("abc123", content)

    def test_run_failure(self) -> None:
        """Teste la gestion d'erreur du script de génération des updates"""
        with patch("subprocess.run") as mock_run:
            # Mock le résultat avec les attributs nécessaires
            mock_result = MagicMock()
            mock_result.returncode = 1
            mock_result.stderr = "Command 'git log' returned non-zero exit status 1."
            mock_result.stdout = "Mocked output"
            mock_run.return_value = mock_result

            # Mock de l'écriture de fichier pour éviter l'erreur
            with patch("builtins.open", mock_open()) as mock_file:
                from scripts._generate_updates_page import main

                main()

                # Vérifie que le script s'exécute sans erreur
                mock_run.assert_called()


if __name__ == "__main__":
    unittest.main()

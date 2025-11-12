import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent


def test_pre_push_zeroia_check_executes_cleanly():
    """Teste que le script pre-push ZeroIA s'exécute sans erreur"""
    script_path = Path("scripts/pre_push_zeroia_check.py")
    assert script_path.exists(), f"Script introuvable : {script_path}"
    result = subprocess.run([sys.executable, str(script_path)], capture_output=True, text=True)
    assert (
        result.returncode == 0
    ), f"Script a échoué avec code {result.returncode}\nstdout: {result.stdout}\nstderr: {result.stderr}"

    # Vérifie que la sortie contient les messages attendus
    output = result.stdout
    assert "✅ Fichier TOML valide" in output
    assert "🛡️ Tous les contrôles ZeroIA sont OK" in output

# 📄 tests/unit/test_helpers.py

import shutil
from pathlib import Path


def ensure_test_toml() -> None:
    """
    Crée un fichier TOML de test minimal pour éviter les erreurs liées
    aux fichiers manquants ou vides dans les tests ZeroIA.
    """
    path = Path("modules/zeroia/state/zeroia_state.toml")
    if not path.exists() or path.read_text().strip() == "":
        path.write_text(
            """
[status]
active = true
confidence = 0.9

[decision]
goal = "observe"
context = "reflexia"
            """.strip()
        )


def ensure_zeroia_state_file() -> None:
    path = Path("modules/zeroia/state/zeroia_state.toml")
    if not path.exists() or path.read_text().strip() == "":
        path.write_text(
            """
[status]
active = true
confidence = 0.93

[decision]
goal = "observe"
context = "reflexia"
""".strip()
        )


def restore_snapshot_if_missing(snapshot_name: str) -> None:
    """
    Restaure un snapshot JSON manquant depuis l'archive vers state/sandozia/.
    """
    src = Path("archive/json_reports/state/sandozia") / snapshot_name
    dst = Path("state/sandozia") / snapshot_name
    if not dst.exists() and src.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(src, dst)
        print(f"[pytest] Snapshot restauré : {snapshot_name}")

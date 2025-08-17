#!/usr/bin/env python3
from pathlib import Path

from core.ark_logger import ark_logger

ROOT = Path(__file__).resolve().parent.parent
MODULES = ROOT / "modules"
ENV_FILE = ROOT / ".env"


def ensure_init_py() -> None:
    init_path = MODULES / "__init__.py"
    if not init_path.exists():
        init_path.touch()
        ark_logger.info(f"✅ Créé : {init_path}", extra={"module": "scripts"})
    else:
        ark_logger.info(f"✔️ Déjà présent : {init_path}", extra={"module": "scripts"})


def ensure_env_py_path() -> None:
    if ENV_FILE.exists():
        content = ENV_FILE.read_text()
        if "PYTHONPATH" in content:
            ark_logger.info("✔️ PYTHONPATH déjà présent dans .env", extra={"module": "scripts"})
            return
    with open(ENV_FILE, "a") as f:
        f.write("\nPYTHONPATH=./modules\n")
    ark_logger.info(f"✅ PYTHONPATH ajouté à {ENV_FILE}", extra={"module": "scripts"})


def main() -> None:
    ark_logger.info("🔧 Patch Pyright / Cursor en cours…", extra={"module": "scripts"})
    ensure_init_py()
    ensure_env_py_path()
    ark_logger.info(
        "✅ Terminé. Recharge Cursor (⇧⌘P > Reload Window)", extra={"module": "scripts"}
    )


if __name__ == "__main__":
    main()

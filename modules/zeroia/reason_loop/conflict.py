"""
Conflict - Détection de conflit IA
"""

import textwrap
from datetime import datetime
from pathlib import Path

from core.ark_logger import ark_logger

DEFAULT_CONTRADICTION_LOG = Path("logs/zeroia_contradictions.log")


def ensure_parent_dir(path: Path) -> None:
    """Assure que le répertoire parent existe"""
    target = path.parent if path.suffix else path
    target.mkdir(parents=True, exist_ok=True)


def check_for_ia_conflict_enhanced(
    reflexia_decision: str,
    zeroia_decision: str,
    log_path: Path,
) -> bool:
    """Détection de conflit IA avec gestion améliorée"""
    if reflexia_decision != zeroia_decision and reflexia_decision != "unknown":
        ensure_parent_dir(log_path)

        # Log the contradiction
        with open(log_path, "a") as f:
            f.write(
                textwrap.dedent(
                    f"""
                    [{datetime.utcnow()}] CONTRADICTION DETECTÉE —
                    ReflexIA={reflexia_decision}, ZeroIA={zeroia_decision}
                    """
                )
            )

        # Event sourcing de la contradiction
        # Note: event_store est géré dans la fonction appelante
        ark_logger.warning(
            f"CONTRADICTION DETECTED: ReflexIA = {reflexia_decision}, ZeroIA = {zeroia_decision}"
        )
        return True

    return False


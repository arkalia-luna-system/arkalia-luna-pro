#!/usr/bin/env python3
"""
🔧 Script de restauration des fichiers cassés par le script de linting
Corrige les erreurs de syntaxe créées par les commentaires noqa mal placés
"""

import re
import subprocess
from pathlib import Path

from core.ark_logger import ark_logger


def fix_broken_imports(file_path: Path) -> bool:
    """Corrige les imports cassés par les commentaires noqa mal placés"""
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    original_content = content

    # Corriger les patterns cassés
    patterns = [
        # Pattern: from module # noqa: F401 import item
        (
            r"from ([^#]+) # noqa: F401 import ([^#\n]+)",
            r"from \1 import \2  # noqa: F401",
        ),
        # Pattern: import item # noqa: F401
        (r"import ([^#\n]+) # noqa: F401", r"import \1  # noqa: F401"),
        # Pattern: EventType # noqa: F401 SOMETHING
        (r"EventType # noqa: F401\.([A-Z_]+)", r"EventType.\1  # noqa: F401"),
        # Pattern: event_store # noqa: F401
        (r"event_store # noqa: F401", r"event_store  # noqa: F401"),
        # Pattern: circuit_breaker # noqa: F401
        (r"circuit_breaker # noqa: F401", r"circuit_breaker  # noqa: F401"),
        # Pattern: create_default_context_enhanced # noqa: F401
        (
            r"create_default_context_enhanced # noqa: F401\(\)",
            r"create_default_context_enhanced()  # noqa: F401",
        ),
        # Pattern: reason_loop_enhanced # noqa: F401
        (r"reason_loop_enhanced # noqa: F401", r"reason_loop_enhanced  # noqa: F401"),
    ]

    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)

    if content != original_content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        ark_logger.info(f"✅ Fixed {file_path}", extra={"module": "scripts"})
        return True

    return False


def fix_variables_with_underscores(file_path: Path) -> bool:
    """Corrige les variables avec underscores mal placés"""
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    original_content = content

    # Corriger les variables avec underscores
    patterns = [
        (r"_config\d+", lambda m: m.group(0)[1:]),  # Enlever underscore
        (r"_original_count", "original_count"),
        (r"_cache_dir", "cache_dir"),
        (r"_cycle_result", "cycle_result"),
    ]

    for pattern, replacement in patterns:
        if callable(replacement):
            content = re.sub(pattern, replacement, content)
        else:
            content = re.sub(pattern, str(replacement), content)

    if content != original_content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        ark_logger.info(f"✅ Fixed variables in {file_path}", extra={"module": "scripts"})
        return True

    return False


def main() -> None:
    """Fonction principale de restauration"""
    ark_logger.info(
        "🔧 Début de la restauration des fichiers cassés...", extra={"module": "scripts"}
    )

    files_to_fix = [
        "modules/zeroia/__init__.py",
        "modules/zeroia/reason_loop_enhanced.py",
        "scripts/ark-validate-performance.py",
        "scripts/arkalia_enhanced_integration.py",
        "tests/unit/zeroia/event_store/test_export.py",
    ]

    fixed_count = 0

    for file_path in files_to_fix:
        path = Path(file_path)
        if path.exists():
            if fix_broken_imports(path):
                fixed_count += 1
            if fix_variables_with_underscores(path):
                fixed_count += 1

    # Formatage final
    try:
        subprocess.run(["isort", "."], check=True)
        subprocess.run(["black", "."], check=True)
        ark_logger.info("✅ Formatage final appliqué", extra={"module": "scripts"})
    except subprocess.CalledProcessError as e:
        ark_logger.info(f"❌ Erreur formatage: {e}", extra={"module": "scripts"})

    ark_logger.info(f"\n✅ Fichiers restaurés: {fixed_count}", extra={"module": "scripts"})


if __name__ == "__main__":
    main()

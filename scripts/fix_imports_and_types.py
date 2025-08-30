#!/usr/bin/env python3
"""
🔧 Script de correction automatique des imports et types
Corrige les erreurs d'imports manquants et les types dépréciés
"""

from core.ark_logger import ark_logger
import re
import subprocess
from pathlib import Path
from typing import Any


def fix_imports(content: str) -> str:
    """Corrige les imports manquants"""
    lines = content.split("\n")
    new_lines: list[str] = []

    # Chercher les imports typing existants
    typing_imports = []
    has_typing_import = False

    for line in lines:
        if line.strip().startswith("from typing import"):
            has_typing_import = True
            typing_imports = line.strip().replace("from typing import ", "").split(", ")
            break

    # Ajouter les imports manquants
    missing_imports = []
    if "List" not in typing_imports and "List" in content:
        missing_imports.append("List")
    if "Any" not in typing_imports and "Any" in content:
        missing_imports.append("Any")
    if "Optional" not in typing_imports and "Optional" in content:
        missing_imports.append("Optional")

    # Corriger les lignes
    for _i, line in enumerate(lines):
        if line.strip().startswith("from typing import") and missing_imports:
            # Ajouter les imports manquants
            existing_imports = line.strip().replace("from typing import ", "").split(", ")
            all_imports = existing_imports + missing_imports
            line = f"from typing import {', '.join(all_imports)}"
        elif not has_typing_import and ("List" in line or "Any" in line or "Optional" in line):
            # Ajouter une ligne d'import typing si elle n'existe pas
            imports_needed = []
            if "List" in line:
                imports_needed.append("List")
            if "Any" in line:
                imports_needed.append("Any")
            if "Optional" in line:
                imports_needed.append("Optional")
            if imports_needed:
                new_lines.insert(0, f"from typing import {', '.join(imports_needed)}")
                has_typing_import = True

        new_lines.append(line)

    return "\n".join(new_lines)


def fix_deprecated_types(content: str) -> str:
    """Corrige les types dépréciés"""
    # Remplacer typing.List par list
    content = re.sub(
        r"from typing import.*\bList\b",
        lambda m: m.group(0)
        .replace("List", "")
        .replace(", ,", ",")
        .replace(", ,", ",")
        .rstrip(", "),
        content,
    )
    content = re.sub(r"\bList\[", "list[", content)

    # Remplacer typing.Tuple par tuple
    content = re.sub(
        r"from typing import.*\bTuple\b",
        lambda m: m.group(0)
        .replace("Tuple", "")
        .replace(", ,", ",")
        .replace(", ,", ",")
        .rstrip(", "),
        content,
    )
    content = re.sub(r"\bTuple\[", "tuple[", content)

    # Nettoyer les imports vides
    content = re.sub(r"from typing import\s*,", "from typing import", content)
    content = re.sub(r"from typing import\s*$", "", content)

    return content


def process_file(file_path: Path) -> bool:
    """Traite un fichier pour corriger les imports et types"""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Appliquer les corrections
        content = fix_imports(content)
        content = fix_deprecated_types(content)

        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            ark_logger.info(f"✅ Fixed {file_path}", extra={"arkalia_module": "scripts"})
            return True

        return False
    except Exception as e:
        ark_logger.error(f"❌ Error processing {file_path}: {e}", extra={"arkalia_module": "scripts"})
        return False


def main() -> None:
    """Fonction principale"""
    ark_logger.info("🔧 Début de la correction des imports et types...", extra={"arkalia_module": "scripts"})

    # Fichiers à traiter
    files_to_fix = [
        "modules/arkalia_master/orchestrator_enhanced_v5.py",
        "modules/arkalia_master/orchestrator_ultimate.py",
        "modules/assistantia/core.py",
        "modules/assistantia/security/prompt_validator.py",
        "modules/cognitive_reactor/core.py",
        "modules/crossmodule_validator/core.py",
        "modules/error_recovery/core.py",
        "modules/generative_ai/core.py",
        "modules/monitoring/core.py",
        "modules/monitoring/prometheus_metrics.py",
        "modules/reflexia/logic/main_loop_enhanced.py",
        "modules/reflexia/logic/metrics_enhanced.py",
        "modules/sandozia/analyzer/behavior.py",
        "modules/sandozia/core/chronalia.py",
        "modules/sandozia/core/cognitive_reactor.py",
        "modules/sandozia/core/sandozia_core.py",
        "modules/sandozia/reasoning/collaborative.py",
        "modules/sandozia/utils/metrics.py",
        "modules/sandozia/validators/crossmodule.py",
        "modules/security/core.py",
        "modules/security/crypto/checksum_validator.py",
        "modules/security/crypto/secret_rotation.py",
        "modules/security/crypto/token_lifecycle.py",
        "modules/security/crypto/vault_manager.py",
        "modules/security/sandbox/__init__.py",
        "modules/security/watchdog/__init__.py",
        "modules/utils_enhanced/cache_enhanced.py",
        "modules/utils_enhanced/core.py",
        "modules/zeroia/circuit_breaker.py",
        "modules/zeroia/confidence_score.py",
        "modules/zeroia/core.py",
        "modules/zeroia/error_recovery_system.py",
        "modules/zeroia/event_store.py",
        "modules/zeroia/graceful_degradation.py",
        "modules/zeroia/model_integrity.py",
        "modules/zeroia/reason_loop.py",
        "modules/zeroia/reason_loop_enhanced.py",
        "modules/zeroia/snapshot_generator.py",
        "modules/zeroia/state/zeroia_state.py",
        "modules/zeroia/utils/state_writer.py",
        "scripts/fix_type_annotations.py",
        "utils/io_safe.py",
    ]

    fixed_count = 0

    for file_path in files_to_fix:
        path = Path(file_path)
        if path.exists():
            if process_file(path):
                fixed_count += 1

    # Formatage final
    try:
        subprocess.run(["black", "."], check=True, capture_output=True, text=True)
        ark_logger.info("✅ Formatage Black appliqué", extra={"arkalia_module": "scripts"})
    except subprocess.CalledProcessError as e:
        ark_logger.info(f"❌ Erreur formatage: {e}", extra={"arkalia_module": "scripts"})

    ark_logger.info(f"\n✅ Fichiers corrigés: {fixed_count}", extra={"arkalia_module": "scripts"})


if __name__ == "__main__":
    main()

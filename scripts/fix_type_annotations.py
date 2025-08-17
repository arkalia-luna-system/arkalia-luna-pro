#!/usr/bin/env python3
"""
🔧 Script de correction automatique des annotations de type
Corrige les erreurs de typage les plus communes dans le projet
"""

import re
import subprocess
from pathlib import Path
from typing import Any, Optional

from core.ark_logger import ark_logger


def add_return_type_annotations(content: str) -> str:
    """Ajoute les annotations de type de retour manquantes"""
    lines = content.split("\n")
    new_lines = []

    for i, line in enumerate(lines):
        # Chercher les fonctions sans annotation de retour
        if line.strip().startswith("def ") and " -> " not in line and line.strip().endswith(":"):
            # Vérifier les lignes suivantes pour déterminer le type de retour
            next_lines = lines[i + 1 : i + 5] if i + 1 < len(lines) else []
            next_content = "\n".join(next_lines)

            if "pass" in next_content or "return None" in next_content:
                # Fonction qui ne retourne rien
                line = line.replace("):", ") -> None:")
            elif "return True" in next_content or "return False" in next_content:
                # Fonction qui retourne un booléen
                line = line.replace("):", ") -> bool:")
            elif re.search(r"return\s+\d+", next_content):
                # Fonction qui retourne un entier
                line = line.replace("):", ") -> int:")
            elif re.search(r'return\s+["\'][^"\']*["\']', next_content):
                # Fonction qui retourne une chaîne
                line = line.replace("):", ") -> str:")

        new_lines.append(line)

    return "\n".join(new_lines)


def add_variable_annotations(content: str) -> str:
    """Ajoute les annotations de type pour les variables"""
    lines = content.split("\n")
    new_lines = []

    for line in lines:
        # Chercher les variables sans annotation
        if " = []" in line and ":" not in line:
            var_name = line.split(" = ")[0].strip()
            if var_name.isidentifier():
                line = line.replace(" = []", ": list[Any] = []")
        elif " = {}" in line and ":" not in line:
            var_name = line.split(" = ")[0].strip()
            if var_name.isidentifier():
                line = line.replace(" = {}", ": dict[str, Any] = {}")
        elif " = set()" in line and ":" not in line:
            var_name = line.split(" = ")[0].strip()
            if var_name.isidentifier():
                line = line.replace(" = set()", ": set[str] = set()")

        new_lines.append(line)

    return "\n".join(new_lines)


def fix_import_issues(content: str) -> str:
    """Corrige les problèmes d'import"""
    # Ajouter les imports manquants
    if "from typing import" in content and "Optional" not in content:
        content = content.replace("from typing import", "from typing import Optional, ")

    if "from typing import" in content and "" not in content:
        content = content.replace("from typing import", "from typing import ")

    return content


def process_file(file_path: Path) -> bool:
    """Traite un fichier pour corriger les annotations de type"""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Appliquer les corrections
        content = add_return_type_annotations(content)
        content = add_variable_annotations(content)
        content = fix_import_issues(content)

        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            ark_logger.info(f"✅ Fixed {file_path}", extra={"module": "scripts"})
            return True

        return False
    except Exception as e:
        ark_logger.error(f"❌ Error processing {file_path}: {e}", extra={"module": "scripts"})
        return False


def main() -> None:
    """Fonction principale"""
    ark_logger.info(
        "🔧 Début de la correction des annotations de type...", extra={"module": "scripts"}
    )

    # Fichiers à traiter en priorité
    priority_files = [
        "modules/zeroia/healthcheck_enhanced.py",
        "modules/zeroia/confidence_score.py",
        "modules/reflexia/logic/snapshot.py",
        "modules/assistantia/security/prompt_validator.py",
        "modules/taskia/__init__.py",
        "modules/security/watchdog/__init__.py",
        "modules/security/sandbox/__init__.py",
        "modules/helloria/state.py",
        "modules/helloria/core.py",
        "modules/helloria/routes/main.py",
        "modules/error_recovery/core.py",
        "modules/crossmodule_validator/core.py",
        "modules/arkalia_master/orchestrator_enhanced_v5.py",
        "modules/arkalia_master/orchestrator_ultimate.py",
        "modules/security/crypto/checksum_validator.py",
        "modules/security/crypto/secret_rotation.py",
        "modules/security/crypto/token_lifecycle.py",
        "modules/security/crypto/vault_manager.py",
        "modules/security/core.py",
        "modules/monitoring/core.py",
        "modules/monitoring/prometheus_metrics.py",
        "modules/monitoring/__init__.py",
        "modules/generative_ai/core.py",
        "modules/cognitive_reactor/core.py",
        "modules/zeroia/reason_loop_enhanced.py",
        "modules/zeroia/orchestrator.py",
        "modules/zeroia/core.py",
        "modules/zeroia/__init__.py",
        "modules/zeroia/failsafe.py",
        "modules/zeroia/circuit_breaker.py",
        "modules/zeroia/graceful_degradation.py",
        "modules/zeroia/error_recovery_system.py",
        "modules/utils_enhanced/core.py",
        "modules/sandozia/core/sandozia_core.py",
        "modules/sandozia/core/cognitive_reactor.py",
        "modules/sandozia/utils/metrics.py",
        "modules/sandozia/analyzer/behavior.py",
        "modules/sandozia/core/chronalia.py",
        "modules/sandozia/reasoning/collaborative.py",
        "modules/sandozia/validators/crossmodule.py",
        "modules/reflexia/logic/main_loop_enhanced.py",
        "modules/reflexia/logic/metrics_enhanced.py",
        "modules/reflexia/utils/config_loader.py",
        "modules/reflexia/core_api.py",
        "modules/helloria/__init__.py",
        "modules/error_recovery/__init__.py",
        "modules/crossmodule_validator/__init__.py",
        "modules/assistantia/core.py",
        "modules/assistantia/utils/ollama_connector.py",
        "utils/io_safe.py",
        "modules/zeroia/healthcheck_zeroia.py",
        "modules/zeroia/state/zeroia_state.py",
        "modules/zeroia/logic/reflexia_check_trigger.py",
        "modules/zeroia/snapshot_generator.py",
        "modules/zeroia/utils/state_writer.py",
        "modules/zeroia/model_integrity.py",
        "modules/zeroia/event_store.py",
        "modules/utils_enhanced/cache_enhanced.py",
        "modules/zeroia/reason_loop.py",
    ]

    fixed_count = 0

    for file_path in priority_files:
        path = Path(file_path)
        if path.exists():
            if process_file(path):
                fixed_count += 1

    # Formatage final
    try:
        subprocess.run(["isort", "."], check=True)
        subprocess.run(["black", "."], check=True)
        ark_logger.info("✅ Formatage final appliqué", extra={"module": "scripts"})
    except subprocess.CalledProcessError as e:
        ark_logger.info(f"❌ Erreur formatage: {e}", extra={"module": "scripts"})

    ark_logger.info(f"\n✅ Fichiers corrigés: {fixed_count}", extra={"module": "scripts"})


if __name__ == "__main__":
    main()

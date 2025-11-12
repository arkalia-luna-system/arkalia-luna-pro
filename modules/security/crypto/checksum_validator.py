"""
Module checksum_validator.

Ce module fait partie du système Arkalia Luna Pro.
"""

# 🔐 modules/security/crypto/checksum_validator.py
# Validation checksums SHA256 des artefacts de build

import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from core.ark_logger import ark_logger

logger = logging.getLogger(__name__)


class SecurityError(Exception):
    """Exception levée lors d'une violation de sécurité ou d'intégrité."""

    pass


class BuildIntegrityValidator:
    """
    Validateur d'intégrité des builds via checksums SHA256

    Fonctionnalités:
    - Génération checksums pour artefacts critiques
    - Validation vs manifest de référence
    - Détection tampering/corruption
    - Alerting sécurité automatique
    """

    def __init__(self, base_dir: Path | None = None) -> None:
        """
        Fonction __init__.

        Cette fonction fait partie du système Arkalia Luna Pro.
        """
        self.base_dir = Path(base_dir or ".")
        self.critical_extensions = {".py", ".so", ".dll", ".dylib", ".exe", ".jar"}
        self.manifest_file = self.base_dir / "security" / "checksums.manifest.json"
        self.violations_log = self.base_dir / "logs" / "integrity_violations.log"

        # Ensure directories exist
        self.manifest_file.parent.mkdir(parents=True, exist_ok=True)
        self.violations_log.parent.mkdir(parents=True, exist_ok=True)

    def generate_checksums(self, target_dir: Path | None = None) -> dict[str, str]:
        """
        Génère checksums SHA256 pour tous les fichiers critiques

        Args:
            target_dir: Dossier à scanner (défaut: base_dir)

        Returns:
            Dict mapping {fichier_relatif: sha256_hash}
        """
        scan_dir = Path(target_dir or self.base_dir)
        checksums: dict[str, Any] = {}

        logger.info(f"🔍 Scanning {scan_dir} for critical files...")

        for file_path in scan_dir.rglob("*"):
            if self._is_critical_file(file_path):
                try:
                    relative_path = file_path.relative_to(scan_dir)
                    sha256_hash = self._compute_file_hash(file_path)
                    checksums[str(relative_path)] = sha256_hash

                except Exception as e:
                    logger.warning(f"⚠️ Skipping {file_path}: {e}")

        logger.info(f"✅ Generated checksums for {len(checksums)} files")
        return checksums

    def save_manifest(self, checksums: dict[str, str], metadata: dict | None = None) -> Path:
        """
        Sauvegarde manifest de checksums avec métadonnées

        Args:
            checksums: Dict des checksums à sauvegarder
            metadata: Métadonnées additionnelles (version, build_id, etc.)

        Returns:
            Path du fichier manifest créé
        """
        manifest_data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "arkalia_version": self._get_arkalia_version(),
                "file_count": len(checksums),
                "security_level": "PARANOID",
                **(metadata or {}),
            },
            "checksums": checksums,
        }

        # Atomic write pour éviter corruption
        from utils.io_safe import save_json_safe

        save_json_safe(manifest_data, str(self.manifest_file))

        logger.info(f"💾 Manifest saved: {self.manifest_file}")
        return self.manifest_file

    def validate_integrity(self, manifest_path: Path | None = None) -> bool:
        """
        Valide intégrité complète vs manifest de référence

        Args:
            manifest_path: Chemin du manifest (défaut: manifest_file)

        Returns:
            True si intégrité OK, raise SecurityError sinon

        Raises:
            SecurityError: Si violation d'intégrité détectée
        """
        manifest_file = Path(manifest_path or self.manifest_file)

        if not manifest_file.exists():
            raise SecurityError(f"Manifest not found: {manifest_file}")

        logger.info(f"🔍 Validating integrity against {manifest_file}")

        # Load reference manifest
        manifest_data = json.loads(manifest_file.read_text())
        reference_checksums = manifest_data.get("checksums", {})

        # Generate current checksums
        current_checksums = self.generate_checksums()

        # Validate each file
        violations: list[Any] = []

        for file_path, expected_hash in reference_checksums.items():
            current_hash = current_checksums.get(file_path)

            if current_hash is None:
                violations.append(f"MISSING: {file_path}")
            elif current_hash != expected_hash:
                violations.append(
                    f"MODIFIED: {file_path} (expected: {expected_hash[:16]}..., "
                    f"got: {current_hash[:16]}...)"
                )

        # Check for new files not in manifest
        new_files = set(current_checksums.keys()) - set(reference_checksums.keys())
        for new_file in new_files:
            violations.append(f"UNAUTHORIZED: {new_file}")

        if violations:
            self._log_violations(violations, manifest_data.get("metadata", {}))
            raise SecurityError(f"Integrity violations detected: {len(violations)} issues")

        logger.info("✅ Integrity validation PASSED")
        return True

    def quick_check(self, critical_files: list[str] | None = None) -> dict[str, bool]:
        """
        Vérification rapide d'un sous-ensemble de fichiers critiques

        Args:
            critical_files: Liste des fichiers à vérifier (paths relatifs)

        Returns:
            Dict {fichier: integrity_ok}
        """
        if not self.manifest_file.exists():
            logger.warning("⚠️ No manifest found for quick check")
            return {}

        manifest_data = json.loads(self.manifest_file.read_text())
        reference_checksums = manifest_data.get("checksums", {})

        files_to_check = critical_files or self._get_critical_files_list()
        results: dict[str, Any] = {}

        for file_path in files_to_check:
            if file_path in reference_checksums:
                try:
                    full_path = self.base_dir / file_path
                    current_hash = self._compute_file_hash(full_path)
                    expected_hash = reference_checksums[file_path]
                    results[file_path] = current_hash == expected_hash
                except Exception as e:
                    logger.error(f"❌ Error checking {file_path}: {e}")
                    results[file_path] = False
            else:
                results[file_path] = False

        return results

    def _is_critical_file(self, file_path: Path) -> bool:
        if not file_path.is_file():
            return False

        # Extension critique
        if file_path.suffix.lower() in self.critical_extensions:
            return True

        # Fichiers spéciaux Arkalia
        critical_patterns = {
            "main.py",
            "core.py",
            "reason_loop.py",
            "requirements.txt",
            "pyproject.toml",
            "docker-compose.yml",
            "Dockerfile",
        }

        if file_path.name in critical_patterns:
            return True

        # Répertoires sensibles
        sensitive_dirs = {"modules", "scripts", "config"}
        if any(part in sensitive_dirs for part in file_path.parts):
            return file_path.suffix == ".py"

        return False

    def _compute_file_hash(self, file_path: Path) -> str:
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def _get_arkalia_version(self) -> str:
        try:
            import toml

            version_file = self.base_dir / "version.toml"
            if version_file.exists():
                version_data: dict[str, Any] = toml.load(version_file)
                current = version_data.get("current_version", "unknown")
                return str(current)
        except Exception:
            return "unknown"
        return "unknown"

    def _get_critical_files_list(self) -> list[str]:
        return [
            # "modules/zeroia/core.py",  # Module supprimé lors de la refactorisation
            "modules/reflexia/core.py",
            "modules/assistantia/core.py",
            "modules/security/__init__.py",
            "main.py",
            "docker-compose.yml",
        ]

    def _log_violations(self, violations: list[str], metadata: dict) -> None:
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "violations_count": len(violations),
            "manifest_metadata": metadata,
            "violations": violations,
            "security_level": "CRITICAL",
        }

        # Log en JSON pour parsing automatique
        with open(self.violations_log, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

        logger.critical(f"🚨 SECURITY VIOLATION: {len(violations)} integrity issues logged")


# Fonctions utilitaires
def generate_build_manifest(output_path: Path | None = None) -> Path:
    """
    Génère un manifest de build avec les checksums de tous les artefacts critiques.

    Args:
        output_path: Chemin optionnel pour sauvegarder le manifest.
                    Si None, utilise le chemin par défaut du validateur.

    Returns:
        Path: Chemin du fichier manifest généré.
    """
    validator = BuildIntegrityValidator()
    checksums = validator.generate_checksums()

    build_metadata = {
        "build_id": f"arkalia-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "build_type": "production",
        "git_commit": _get_git_commit(),
    }

    manifest_path = validator.save_manifest(checksums, build_metadata)
    return manifest_path


def validate_production_integrity() -> bool:
    """
    Valide l'intégrité de tous les artefacts en production.

    Vérifie que tous les fichiers critiques correspondent aux checksums
    enregistrés dans le manifest de référence.

    Returns:
        bool: True si l'intégrité est validée, False sinon.
    """
    try:
        validator = BuildIntegrityValidator()
        return validator.validate_integrity()
    except SecurityError as e:
        logger.critical(f"🚨 PRODUCTION INTEGRITY FAILED: {e}")
        return False


def _get_git_commit() -> str:
    try:
        from git import Repo

        repo = Repo(search_parent_directories=True)
        sha: str = repo.head.commit.hexsha
        return sha
    except Exception:
        return "unknown"


if __name__ == "__main__":
    # CLI pour génération/validation manifests
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "generate":
            manifest_path = generate_build_manifest()
            ark_logger.info(f"✅ Manifest generated: {manifest_path}", extra={"module": "crypto"})

        elif command == "validate":
            is_valid = validate_production_integrity()
            sys.exit(0 if is_valid else 1)

        elif command == "quick":
            validator = BuildIntegrityValidator()
            results = validator.quick_check()

            failed = [f for f, ok in results.items() if not ok]
            if failed:
                ark_logger.error(f"❌ Quick check failed: {failed}", extra={"module": "crypto"})
                sys.exit(1)
            else:
                ark_logger.info("✅ Quick check passed", extra={"module": "crypto"})

        else:
            ark_logger.info(
                "Usage: python checksum_validator.py [generate|validate|quick]",
                extra={"module": "crypto"},
            )
            sys.exit(1)
    else:
        # Mode interactif
        validator = BuildIntegrityValidator()
        checksums = validator.generate_checksums()
        ark_logger.info(
            f"Generated checksums for {len(checksums)} files", extra={"module": "crypto"}
        )

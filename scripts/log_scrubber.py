#!/usr/bin/env python3
"""
🧹 [LOG SCRUBBER] - Roadmap S1-P1 Arkalia-LUNA
Nettoyage automatique des logs sensibles et rotation intelligente

Fonctionnalités:
- Suppression données sensibles (tokens, mots de passe, IPs privées)
- Rotation logs par taille et âge
- Archivage compressé
- Métriques de nettoyage
"""

from core.ark_logger import ark_logger
import gzip
import json
import re
import shutil
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional


class LogScrubber:
    """Nettoyeur intelligent de logs Arkalia-LUNA"""

    def __init__(self, config_path: Path | None = None) -> None:
        self.config = self._load_config(config_path)
        log_files: list[Path] = []
        self.stats: dict[str, Any] = {
            "files_processed": 0,
            "sensitive_data_removed": 0,
            "bytes_saved": 0,
            "archives_created": 0,
            "errors": [],
        }

    def _load_config(self, config_path: Path | None) -> dict:
        """Charge la configuration du scrubber"""
        default_config = {
            "log_directories": [
                "logs/",
                "modules/*/logs/",
                "infrastructure/monitoring/loki/",
                "infrastructure/monitoring/prometheus/",
            ],
            "max_log_age_days": 30,
            "max_log_size_mb": 100,
            "sensitive_patterns": [
                r"password[\"\':\s]*[\"\']\w+[\"\']\s*",  # Mots de passe
                r"token[\"\':\s]*[\"\']\w+[\"\']\s*",  # Tokens
                r"api_key[\"\':\s]*[\"\']\w+[\"\']\s*",  # API keys
                r"\b192\.168\.\d{1,3}\.\d{1,3}\b",  # IPs privées
                r"\b10\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",  # IPs privées
                r"\b172\.(1[6-9]|2[0-9]|3[0-1])\.\d{1,3}\.\d{1,3}\b",  # IPs privées
                r"Bearer [A-Za-z0-9\-._~+/]+=*",  # Bearer tokens
                r"ssh-rsa [A-Za-z0-9+/=]+",  # SSH keys
            ],
            "archive_directory": "logs/archives/",
            "dry_run": False,
        }

        if config_path and config_path.exists():
            try:
                with open(config_path) as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                ark_logger.info(f"⚠️ [SCRUBBER] Erreur config: {e}, utilisation config par défaut", extra={"arkalia_module": "scripts"})

        return default_config

    def _find_log_files(self) -> list[Path]:
        """Trouve tous les fichiers de logs à traiter"""
        log_files = []
        base_path = Path(".")

        for pattern in self.config["log_directories"]:
            for log_file in base_path.glob(pattern + "*.log"):
                if log_file.is_file():
                    log_files.append(log_file)

            # Inclut aussi les fichiers .log dans sous-dossiers
            for log_file in base_path.glob(pattern + "**/*.log"):
                if log_file.is_file():
                    log_files.append(log_file)

        return sorted(set(log_files))

    def _scrub_sensitive_data(self, content: str) -> tuple[str, int]:
        """Supprime les données sensibles du contenu"""
        removed_count = 0
        scrubbed_content = content

        for pattern in self.config["sensitive_patterns"]:
            matches = re.findall(pattern, scrubbed_content, re.IGNORECASE)
            if matches:
                removed_count += len(matches)
                scrubbed_content = re.sub(
                    pattern,
                    "[REDACTED_SENSITIVE_DATA]",
                    scrubbed_content,
                    flags=re.IGNORECASE,
                )

        return scrubbed_content, removed_count

    def _should_archive(self, log_file: Path) -> bool:
        """Détermine si un fichier doit être archivé"""
        try:
            # Vérification âge
            file_age = datetime.now() - datetime.fromtimestamp(log_file.stat().st_mtime)
            max_age = timedelta(days=self.config["max_log_age_days"])

            # Vérification taille
            file_size_mb = log_file.stat().st_size / (1024 * 1024)
            max_size_mb = self.config["max_log_size_mb"]

            return file_age > max_age or file_size_mb > max_size_mb
        except Exception:
            return False

    def _archive_log_file(self, log_file: Path) -> Path | None:
        """Archive un fichier de log en le compressant"""
        try:
            archive_dir = Path(self.config["archive_directory"])
            archive_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_name = f"{log_file.stem}_{timestamp}.log.gz"
            archive_path = archive_dir / archive_name

            # Compression avec gzip
            with open(log_file, "rb") as f_in:
                with gzip.open(archive_path, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)

            # Calcul compression
            original_size = log_file.stat().st_size
            compressed_size = archive_path.stat().st_size
            compression_ratio = (1 - compressed_size / original_size) * 100

            ark_logger.info(
                f"📦 [SCRUBBER] Archivé: {log_file.name} → {archive_name} "
                f"(compression: {compression_ratio:.1f}%, extra={"arkalia_module": "scripts"})"
            )

            return archive_path

        except Exception as e:
            self.stats["errors"].append(f"Erreur archivage {log_file}: {e}")
            return None

    def _process_log_file(self, log_file: Path) -> bool:
        """Traite un fichier de log individuel"""
        try:
            ark_logger.info(f"🧹 [SCRUBBER] Traitement: {log_file}", extra={"arkalia_module": "scripts"})

            # Lecture du contenu
            with open(log_file, encoding="utf-8", errors="ignore") as f:
                original_content = f.read()

            original_size = len(original_content)

            # Nettoyage des données sensibles
            scrubbed_content, removed_count = self._scrub_sensitive_data(original_content)

            # Archivage si nécessaire
            if self._should_archive(log_file):
                archive_path = self._archive_log_file(log_file)
                if archive_path:
                    self.stats["archives_created"] += 1

                # Suppression de l'original après archivage réussi
                if not self.config["dry_run"] and archive_path:
                    log_file.unlink()
                    ark_logger.info(f"🗑️ [SCRUBBER] Supprimé original: {log_file}", extra={"arkalia_module": "scripts"})
            else:
                # Réécriture du fichier nettoyé
                if removed_count > 0 and not self.config["dry_run"]:
                    with open(log_file, "w", encoding="utf-8") as f:
                        f.write(scrubbed_content)

            # Mise à jour statistiques
            self.stats["files_processed"] += 1
            self.stats["sensitive_data_removed"] += removed_count
            self.stats["bytes_saved"] += original_size - len(scrubbed_content)

            if removed_count > 0:
                ark_logger.info(f"🛡️ [SCRUBBER] Données sensibles supprimées: {removed_count}", extra={"arkalia_module": "scripts"})

            return True

        except Exception as e:
            error_msg = f"Erreur traitement {log_file}: {e}"
            self.stats["errors"].append(error_msg)
            ark_logger.error(f"❌ [SCRUBBER] {error_msg}", extra={"arkalia_module": "scripts"})
            return False

    def run(self) -> dict:
        """Exécute le nettoyage complet des logs"""
        start_time = time.time()
        mode = "DRY RUN" if self.config["dry_run"] else "LIVE"
        ark_logger.info(f"🚀 [SCRUBBER] Démarrage nettoyage logs - Mode: {mode}", extra={"arkalia_module": "scripts"})

        # Recherche des fichiers de logs
        log_files = self._find_log_files()
        ark_logger.info(f"📂 [SCRUBBER] Fichiers trouvés: {len(log_files, extra={"arkalia_module": "scripts"})}")

        if not log_files:
            ark_logger.info("ℹ️ [SCRUBBER] Aucun fichier de log à traiter", extra={"arkalia_module": "scripts"})
            return self.stats

        # Traitement des fichiers
        for log_file in log_files:
            self._process_log_file(log_file)

        # Nettoyage archives anciennes (>90 jours)
        self._cleanup_old_archives()

        # Rapport final
        duration = time.time() - start_time
        self._generate_report(duration)

        return self.stats

    def _cleanup_old_archives(self):
        """Supprime les archives trop anciennes"""
        archive_dir = Path(self.config["archive_directory"])
        if not archive_dir.exists():
            return

        cutoff_date = datetime.now() - timedelta(days=90)
        removed_count = 0

        for archive_file in archive_dir.glob("*.gz"):
            try:
                file_date = datetime.fromtimestamp(archive_file.stat().st_mtime)
                if file_date < cutoff_date:
                    if not self.config["dry_run"]:
                        archive_file.unlink()
                    removed_count += 1
                    ark_logger.info(f"🗑️ [SCRUBBER] Archive ancienne supprimée: {archive_file.name}", extra={"arkalia_module": "scripts"})
            except Exception as e:
                self.stats["errors"].append(f"Erreur suppression archive {archive_file}: {e}")

        if removed_count > 0:
            ark_logger.info(f"🧹 [SCRUBBER] Archives anciennes supprimées: {removed_count}", extra={"arkalia_module": "scripts"})

    def _generate_report(self, duration: float):
        """Génère le rapport final de nettoyage"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": round(duration, 2),
            "stats": self.stats,
            "config": {
                "dry_run": self.config["dry_run"],
                "max_log_age_days": self.config["max_log_age_days"],
                "sensitive_patterns_count": len(self.config["sensitive_patterns"]),
            },
        }

        # Sauvegarde rapport
        report_path = Path("logs/scrubber_reports/")
        report_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = report_path / f"scrubber_report_{timestamp}.json"

        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        ark_logger.info("\n📊 [SCRUBBER] RAPPORT FINAL:", extra={"arkalia_module": "scripts"})
        ark_logger.info(f"   ⏱️ Durée: {duration:.2f}s", extra={"arkalia_module": "scripts"})
        ark_logger.info(f"   📁 Fichiers traités: {self.stats['files_processed']}", extra={"arkalia_module": "scripts"})
        sensitive_count = self.stats["sensitive_data_removed"]
        ark_logger.info(f"   🛡️ Données sensibles supprimées: {sensitive_count}", extra={"arkalia_module": "scripts"})
        ark_logger.info(f"   💾 Octets économisés: {self.stats['bytes_saved']:,}", extra={"arkalia_module": "scripts"})
        ark_logger.info(f"   📦 Archives créées: {self.stats['archives_created']}", extra={"arkalia_module": "scripts"})
        ark_logger.error(f"   ❌ Erreurs: {len(self.stats['errors'], extra={"arkalia_module": "scripts"})}")
        ark_logger.info(f"   📄 Rapport: {report_file}", extra={"arkalia_module": "scripts"})

        if self.stats["errors"]:
            ark_logger.info("\n⚠️ [SCRUBBER] ERREURS DÉTECTÉES:", extra={"arkalia_module": "scripts"})
            for error in self.stats["errors"][:5]:  # Limite à 5 erreurs
                ark_logger.error(f"   • {error}", extra={"arkalia_module": "scripts"})


def main():
    """Point d'entrée principal"""
    import argparse

    parser = argparse.ArgumentParser(description="🧹 Arkalia-LUNA Log Scrubber")
    parser.add_argument("--config", type=Path, help="Fichier de configuration JSON")
    parser.add_argument(
        "--dry-run", action="store_true", help="Mode simulation (aucune modification)"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Mode verbeux")

    args = parser.parse_args()

    scrubber = LogScrubber(config_path=args.config)

    if args.dry_run:
        scrubber.config["dry_run"] = True

    try:
        stats = scrubber.run()

        # Code de sortie basé sur les erreurs
        exit_code = 1 if stats["errors"] else 0
        exit(exit_code)

    except KeyboardInterrupt:
        ark_logger.info("\n🛑 [SCRUBBER] Interruption utilisateur", extra={"arkalia_module": "scripts"})
        exit(130)
    except Exception as e:
        raise RuntimeError(f"Erreur log scrubber: {e}") from e


if __name__ == "__main__":
    main()

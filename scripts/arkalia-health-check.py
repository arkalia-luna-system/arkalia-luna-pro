#!/usr/bin/env python3
"""
🔍 Arkalia-LUNA Pro - Health Check Complet
Script de diagnostic et monitoring des deux sites web
"""

import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import requests

from core.ark_logger import ark_logger

# Configuration logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class ArkaliaHealthChecker:
    """🔍 Vérificateur de santé complet pour Arkalia-LUNA Pro"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "unknown",
            "sites": {},
            "errors": [],
            "warnings": [],
            "recommendations": [],
        }

    def check_site_availability(self, url: str, name: str) -> dict:
        """Vérifie la disponibilité d'un site"""
        try:
            start_time = time.time()
            response = requests.get(url, timeout=10)
            response_time = time.time() - start_time

            return {
                "status": "online" if response.status_code == 200 else "error",
                "status_code": response.status_code,
                "response_time": round(response_time, 3),
                "content_length": len(response.content),
                "headers": dict(response.headers),
            }
        except Exception as e:
            return {"status": "offline", "error": str(e), "response_time": None}

    def check_processes(self) -> dict:
        """Vérifie les processus en cours"""
        processes = {}

        # Vérifier les ports
        ports_to_check = [8080, 5173, 3000, 8000]
        for port in ports_to_check:
            try:
                result = subprocess.run(
                    ["/usr/sbin/lsof", "-ti", f":{port}"], capture_output=True, text=True
                )  # nosec B607
                if result.stdout.strip():
                    processes[f"port_{port}"] = {
                        "status": "in_use",
                        "pids": result.stdout.strip().split("\n"),
                    }
                else:
                    processes[f"port_{port}"] = {"status": "free"}
            except Exception as e:
                processes[f"port_{port}"] = {"status": "error", "error": str(e)}

        return processes

    def check_logs(self) -> dict:
        """Analyse les logs pour détecter les erreurs"""
        log_analysis = {"recent_errors": [], "error_count": 0, "warning_count": 0}

        log_files = ["logs/arkalia_master.log", "logs/cognitive_reactor.log", "app_errors.log"]

        for log_file in log_files:
            log_path = self.project_root / log_file
            if log_path.exists():
                try:
                    with open(log_path) as f:
                        lines = f.readlines()
                        recent_lines = lines[-50:]  # Dernières 50 lignes

                        for line in recent_lines:
                            if any(
                                keyword in line.lower()
                                for keyword in ["error", "exception", "traceback"]
                            ):
                                log_analysis["recent_errors"].append(
                                    {
                                        "file": log_file,
                                        "line": line.strip(),
                                        "timestamp": datetime.now().isoformat(),
                                    }
                                )
                                log_analysis["error_count"] += 1
                            elif "warning" in line.lower():
                                log_analysis["warning_count"] += 1
                except Exception as e:
                    log_analysis["recent_errors"].append(
                        {"file": log_file, "error": f"Impossible de lire le fichier: {e}"}
                    )

        return log_analysis

    def check_file_integrity(self) -> dict:
        """Vérifie l'intégrité des fichiers critiques"""
        critical_files = [
            "docs/assets/arkalia-luna-theme.css",
            "frontend/src/App.jsx",
            "frontend/components/ArkaliaLunaHomepage.jsx",
            "modules/zeroia/core.py",
            "modules/zeroia/reason_loop.py",
            "config/arkalia_master_config.toml",
        ]

        integrity_check = {
            "missing_files": [],
            "corrupted_files": [],
            "total_files": len(critical_files),
            "valid_files": 0,
        }

        for file_path in critical_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                integrity_check["missing_files"].append(file_path)
            else:
                try:
                    # Vérifier si le fichier est lisible
                    with open(full_path) as f:
                        content = f.read()
                        if len(content) > 0:
                            integrity_check["valid_files"] += 1
                        else:
                            integrity_check["corrupted_files"].append(file_path)
                except Exception:
                    integrity_check["corrupted_files"].append(file_path)

        return integrity_check

    def check_performance(self) -> dict:
        """Vérifie les performances système"""
        try:
            import psutil

            return {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage("/").percent,
                "load_average": os.getloadavg() if hasattr(os, "getloadavg") else None,
            }
        except ImportError:
            return {"error": "psutil non disponible"}
        except Exception as e:
            return {"error": str(e)}

    def generate_recommendations(self) -> list[str]:
        """Génère des recommandations basées sur les résultats"""
        recommendations = []

        # Vérifier les sites
        for site_name, site_data in self.results["sites"].items():
            if site_data.get("status") == "offline":
                recommendations.append(f"🔴 Redémarrer le site {site_name}")
            elif site_data.get("response_time", 0) > 2.0:
                recommendations.append(f"⚠️ Optimiser les performances du site {site_name}")

        # Vérifier les erreurs
        if self.results["errors"]:
            recommendations.append("🔧 Corriger les erreurs identifiées dans les logs")

        # Vérifier l'intégrité des fichiers
        integrity = self.results.get("file_integrity", {})
        if integrity.get("missing_files"):
            recommendations.append("📁 Restaurer les fichiers manquants")
        if integrity.get("corrupted_files"):
            recommendations.append("🔧 Réparer les fichiers corrompus")

        # Vérifier les performances
        perf = self.results.get("performance", {})
        if isinstance(perf, dict) and not perf.get("error"):
            if perf.get("cpu_percent", 0) > 80:
                recommendations.append("⚡ Optimiser l'utilisation CPU")
            if perf.get("memory_percent", 0) > 85:
                recommendations.append("💾 Optimiser l'utilisation mémoire")

        return recommendations

    def run_full_check(self) -> dict:
        """Exécute une vérification complète"""
        logger.info("🔍 Démarrage du diagnostic Arkalia-LUNA Pro...")

        # Vérifier les sites
        logger.info("🌐 Vérification des sites web...")
        self.results["sites"] = {
            "mkdocs": self.check_site_availability("http://localhost:8080", "MkDocs"),
            "react": self.check_site_availability("http://localhost:5173", "React"),
        }

        # Vérifier les processus
        logger.info("⚙️ Vérification des processus...")
        self.results["processes"] = self.check_processes()

        # Vérifier les logs
        logger.info("📋 Analyse des logs...")
        self.results["logs"] = self.check_logs()

        # Vérifier l'intégrité des fichiers
        logger.info("🔍 Vérification de l'intégrité des fichiers...")
        self.results["file_integrity"] = self.check_file_integrity()

        # Vérifier les performances
        logger.info("⚡ Vérification des performances...")
        self.results["performance"] = self.check_performance()

        # Générer les recommandations
        self.results["recommendations"] = self.generate_recommendations()

        # Déterminer le statut global
        all_sites_online = all(
            site.get("status") == "online" for site in self.results["sites"].values()
        )

        has_errors = bool(self.results["errors"] or self.results["logs"]["error_count"] > 0)

        if all_sites_online and not has_errors:
            self.results["overall_status"] = "healthy"
        elif all_sites_online:
            self.results["overall_status"] = "warning"
        else:
            self.results["overall_status"] = "critical"

        return self.results

    def print_report(self):
        """Affiche le rapport de diagnostic"""
        ark_logger.info("\n" + "=" * 60, extra={"arkalia_module": "scripts"})
        ark_logger.info(
            "🔍 RAPPORT DE DIAGNOSTIC ARKALIA-LUNA PRO", extra={"arkalia_module": "scripts"}
        )
        ark_logger.info("=" * 60, extra={"arkalia_module": "scripts"})
        ark_logger.info(
            f"📅 Timestamp: {self.results['timestamp']}", extra={"arkalia_module": "scripts"}
        )
        ark_logger.info(
            f"🏥 Statut global: {self.results['overall_status'].upper()}",
            extra={"arkalia_module": "scripts"},
        )

        ark_logger.info("\n🌐 SITES WEB:", extra={"arkalia_module": "scripts"})
        for site_name, site_data in self.results["sites"].items():
            status_emoji = "🟢" if site_data["status"] == "online" else "🔴"
            ark_logger.info(
                f"  {status_emoji} {site_name.upper()}: {site_data['status']}",
                extra={"arkalia_module": "scripts"},
            )
            if site_data.get("response_time"):
                ark_logger.info(
                    f"     ⏱️ Temps de réponse: {site_data['response_time']}s",
                    extra={"arkalia_module": "scripts"},
                )

        ark_logger.info("\n⚙️ PROCESSUS:", extra={"arkalia_module": "scripts"})
        for proc_name, proc_data in self.results["processes"].items():
            status_emoji = "🟢" if proc_data["status"] == "free" else "🟡"
            ark_logger.info(
                f"  {status_emoji} {proc_name}: {proc_data['status']}",
                extra={"arkalia_module": "scripts"},
            )

        ark_logger.info("\n📋 LOGS:", extra={"arkalia_module": "scripts"})
        logs = self.results["logs"]
        ark_logger.error(
            f"  🔴 Erreurs: {logs['error_count']}", extra={"arkalia_module": "scripts"}
        )
        ark_logger.warning(
            f"  ⚠️ Avertissements: {logs['warning_count']}", extra={"arkalia_module": "scripts"}
        )

        ark_logger.info("\n🔍 INTÉGRITÉ DES FICHIERS:", extra={"arkalia_module": "scripts"})
        integrity = self.results["file_integrity"]
        ark_logger.info(
            f"  ✅ Fichiers valides: {integrity['valid_files']}/{integrity['total_files']}",
            extra={"arkalia_module": "scripts"},
        )
        if integrity["missing_files"]:
            ark_logger.info(
                f"  ❌ Fichiers manquants: {len(integrity['missing_files'])}",
                extra={"arkalia_module": "scripts"},
            )
        if integrity["corrupted_files"]:
            ark_logger.info(
                f"  🔧 Fichiers corrompus: {len(integrity['corrupted_files'])}",
                extra={"arkalia_module": "scripts"},
            )

        if self.results["recommendations"]:
            ark_logger.info("\n💡 RECOMMANDATIONS:", extra={"arkalia_module": "scripts"})
            for rec in self.results["recommendations"]:
                ark_logger.info(f"  {rec}", extra={"arkalia_module": "scripts"})

        ark_logger.info("\n" + "=" * 60, extra={"arkalia_module": "scripts"})


def main():
    """Point d'entrée principal"""
    checker = ArkaliaHealthChecker()
    results = checker.run_full_check()
    checker.print_report()

    # Sauvegarder le rapport
    report_path = Path("logs/health_check_report.json")
    report_path.parent.mkdir(exist_ok=True)

    with open(report_path, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    ark_logger.info(f"\n📄 Rapport sauvegardé: {report_path}", extra={"arkalia_module": "scripts"})

    # Code de sortie basé sur le statut
    if results["overall_status"] == "critical":
        sys.exit(1)
    elif results["overall_status"] == "warning":
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()

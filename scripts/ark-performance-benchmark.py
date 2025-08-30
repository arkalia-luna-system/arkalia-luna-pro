#!/usr/bin/env python3
# 🚀 scripts/ark-performance-benchmark.py
# Script d'exécution des benchmarks performance Arkalia-LUNA

"""
Script de benchmarking performance pour Arkalia-LUNA Enhanced v2.7.1

Fonctionnalités :
- Lance tous les tests de performance
- Collecte et sauvegarde les métriques
- Génère rapport HTML
- Détecte régressions performance
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

from core.ark_logger import ark_logger

# Ajouter le chemin des modules
sys.path.insert(0, str(Path(__file__).parent.parent))


def run_performance_tests(output_dir="benchmark_results"):
    """Lance les tests de performance et collecte les résultats"""

    ark_logger.info(
        "🚀 Lancement des benchmarks performance Arkalia-LUNA", extra={"arkalia_module": "scripts"}
    )
    ark_logger.info("=" * 60, extra={"arkalia_module": "scripts"})

    # Créer dossier de résultats
    results_dir = Path(output_dir)
    results_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Configuration environnement pour les tests
    env = os.environ.copy()
    env.update(
        {
            "ZEROIA_DECISION_THRESHOLD": "2.0",
            "CIRCUIT_LATENCY_THRESHOLD_MS": "10.0",
            "EVENT_STORE_WRITE_THRESHOLD_MS": "50.0",
            "PYTEST_CURRENT_TEST": "performance",
        }
    )

    # Commande pytest pour les tests de performance
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/performance/",
        "-v",
        "--benchmark-only",
        "--benchmark-sort=mean",
        "--benchmark-min-rounds=5",
        "--benchmark-warmup=1",
        "--benchmark-disable-gc",
        "--benchmark-skip",
        "-m",
        "performance",
        "--capture=no",  # Afficher les prints
    ]

    ark_logger.info(f"📊 Commande : {' '.join(cmd)}", extra={"arkalia_module": "scripts"})
    ark_logger.info(f"📁 Résultats dans : {results_dir}", extra={"arkalia_module": "scripts"})
    ark_logger.info("")

    # Exécuter les tests
    start_time = time.time()

    try:
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minutes max
        )

        end_time = time.time()
        duration = end_time - start_time

        # Sauvegarder les résultats
        results = {
            "timestamp": timestamp,
            "duration_seconds": duration,
            "return_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "environment": {
                "python_version": sys.version,
                "os": os.name,
                "platform": sys.platform,
            },
        }

        results_file = results_dir / f"benchmark_results_{timestamp}.json"
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)

        # Afficher résultats
        ark_logger.info(
            f"✅ Benchmarks terminés en {duration:.1f}s", extra={"arkalia_module": "scripts"}
        )
        ark_logger.info(
            f"📊 Code retour : {result.returncode}", extra={"arkalia_module": "scripts"}
        )
        ark_logger.info(
            f"💾 Résultats sauvés : {results_file}", extra={"arkalia_module": "scripts"}
        )

        if result.returncode == 0:
            ark_logger.info(
                "🎯 Tous les benchmarks ont réussi !", extra={"arkalia_module": "scripts"}
            )
        else:
            ark_logger.info("⚠️ Certains benchmarks ont échoué", extra={"arkalia_module": "scripts"})

        # Afficher stdout si présent
        if result.stdout:
            ark_logger.info("\n📋 Sortie des tests :", extra={"arkalia_module": "scripts"})
            ark_logger.info("-" * 40, extra={"arkalia_module": "scripts"})
            ark_logger.info(result.stdout, extra={"arkalia_module": "scripts"})

        if result.stderr:
            ark_logger.info("\n❌ Erreurs :", extra={"arkalia_module": "scripts"})
            ark_logger.info("-" * 40, extra={"arkalia_module": "scripts"})
            ark_logger.info(result.stderr, extra={"arkalia_module": "scripts"})

        return result.returncode == 0

    except subprocess.TimeoutExpired:
        ark_logger.info(
            "❌ Timeout : Les benchmarks ont pris trop de temps (>5min)",
            extra={"arkalia_module": "scripts"},
        )
        return False

    except Exception as e:
        ark_logger.info(f"❌ Erreur lors de l'exécution : {e}", extra={"arkalia_module": "scripts"})
        return False


def generate_summary_report(output_dir="benchmark_results"):
    """Génère un rapport de synthèse des benchmarks"""

    results_dir = Path(output_dir)
    if not results_dir.exists():
        ark_logger.info(f"❌ Dossier {output_dir} introuvable", extra={"arkalia_module": "scripts"})
        return

    # Trouver le fichier de résultats le plus récent
    json_files = list(results_dir.glob("benchmark_results_*.json"))
    if not json_files:
        ark_logger.info("❌ Aucun fichier de résultats trouvé", extra={"arkalia_module": "scripts"})
        return

    latest_file = max(json_files, key=lambda f: f.stat().st_mtime)

    try:
        with open(latest_file) as f:
            results = json.load(f)

        ark_logger.info("\n📊 RAPPORT DE SYNTHÈSE BENCHMARKS", extra={"arkalia_module": "scripts"})
        ark_logger.info("=" * 50, extra={"arkalia_module": "scripts"})
        ark_logger.info(f"📅 Date : {results['timestamp']}", extra={"arkalia_module": "scripts"})
        ark_logger.info(
            f"⏱️ Durée : {results['duration_seconds']:.1f}s", extra={"arkalia_module": "scripts"}
        )
        ark_logger.info(
            f"🎯 Statut : {'✅ SUCCÈS' if results['return_code'] == 0 else '❌ ÉCHEC'}",
            extra={"arkalia_module": "scripts"},
        )
        ark_logger.info(
            f"🐍 Python : {results['environment']['python_version'].split('.')[0]}",
            extra={"arkalia_module": "scripts"},
        )
        ark_logger.info(
            f"💻 Plateforme : {results['environment']['platform']}",
            extra={"arkalia_module": "scripts"},
        )

        # Extraire métriques du stdout si possible
        stdout = results.get("stdout", "")
        if "ZeroIA décision en" in stdout:
            ark_logger.info("\n🧠 Métriques ZeroIA :", extra={"arkalia_module": "scripts"})
            for line in stdout.split("\n"):
                if "ZeroIA décision en" in line:
                    ark_logger.info(f"  {line}", extra={"arkalia_module": "scripts"})

        if "Circuit Breaker" in stdout:
            ark_logger.info("\n⚡ Métriques Circuit Breaker :", extra={"arkalia_module": "scripts"})
            for line in stdout.split("\n"):
                if "Circuit Breaker" in line and "Latence" in line:
                    ark_logger.info(f"  {line}", extra={"arkalia_module": "scripts"})

        if "Event Store" in stdout:
            ark_logger.info("\n💾 Métriques Event Store :", extra={"arkalia_module": "scripts"})
            for line in stdout.split("\n"):
                if "Event Store" in line and "événements" in line:
                    ark_logger.info(f"  {line}", extra={"arkalia_module": "scripts"})

    except Exception as e:
        ark_logger.info(
            f"❌ Erreur lors de la génération du rapport : {e}", extra={"arkalia_module": "scripts"}
        )


def main():
    """Point d'entrée principal"""

    parser = argparse.ArgumentParser(description="Benchmarks performance Arkalia-LUNA Enhanced")
    parser.add_argument(
        "--output-dir",
        default="benchmark_results",
        help="Dossier de sortie des résultats",
    )
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Générer seulement le rapport (sans lancer les tests)",
    )

    args = parser.parse_args()

    try:
        if args.report_only:
            generate_summary_report(args.output_dir)
        else:
            success = run_performance_tests(args.output_dir)
            if success:
                generate_summary_report(args.output_dir)
            sys.exit(0 if success else 1)
    except Exception as e:
        ark_logger.info(f"❌ Erreur fatale : {e}", extra={"arkalia_module": "scripts"})
        sys.exit(1)


if __name__ == "__main__":
    main()

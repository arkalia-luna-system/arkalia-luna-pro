#!/usr/bin/env python3
"""
🚀 Bootstrap Arkalia-LUNA Pro - Script d'installation et vérification complète

Vérifications :
- Docker et Docker Compose
- Python venv et dépendances
- Ports disponibles
- Services uvicorn
- Configuration système
"""

import json
import os
import platform
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Optional

# Configuration
ARKALIA_PORTS = [8000, 8001, 8002, 8003, 3000, 9090, 9093, 3100]
REQUIRED_DOCKER_IMAGES = [
    "arkalia-api",
    "arkalia-assistantia",
    "arkalia-reflexia",
    "arkalia-zeroia",
    "arkalia-sandozia",
    "arkalia-cognitive-reactor",
]


class ArkaliaBootstrap:
    """Bootstrap complet pour Arkalia-LUNA Pro"""

    def __init__(self) -> None:
        self.project_root = Path(__file__).parent.parent.parent
        self.venv_path = self.project_root / "venv"
        self.results: dict[str, Any] = {
            "timestamp": time.time(),
            "system_info": {},
            "checks": {},
            "recommendations": [],
        }

    def print_header(self, title: str) -> None:
        """Affiche un en-tête"""
        print(f"\n{'=' * 60}")
        print(f"🎯 {title}")
        print(f"{'=' * 60}")

    def print_step(self, step: str, status: str = "✅") -> None:
        """Affiche une étape"""
        print(f"{status} {step}")

    def get_system_info(self) -> dict:
        """Collecte les informations système"""
        self.print_header("SYSTÈME")

        info = {
            "platform": platform.system(),
            "platform_version": platform.version(),
            "python_version": sys.version,
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "cwd": str(self.project_root),
            "user": os.getenv("USER", "unknown"),
            "home": os.getenv("HOME", "unknown"),
        }

        # Mémoire disponible
        try:
            if platform.system() == "Darwin":  # macOS
                result = subprocess.run(["vm_stat"], capture_output=True, text=True)
                if result.returncode == 0:
                    lines = result.stdout.split("\n")
                    for line in lines:
                        if "Pages free:" in line:
                            free_pages = int(line.split(":")[1].strip())
                            free_mb = (free_pages * 4096) / (1024 * 1024)
                            info["free_memory_mb"] = str(round(free_mb, 2))
                            break
            else:
                # Linux
                with open("/proc/meminfo") as f:
                    for line in f:
                        if "MemAvailable:" in line:
                            free_kb = int(line.split()[1])
                            info["free_memory_mb"] = str(round(free_kb / 1024, 2))
                            break
        except Exception:
            info["free_memory_mb"] = "unknown"

        self.results["system_info"] = info

        print(f"🖥️  Plateforme: {info['platform']} {info['platform_version']}")
        print(f"🐍 Python: {info['python_version'].split()[0]}")
        print(f"🏗️  Architecture: {info['architecture']}")
        print(f"👤 Utilisateur: {info['user']}")
        print(f"📂 Répertoire: {info['cwd']}")
        if info.get("free_memory_mb") != "unknown":
            print(f"🧠 Mémoire libre: {info['free_memory_mb']} MB")

        return info

    def check_docker(self) -> bool:
        """Vérifie Docker et Docker Compose"""
        self.print_header("DOCKER")

        checks = {}

        # Vérifier Docker
        try:
            result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                docker_version = result.stdout.strip()
                checks["docker"] = {"status": "✅", "version": docker_version}
                print(f"🐳 Docker: {docker_version}")
            else:
                checks["docker"] = {"status": "❌", "error": "Docker non installé"}
                print("❌ Docker non installé")
                return False
        except FileNotFoundError:
            checks["docker"] = {"status": "❌", "error": "Docker non trouvé"}
            print("❌ Docker non trouvé")
            return False

        # Vérifier Docker Compose
        try:
            result = subprocess.run(["docker-compose", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                compose_version = result.stdout.strip()
                checks["docker_compose"] = {"status": "✅", "version": compose_version}
                print(f"🐙 Docker Compose: {compose_version}")
            else:
                checks["docker_compose"] = {"status": "❌", "error": "Docker Compose non installé"}
                print("❌ Docker Compose non installé")
                return False
        except FileNotFoundError:
            checks["docker_compose"] = {"status": "❌", "error": "Docker Compose non trouvé"}
            print("❌ Docker Compose non trouvé")
            return False

        # Vérifier que Docker daemon fonctionne
        try:
            result = subprocess.run(["docker", "info"], capture_output=True, text=True)
            if result.returncode == 0:
                checks["docker_daemon"] = {"status": "✅", "info": "Docker daemon actif"}
                print("✅ Docker daemon actif")
            else:
                checks["docker_daemon"] = {"status": "❌", "error": "Docker daemon inactif"}
                print("❌ Docker daemon inactif")
                return False
        except Exception as e:
            checks["docker_daemon"] = {"status": "❌", "error": str(e)}
            print(f"❌ Erreur Docker daemon: {e}")
            return False

        self.results["checks"]["docker"] = checks
        return True

    def check_python_venv(self) -> bool:
        """Vérifie l'environnement Python virtuel"""
        self.print_header("PYTHON VENV")

        checks = {}

        # Vérifier si on est dans un venv
        in_venv = hasattr(sys, "real_prefix") or (
            hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
        )
        checks["in_venv"] = {"status": "✅" if in_venv else "❌", "value": in_venv}

        if in_venv:
            print("✅ Environnement virtuel actif")
            print(f"   📂 Venv: {sys.prefix}")
        else:
            print("❌ Pas d'environnement virtuel actif")
            print("   💡 Recommandation: Créer et activer un venv")

        # Vérifier les dépendances principales
        required_packages = [
            "fastapi",
            "uvicorn",
            "pydantic",
            "prometheus_client",
            "toml",
            "pytest",
            "black",
            "ruff",
        ]

        missing_packages = []
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
                checks[f"package_{package}"] = {"status": "✅", "installed": True}
            except ImportError:
                missing_packages.append(package)
                checks[f"package_{package}"] = {"status": "❌", "installed": False}

        if missing_packages:
            print(f"❌ Packages manquants: {', '.join(missing_packages)}")
            print("   💡 Installer: pip install -r requirements.txt")
        else:
            print("✅ Tous les packages requis sont installés")

        self.results["checks"]["python_venv"] = checks
        return len(missing_packages) == 0

    def check_ports(self) -> bool:
        """Vérifie la disponibilité des ports"""
        self.print_header("PORTS")

        checks = {}
        available_ports = []
        occupied_ports = []

        for port in ARKALIA_PORTS:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    result = s.connect_ex(("localhost", port))
                    if result == 0:
                        occupied_ports.append(port)
                        checks[f"port_{port}"] = {"status": "❌", "occupied": True}
                    else:
                        available_ports.append(port)
                        checks[f"port_{port}"] = {"status": "✅", "occupied": False}
            except Exception as e:
                checks[f"port_{port}"] = {"status": "⚠️", "error": str(e)}

        print(f"✅ Ports disponibles: {', '.join(map(str, available_ports))}")
        if occupied_ports:
            print(f"❌ Ports occupés: {', '.join(map(str, occupied_ports))}")
            print("   💡 Arrêter les services ou changer les ports")

        self.results["checks"]["ports"] = checks
        return len(occupied_ports) == 0

    def check_uvicorn_services(self) -> bool:
        """Vérifie les services uvicorn"""
        self.print_header("UVICORN SERVICES")

        checks = {}
        services = [
            {"name": "arkalia-api", "port": 8000, "path": "scripts/run/run_arkalia_api.py"},
            {"name": "reflexia-api", "port": 8002, "path": "scripts/run/run_reflexia_api.py"},
        ]

        for service in services:
            service_path = self.project_root / Path(service["path"])
            if service_path.exists():
                checks[f"service_{service['name']}"] = {
                    "status": "✅",
                    "exists": True,
                    "path": str(service_path),
                }
                print(f"✅ {service['name']}: {service_path}")
            else:
                checks[f"service_{service['name']}"] = {
                    "status": "❌",
                    "exists": False,
                    "path": str(service_path),
                }
                print(f"❌ {service['name']}: {service_path} manquant")

        self.results["checks"]["uvicorn_services"] = checks
        return all(check["exists"] for check in checks.values())

    def check_docker_images(self) -> bool:
        """Vérifie les images Docker requises"""
        self.print_header("DOCKER IMAGES")

        checks = {}
        missing_images = []

        try:
            result = subprocess.run(
                ["docker", "images", "--format", "{{.Repository}}"], capture_output=True, text=True
            )
            if result.returncode == 0:
                available_images = result.stdout.strip().split("\n")

                for image in REQUIRED_DOCKER_IMAGES:
                    if image in available_images:
                        checks[f"image_{image}"] = {"status": "✅", "available": True}
                        print(f"✅ {image}")
                    else:
                        missing_images.append(image)
                        checks[f"image_{image}"] = {"status": "❌", "available": False}
                        print(f"❌ {image}")
            else:
                print("❌ Impossible de lister les images Docker")
                return False
        except Exception as e:
            print(f"❌ Erreur lors de la vérification des images: {e}")
            return False

        if missing_images:
            print(f"   💡 Images manquantes: {', '.join(missing_images)}")
            print("   💡 Construire: docker-compose build")

        self.results["checks"]["docker_images"] = checks
        return len(missing_images) == 0

    def generate_recommendations(self) -> None:
        """Génère des recommandations basées sur les vérifications"""
        self.print_header("RECOMMANDATIONS")

        recommendations = []

        # Vérifications Docker
        docker_checks = self.results["checks"].get("docker", {})
        if not docker_checks:
            recommendations.append("🔧 Installer Docker et Docker Compose")

        # Vérifications Python
        python_checks = self.results["checks"].get("python_venv", {})
        if not python_checks.get("in_venv", {}).get("value", False):
            recommendations.append("🐍 Créer et activer un environnement virtuel Python")

        missing_packages = [
            k
            for k, v in python_checks.items()
            if k.startswith("package_") and not v.get("installed", False)
        ]
        if missing_packages:
            recommendations.append("📦 Installer les dépendances: pip install -r requirements.txt")

        # Vérifications ports
        port_checks = self.results["checks"].get("ports", {})
        occupied_ports = [
            k for k, v in port_checks.items() if k.startswith("port_") and v.get("occupied", False)
        ]
        if occupied_ports:
            recommendations.append("🔌 Libérer les ports occupés ou modifier la configuration")

        # Vérifications services
        service_checks = self.results["checks"].get("uvicorn_services", {})
        missing_services = [
            k
            for k, v in service_checks.items()
            if k.startswith("service_") and not v.get("exists", False)
        ]
        if missing_services:
            recommendations.append("🚀 Vérifier les fichiers de services uvicorn")

        # Vérifications images
        image_checks = self.results["checks"].get("docker_images", {})
        missing_images = [
            k
            for k, v in image_checks.items()
            if k.startswith("image_") and not v.get("available", False)
        ]
        if missing_images:
            recommendations.append("🐳 Construire les images Docker: docker-compose build")

        # Recommandations générales
        recommendations.extend(
            [
                "📊 Configurer Grafana pour le monitoring",
                "🔒 Vérifier les permissions des fichiers sensibles",
                "📝 Consulter la documentation: docs/",
                "🧪 Lancer les tests: make test",
            ]
        )

        for i, rec in enumerate(recommendations, 1):
            print(f"{i:2d}. {rec}")

        self.results["recommendations"] = recommendations

    def save_report(self, filename: str = "bootstrap_report.json"):
        """Sauvegarde le rapport de bootstrap"""
        report_path = self.project_root / filename
        with open(report_path, "w") as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"\n💾 Rapport sauvegardé: {report_path}")

    def run_full_check(self) -> bool:
        """Exécute toutes les vérifications"""
        self.print_header("BOOTSTRAP ARKALIA-LUNA PRO")

        print("🔍 Vérification complète du système...")

        # Collecter les informations système
        self.get_system_info()

        # Vérifications critiques
        checks = [
            ("Docker", self.check_docker),
            ("Python Venv", self.check_python_venv),
            ("Ports", self.check_ports),
            ("Uvicorn Services", self.check_uvicorn_services),
            ("Docker Images", self.check_docker_images),
        ]

        all_passed = True
        for name, check_func in checks:
            try:
                if not check_func():
                    all_passed = False
            except Exception as e:
                print(f"❌ Erreur lors de la vérification {name}: {e}")
                all_passed = False

        # Générer les recommandations
        self.generate_recommendations()

        # Sauvegarder le rapport
        self.save_report()

        # Résumé final
        self.print_header("RÉSUMÉ")
        if all_passed:
            print("🎉 Toutes les vérifications sont passées !")
            print("🚀 Arkalia-LUNA est prêt à démarrer.")
            print("   💡 Commandes utiles:")
            print("      make run          # Démarrer tous les services")
            print("      make test         # Lancer les tests")
            print("      python scripts/launch_demo_scenario.py --all  # Démo complète")
        else:
            print("⚠️  Certaines vérifications ont échoué.")
            print("🔧 Suivre les recommandations ci-dessus.")

        return all_passed


def main() -> None:
    """Point d'entrée principal"""
    bootstrap = ArkaliaBootstrap()

    try:
        success = bootstrap.run_full_check()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Bootstrap interrompu par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur lors du bootstrap: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

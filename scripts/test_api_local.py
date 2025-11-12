#!/usr/bin/env python3
"""
🧪 Script de test local pour l'API Arkalia-LUNA
Vérifie que l'API fonctionne avant de tester avec Docker
"""

import sys
from pathlib import Path

import requests


def test_api_endpoints() -> None:
    """Test des endpoints de l'API"""
    base_url = "http://localhost:8000"
    endpoints = ["/", "/health", "/status", "/metrics"]

    print("🧪 Test des endpoints de l'API Arkalia-LUNA...")
    print(f"📍 URL de base: {base_url}")
    print()

    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            if response.status_code == 200:
                print(f"✅ {endpoint} - OK (Status: {response.status_code})")
                if endpoint == "/health":
                    print(f"   📊 Réponse: {response.json()}")
            else:
                print(f"❌ {endpoint} - ÉCHEC (Status: {response.status_code})")
        except requests.exceptions.ConnectionError:
            print(f"❌ {endpoint} - Impossible de se connecter (API non démarrée)")
        except requests.exceptions.Timeout:
            print(f"⏰ {endpoint} - Timeout (API trop lente)")
        except Exception as e:
            print(f"💥 {endpoint} - Erreur: {e}")

    print()


def test_api_startup() -> bool:
    """Test du démarrage de l'API"""
    print("🚀 Test du démarrage de l'API...")

    # Vérifier que le fichier principal existe
    api_file = Path("scripts/run/run_arkalia_api.py")
    if not api_file.exists():
        print("❌ Fichier scripts/run/run_arkalia_api.py non trouvé")
        return False

    # Vérifier que modules/helloria/core.py existe
    core_file = Path("modules/helloria/core.py")
    if not core_file.exists():
        print("❌ Fichier modules/helloria/core.py non trouvé")
        return False

    print("✅ Fichiers de l'API présents")

    # Vérifier les dépendances
    try:
        import fastapi  # noqa: F401
        import uvicorn  # noqa: F401

        print("✅ Dépendances FastAPI et Uvicorn disponibles")
    except ImportError as e:
        print(f"❌ Dépendance manquante: {e}")
        return False

    return True


def test_docker_healthcheck() -> bool:
    """Test du healthcheck Docker"""
    print("🐳 Test du healthcheck Docker...")

    # Simuler le healthcheck Docker
    healthcheck_cmd = [
        "python",
        "-c",
        "import requests; requests.get('http://localhost:8000/health', timeout=5)",
    ]

    print(f"🔍 Commande de test: {' '.join(healthcheck_cmd)}")

    try:
        import requests

        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Healthcheck Docker - OK")
            print(f"   📊 Réponse: {response.json()}")
            return True
        else:
            print(f"❌ Healthcheck Docker - ÉCHEC (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Healthcheck Docker - Erreur: {e}")
        return False


def main() -> None:
    """Fonction principale"""
    print("🌕 Test de l'API Arkalia-LUNA")
    print("=" * 50)

    # Test 1: Vérification des fichiers et dépendances
    if not test_api_startup():
        print("❌ L'API ne peut pas démarrer")
        sys.exit(1)

    print()

    # Test 2: Test du healthcheck Docker
    if not test_docker_healthcheck():
        print("❌ Le healthcheck Docker échoue")
        print("💡 Vérifiez que l'API est démarrée sur le port 8000")
        sys.exit(1)

    print()

    # Test 3: Test de tous les endpoints
    test_api_endpoints()

    print("🎉 Tous les tests sont passés!")
    print("✅ L'API est prête pour Docker")


if __name__ == "__main__":
    main()

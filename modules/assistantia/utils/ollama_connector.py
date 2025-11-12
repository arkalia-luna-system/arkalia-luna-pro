"""
Module de connexion à Ollama.

Ce module gère la communication avec l'API Ollama pour les requêtes
de modèles de langage.
"""

# modules/assistantia/utils/ollama_connector.py

import json
import os
from typing import Any

import requests

# Configuration Ollama - utiliser l'IP de l'hôte pour Docker
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "host.docker.internal")  # Accès à l'hôte depuis Docker
OLLAMA_PORT = os.getenv("OLLAMA_PORT", "11434")
OLLAMA_BASE_URL = f"http://{OLLAMA_HOST}:{OLLAMA_PORT}"


def query_ollama(prompt: str, model: str = "llama2", temperature: float = 0.7) -> str:
    """Interroge l'API Ollama avec un prompt donné."""
    # Vérifier si le prompt est vide
    if not prompt.strip():
        return "[⚠️ Réponse IA vide]"

    try:
        # Vérifier si le modèle est disponible
        available_models = get_available_models()
        if available_models:
            model_names = [m.get("name", "") for m in available_models.get("models", [])]
            # Vérifier si le modèle exact existe ou si une version avec tag existe
            if model not in model_names:
                # Essayer de trouver une version avec tag (ex: mistral -> mistral:latest)
                base_model = model.split(":")[0]
                matching_models = [m for m in model_names if m.startswith(f"{base_model}:")]
                if not matching_models:
                    available = ", ".join(model_names)
                    raise ValueError(
                        f"Modèle '{model}' non disponible. Modèles disponibles: {available}"
                    )
                # Utiliser le premier modèle trouvé avec le bon préfixe
                model = matching_models[0]

        url = f"{OLLAMA_BASE_URL}/api/generate"
        payload = {"model": model, "prompt": prompt, "temperature": temperature, "stream": False}

        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()

        data = response.json()
        return data.get("response", "Aucune réponse reçue")
    except ValueError:
        # Re-raise ValueError pour les modèles invalides
        raise
    except requests.RequestException as e:
        return f"Erreur IA: {str(e)}"
    except json.JSONDecodeError:
        return "Erreur de décodage JSON"
    except Exception as e:
        return f"Erreur inattendue: {str(e)}"


def get_available_models() -> dict[str, Any] | None:
    """Récupère la liste des modèles disponibles."""
    try:
        url = f"{OLLAMA_BASE_URL}/api/tags"
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()
        return data
    except requests.RequestException:
        return None
    except Exception:
        return None


def check_ollama_health() -> bool:
    """Vérifie si Ollama est accessible."""
    try:
        url = f"{OLLAMA_BASE_URL}/api/tags"
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except Exception:
        return False

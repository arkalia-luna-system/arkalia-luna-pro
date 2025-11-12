"""
Module main.

Ce module fait partie du système Arkalia Luna Pro.
"""

import os

from core import app

if __name__ == "__main__":
    import uvicorn

    # Utiliser une variable d'environnement pour le host
    # "127.0.0.1" par défaut pour la sécurité
    # En production, définir explicitement HOST=0.0.0.0 via variable d'environnement
    host = os.getenv("HOST", "127.0.0.1")
    uvicorn.run(app, host=host, port=8000)

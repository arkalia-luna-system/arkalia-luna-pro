"""Module core d'Arkalia-LUNA Pro.

Ce module expose l'API FastAPI de base pour le système Arkalia.
"""

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root() -> dict:
    """Endpoint racine de l'API Arkalia Core.

    Returns:
        dict: Message de bienvenue.
    """
    return {"message": "Hello from Arkalia Core"}

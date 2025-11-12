"""
Module de traitement pour AssistantIA.

Ce module gère le prétraitement des messages utilisateur
avant envoi aux modèles de langage.
"""
# modules/assistantia/utils/processing.py


def process_input(message: str) -> str:
    """Prétraite le message utilisateur."""
    message = message.strip()
    if not message:
        return "Tu as dit : "
    return f"Tu as dit : {message}"

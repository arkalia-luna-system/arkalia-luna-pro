"""
Module de métriques pour Reflexia.

Ce module gère la collecte et l'analyse des métriques système
pour les vérifications Reflexia.
"""


def read_metrics() -> dict:
    """
    Simule la collecte de métriques système.
    Peut être remplacée plus tard par psutil ou outils réels.
    """
    return {
        "cpu": 72.5,
        "ram": 61.8,
        "latency": 145,
    }

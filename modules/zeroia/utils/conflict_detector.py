"""Détecteur de conflits pour le module ZeroIA.

Ce module fournit des fonctions pour détecter les conflits entre
différents états ou configurations.
"""


def detect_conflict(dict1: dict, dict2: dict) -> bool:
    """Détecte les conflits entre deux dictionnaires.

    Args:
        dict1: Premier dictionnaire à comparer.
        dict2: Deuxième dictionnaire à comparer.

    Returns:
        bool: True si un conflit est détecté, False sinon.
    """
    return any(key in dict2 and dict1[key] != dict2[key] for key in dict1)

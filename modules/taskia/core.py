"""
Module core.

Ce module fait partie du système Arkalia Luna Pro.
"""

from modules.taskia.utils.formatter import format_summary


def taskia_main(context: dict) -> str:
    """
    Fonction principale de TaskIA pour formater un résumé.

    Args:
        context: Dictionnaire contenant les données à formater.

    Returns:
        str: Résumé formaté.
    """
    return format_summary(context)

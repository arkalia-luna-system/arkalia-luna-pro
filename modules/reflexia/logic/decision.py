"""
Module de décision pour Reflexia.

Ce module gère l'évaluation des métriques système et la prise de décision
pour les vérifications Reflexia.
"""
def monitor_status(metrics: dict) -> str:
    """
    Évalue les métriques et renvoie un statut global.
    """
    if metrics["cpu"] > 90:
        return "🛑 surcharge CPU"
    if metrics["ram"] > 80:
        return "⚠️ haute mémoire"
    if metrics["latency"] > 300:
        return "degraded"
    return "ok"

# 📁 modules/reflexia/core.py

"""
Module principal pour lancer la logique réflexive :
- Check unique (snapshot + status)
- Boucle réflexive (surveillance continue)
- Version Enhanced v2.6.0 avec vraies métriques
"""

from core.ark_logger import ark_logger
from modules.reflexia.logic.decision import monitor_status
from modules.reflexia.logic.metrics_enhanced import read_metrics, read_metrics_enhanced
from modules.reflexia.logic.snapshot import save_snapshot


def launch_reflexia_check() -> dict:
    """
    📍 Lance une vérification réflexive unique :
    - Collecte des métriques système RÉELLES
    - Évaluation de l'état via `monitor_status`
    - Sauvegarde snapshot dans `state/`

    :return: Dictionnaire contenant `status` (str) et `metrics` (dict)
    """
    metrics = read_metrics()
    status = monitor_status(metrics)

    # ✅ Sauvegarde même si status critique
    save_snapshot(metrics, status)

    return {"status": status, "metrics": metrics}


def launch_reflexia_check_enhanced() -> dict:
    """
    📍 Version Enhanced avec métriques complètes système + containers
    """
    metrics_enhanced = read_metrics_enhanced()
    metrics_simple = read_metrics()
    status = monitor_status(metrics_simple)

    save_snapshot(metrics_simple, status)

    return {
        "status": status,
        "metrics": metrics_simple,
        "enhanced_metrics": metrics_enhanced,
    }


# ✅ Alias utilisé par l'API pour simplifier les imports
def get_metrics() -> dict:
    """
    🎯 Interface simple pour l'API REST :
    Retourne les métriques RÉELLES (plus les static fake).
    """
    return read_metrics()


def launch_reflexia_loop(max_iterations: int | None = None) -> None:
    """
    🔁 Lance la boucle réflexive automatique Enhanced v2.6.0
    Utilise maintenant les vraies métriques système !
    """
    from modules.reflexia.logic.main_loop_enhanced import reflexia_loop_enhanced

    ark_logger.info("🚀 Démarrage Reflexia Enhanced v2.6.0", extra={"arkalia_module": "reflexia"})
    reflexia_loop_enhanced(max_iterations=max_iterations)


def load_reflexia_data() -> dict:
    """Fonction de compatibilité - maintenant avec vraies données"""
    metrics = read_metrics()
    return {
        "metrics": metrics,
        "status": "enhanced_v2.6.0",
    }

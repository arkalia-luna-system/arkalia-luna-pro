"""
Persistence - Sauvegarde état et dashboard
"""

from datetime import datetime
from pathlib import Path

from modules.utils.helpers import save_json_if_changed, save_toml_if_changed
from modules.zeroia.event_store import EventType
from modules.zeroia.utils.backup import save_backup

from .initialization import initialize_components_with_recovery

# === Chemins par défaut ===
STATE_PATH = Path("state/zeroia_state.toml")
DASHBOARD_PATH = Path("state/zeroia_dashboard.json")
LOG_PATH = Path("modules/zeroia/logs/zeroia.log")


def ensure_parent_dir(path: Path) -> None:
    """Assure que le répertoire parent existe"""
    target = path.parent if path.suffix else path
    target.mkdir(parents=True, exist_ok=True)


def persist_state_enhanced(
    decision: str,
    score: float,
    ctx: dict,
    state_path_override: Path | None = None,
) -> None:
    """Persistance d'état avec event sourcing"""
    reflexia_summary = ctx.get("reflexia", {})
    status = ctx.get("status", {})
    cpu = status.get("cpu", "N/A")
    severity = status.get("severity", "none")

    state_path = state_path_override or STATE_PATH
    ensure_parent_dir(state_path)
    save_backup()

    # Sauvegarder l'état
    save_toml_if_changed(
        {
            "decision": {
                "last_decision": decision,
                "confidence_score": score,
                "justification": f"cpu={cpu}, severity={severity}",
                "timestamp": datetime.now().isoformat(),
            }
        },
        str(state_path),
    )

    # Event sourcing de la décision
    _, es, _, _ = initialize_components_with_recovery()
    es.add_event(
        EventType.DECISION_MADE,
        {
            "decision": decision,
            "confidence": score,
            "cpu": cpu,
            "severity": severity,
            "reflexia_summary": reflexia_summary,
            "justification": f"cpu={cpu}, severity={severity}",
        },
    )

    # Log traditionnel
    ensure_parent_dir(LOG_PATH)
    with open(LOG_PATH, "a") as f:
        f.write(
            f"{datetime.now()} :: FROM REFLEXIA: {reflexia_summary} | "
            f"CPU={cpu} | SEVERITY={severity} → DECISION = "
            f"{decision} (confidence={score})\n"
        )


def update_dashboard_enhanced(
    decision: str,
    score: float,
    ctx: dict,
    dashboard_path_override: Path | None = None,
) -> None:
    """Mise à jour dashboard avec métriques circuit breaker"""
    dashboard_path = dashboard_path_override or DASHBOARD_PATH
    ensure_parent_dir(dashboard_path)

    cb, es, _, _ = initialize_components_with_recovery()

    # Récupérer les métriques du circuit breaker
    cb_status = cb.get_status()

    # Récupérer analytics des événements
    analytics = es.get_analytics()

    dashboard_data = {
        "last_decision": decision,
        "confidence": score,
        "reasoning_loop_active": True,
        "connected_modules": ["reflexia"],
        "previous": ["reduce_load", "monitor", "monitor"],
        "last_updated": datetime.now().isoformat(),
        "circuit_breaker": {
            "state": cb_status["state"],
            "failure_rate": cb_status["metrics"]["failure_rate"],
            "success_rate": cb_status["metrics"]["success_rate"],
            "consecutive_failures": cb_status["metrics"]["consecutive_failures"],
        },
        "event_analytics": {
            "total_events": analytics["total_events"],
            "recent_events": analytics["recent_events_analyzed"],
            "events_by_type": analytics["events_by_type"],
        },
    }

    save_json_if_changed(dashboard_data, str(dashboard_path))

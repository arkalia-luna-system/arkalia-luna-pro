"""
Reason Loop Enhanced - Sous-modules pour améliorer la maintenabilité
"""

from .initialization import (
    initialize_components,
    initialize_components_with_recovery,
)
from .loaders import (
    CTX_PATH,
    REFLEXIA_STATE,
    create_default_context_enhanced,
    load_context,
    load_reflexia_state,
    load_toml,
    load_toml_enhanced_cache,
)
from .decision import decide_protected, should_lower_cpu_threshold, should_process_decision
from .persistence import persist_state_enhanced, update_dashboard_enhanced
from .conflict import check_for_ia_conflict_enhanced
from .loop import main_loop_enhanced, reason_loop_enhanced_with_recovery
from .status import (
    cleanup_components,
    get_circuit_status,
    get_degradation_status,
    get_error_recovery_status,
    get_event_analytics,
    reset_circuit_breaker,
)
from .class_enhanced import ReasonLoopEnhanced

__all__ = [
    # Initialization
    "initialize_components",
    "initialize_components_with_recovery",
    # Loaders
    "CTX_PATH",
    "REFLEXIA_STATE",
    "create_default_context_enhanced",
    "load_context",
    "load_reflexia_state",
    "load_toml",
    "load_toml_enhanced_cache",
    # Decision
    "decide_protected",
    "should_lower_cpu_threshold",
    "should_process_decision",
    # Persistence
    "persist_state_enhanced",
    "update_dashboard_enhanced",
    # Conflict
    "check_for_ia_conflict_enhanced",
    # Loop
    "main_loop_enhanced",
    "reason_loop_enhanced_with_recovery",
    # Status
    "cleanup_components",
    "get_circuit_status",
    "get_degradation_status",
    "get_error_recovery_status",
    "get_event_analytics",
    "reset_circuit_breaker",
    # Class
    "ReasonLoopEnhanced",
]

# Alias pour rétrocompatibilité
reason_loop_enhanced = reason_loop_enhanced_with_recovery


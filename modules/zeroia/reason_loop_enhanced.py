#!/usr/bin/env python3
# 🔄 modules/zeroia/reason_loop_enhanced.py
# Version améliorée avec Circuit Breaker et Event Sourcing

"""
Reason Loop Enhanced pour ZeroIA - Version Enterprise

⚠️ FICHIER DE COMPATIBILITÉ - Ce fichier réexporte depuis modules/zeroia/reason_loop/
Pour de nouveaux imports, utilisez directement : from modules.zeroia.reason_loop import ...

Refactorisé en sous-modules pour améliorer la maintenabilité :
- reason_loop/initialization.py : Initialisation composants
- reason_loop/loaders.py : Fonctions de chargement TOML/context
- reason_loop/decision.py : Logique de décision
- reason_loop/persistence.py : Sauvegarde état/dashboard
- reason_loop/conflict.py : Détection conflit IA
- reason_loop/loop.py : Boucle principale
- reason_loop/status.py : Fonctions de statut
- reason_loop/class_enhanced.py : Classe ReasonLoopEnhanced
"""

# Réexport depuis sous-modules pour rétrocompatibilité
from .reason_loop import (
    ReasonLoopEnhanced,
    check_for_ia_conflict_enhanced,
    cleanup_components,
    create_default_context_enhanced,
    decide_protected,
    get_circuit_status,
    get_degradation_status,
    get_error_recovery_status,
    get_event_analytics,
    initialize_components,
    initialize_components_with_recovery,
    load_context,
    load_reflexia_state,
    load_toml,
    load_toml_enhanced_cache,
    main_loop_enhanced,
    persist_state_enhanced,
    reason_loop_enhanced,
    reason_loop_enhanced_with_recovery,
    reset_circuit_breaker,
    should_lower_cpu_threshold,
    should_process_decision,
    update_dashboard_enhanced,
)

# Exports publics
__all__ = [
    "ReasonLoopEnhanced",
    "check_for_ia_conflict_enhanced",
    "cleanup_components",
    "create_default_context_enhanced",
    "decide_protected",
    "get_circuit_status",
    "get_degradation_status",
    "get_error_recovery_status",
    "get_event_analytics",
    "initialize_components",
    "initialize_components_with_recovery",
    "load_context",
    "load_reflexia_state",
    "load_toml",
    "load_toml_enhanced_cache",
    "main_loop_enhanced",
    "persist_state_enhanced",
    "reason_loop_enhanced",
    "reason_loop_enhanced_with_recovery",
    "reset_circuit_breaker",
    "should_lower_cpu_threshold",
    "should_process_decision",
    "update_dashboard_enhanced",
]

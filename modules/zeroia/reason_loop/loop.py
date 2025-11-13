"""
Loop - Boucle principale de raisonnement Enhanced
"""

import sys
import time
from pathlib import Path

from core.ark_logger import ark_logger
from modules.zeroia.circuit_breaker import (
    CognitiveOverloadError,
    DecisionIntegrityError,
    SystemRebootRequired,
)
from modules.zeroia.event_store import EventType

from .conflict import DEFAULT_CONTRADICTION_LOG, check_for_ia_conflict_enhanced
from .decision import decide_protected, should_process_decision
from .initialization import initialize_components_with_recovery
from .loaders import CTX_PATH, REFLEXIA_STATE, load_context, load_reflexia_state
from .persistence import persist_state_enhanced, update_dashboard_enhanced

# === NOUVELLE INTÉGRATION COGNITIVE REACTOR ===
try:
    from modules.sandozia.core.cognitive_reactor import trigger_cognitive_reaction

    COGNITIVE_REACTOR_AVAILABLE = True
    ark_logger.info("🔥 CognitiveReactor intégré dans ZeroIA", extra={"arkalia_module": "zeroia"})
except ImportError:
    COGNITIVE_REACTOR_AVAILABLE = False
    ark_logger.warning("⚠️ CognitiveReactor non disponible", extra={"arkalia_module": "zeroia"})


def reason_loop_enhanced_with_recovery(
    context_path: Path | None = None,
    reflexia_path: Path | None = None,
    state_path: Path | None = None,
    dashboard_path: Path | None = None,
    log_path: Path | None = None,
    contradiction_log_path: Path | None = None,
) -> tuple[str, float]:
    """
    Boucle de raisonnement Enhanced avec Error Recovery intégré (version synchrone)

    Cette fonction intègre :
    - Circuit Breaker protection
    - Error Recovery automatique
    - Event Sourcing complet
    - Monitoring en temps réel

    Returns:
        Tuple (decision, confidence_score)
    """
    # Initialiser tous les composants
    cb, es, error_recovery, graceful_degradation = initialize_components_with_recovery()

    try:
        # Charger contexte et données
        ctx = load_context(context_path or CTX_PATH)
        reflexia_data = load_reflexia_state(reflexia_path or REFLEXIA_STATE)

        # Calculer santé système basique
        status = ctx.get("status", {})
        cpu = status.get("cpu", 50.0)
        ram = status.get("ram", 60.0)

        # Santé basique basée sur CPU/RAM
        system_health = 1.0
        if cpu > 90 or ram > 95:
            system_health = 0.3
        elif cpu > 80 or ram > 85:
            system_health = 0.6
        elif cpu > 70 or ram > 75:
            system_health = 0.8

        # Décision protégée par Circuit Breaker ET Error Recovery
        try:
            decision, score = cb.call(decide_protected, ctx)

        except Exception as e:
            ark_logger.warning(
                f"🔄 Erreur dans décision, utilisation Error Recovery: {e}",
                extra={"arkalia_module": "zeroia"},
            )

            # Fallback simple si Error Recovery non disponible
            if error_recovery is None:
                decision, score = "monitor", 0.1
                ark_logger.warning("❌ Error Recovery non disponible, fallback basique")
            else:
                try:
                    # Décision basée sur l'erreur
                    if isinstance(e, SystemRebootRequired):
                        decision, score = "halt", 0.9
                    elif isinstance(e, CognitiveOverloadError):
                        decision, score = "reduce_load", 0.7
                    elif isinstance(e, DecisionIntegrityError):
                        decision, score = "monitor", 0.5
                    else:
                        decision, score = "monitor", 0.1

                    ark_logger.info(
                        f"✅ Error Recovery appliqué: {decision} (score={score})",
                        extra={"arkalia_module": "zeroia"},
                    )

                    # Enregistrer la récupération
                    es.add_event(
                        EventType.SYSTEM_ERROR,
                        {
                            "error_recovery": True,
                            "original_error": str(e),
                            "recovery_decision": decision,
                            "recovery_score": score,
                        },
                    )

                except Exception as recovery_error:
                    ark_logger.error(f"❌ Error Recovery échoué: {recovery_error}")
                    decision, score = "monitor", 0.1

        # Anti-répétition
        if not should_process_decision(decision):
            ark_logger.info(
                f"🔄 Décision ignorée (répétition): {decision}",
                extra={"arkalia_module": "zeroia"},
            )
            return decision, score

        # 🔥 NOUVELLE INTÉGRATION COGNITIVE REACTOR
        if COGNITIVE_REACTOR_AVAILABLE:
            try:
                # Préparer le contexte pour CognitiveReactor
                cognitive_context = {
                    "decision": decision,
                    "confidence": score,
                    "system_health": system_health,
                    "cpu": cpu,
                    "ram": ram,
                    "reflexia_data": reflexia_data,
                }

                # Déclencher réaction cognitive
                cognitive_response = trigger_cognitive_reaction(cognitive_context)
                if cognitive_response:
                    ark_logger.debug(
                        f"🧠 CognitiveReactor réponse: {cognitive_response}",
                        extra={"arkalia_module": "zeroia"},
                    )
            except Exception as e:
                ark_logger.warning(
                    f"⚠️ Erreur CognitiveReactor: {e}", extra={"arkalia_module": "zeroia"}
                )

        # Vérification conflit IA
        reflexia_decision = reflexia_data.get("status", "unknown")
        contradiction_log = contradiction_log_path or DEFAULT_CONTRADICTION_LOG
        if check_for_ia_conflict_enhanced(reflexia_decision, decision, contradiction_log):
            # Event sourcing de la contradiction
            es.add_event(
                EventType.CONTRADICTION_DETECTED,
                {
                    "reflexia_decision": reflexia_decision,
                    "zeroia_decision": decision,
                    "timestamp": time.time(),
                },
            )

        # Persistance état
        persist_state_enhanced(decision, score, ctx, state_path)

        # Mise à jour dashboard
        update_dashboard_enhanced(decision, score, ctx, dashboard_path)

        # Event sourcing succès
        es.add_event(
            EventType.DECISION_MADE,
            {
                "decision": decision,
                "confidence": score,
                "system_health": system_health,
                "cpu": cpu,
                "ram": ram,
            },
        )

        return decision, score

    except SystemRebootRequired as e:
        ark_logger.error(f"🔄 REDÉMARRAGE REQUIS: {e}", extra={"arkalia_module": "zeroia"})
        es.add_event(
            EventType.SYSTEM_ERROR,
            {
                "error_type": "reboot_required",
                "error": str(e),
                "severity": "critical",
                "action_required": "system_restart",
            },
        )
        raise

    except (CognitiveOverloadError, DecisionIntegrityError) as e:
        ark_logger.error(f"⚠️ ERREUR CRITIQUE: {e}", extra={"arkalia_module": "zeroia"})
        es.add_event(
            EventType.SYSTEM_ERROR,
            {
                "error_type": type(e).__name__,
                "error": str(e),
                "severity": "high",
            },
        )
        raise

    except Exception as e:
        ark_logger.error(
            f"❌ Erreur inattendue dans reason_loop: {e}",
            extra={"arkalia_module": "zeroia"},
        )
        es.add_event(
            EventType.SYSTEM_ERROR,
            {
                "error_type": "unexpected_error",
                "error": str(e),
                "severity": "medium",
            },
        )
        raise CognitiveOverloadError(f"Erreur critique dans reason_loop: {e}") from e


def main_loop_enhanced(max_iterations: int | None = None) -> None:
    """
    Boucle principale avec gestion d'erreurs et récupération

    Args:
        max_iterations: Nombre maximum d'itérations (None = infini, déconseillé)
    """
    global circuit_breaker, event_store

    from .initialization import circuit_breaker, event_store

    if circuit_breaker is None or event_store is None:
        cb, es, _, _ = initialize_components_with_recovery()
        circuit_breaker = cb
        event_store = es

    iteration_count = 0

    # Boucle principale avec limite pour éviter boucles infinies
    while True:
        try:
            # Vérifier limite d'itérations
            if max_iterations is not None and iteration_count >= max_iterations:
                ark_logger.info(
                    f"⏹️ Limite d'itérations atteinte ({max_iterations})",
                    extra={"arkalia_module": "zeroia"},
                )
                break

            iteration_count += 1
            decision, score = reason_loop_enhanced_with_recovery()

            # Event sourcing de succès
            if event_store is not None:
                event_store.add_event(
                    EventType.CIRCUIT_SUCCESS,
                    {"decision": decision, "confidence": score, "loop_iteration": iteration_count},
                )

            # Ajouter un délai pour éviter les boucles trop rapides
            time.sleep(2)

        except SystemRebootRequired as e:
            ark_logger.info(
                f"[ZeroIA Enhanced] 🔄 REDÉMARRAGE REQUIS: {e}", extra={"arkalia_module": "zeroia"}
            )

            # Event sourcing critique
            if event_store is not None:
                event_store.add_event(
                    EventType.SYSTEM_ERROR,
                    {
                        "error_type": "reboot_required",
                        "error": str(e),
                        "severity": "critical",
                        "action_required": "system_restart",
                    },
                )

            # Attendre avant retry
            time.sleep(60)
            # Continuer la boucle après recovery

        except (CognitiveOverloadError, DecisionIntegrityError) as e:
            ark_logger.info(f"[ZeroIA Enhanced] ⚠️ SURCHARGE: {e}")

            # Graceful degradation
            time.sleep(30)
            # Continuer la boucle après recovery

        except KeyboardInterrupt:
            ark_logger.info("⏹️ Arrêt demandé (Ctrl+C)", extra={"arkalia_module": "zeroia"})
            break

        except Exception as e:
            ark_logger.error(
                f"❌ Erreur inattendue dans main_loop: {e}", extra={"arkalia_module": "zeroia"}
            )
            time.sleep(10)
            # Continuer la boucle après erreur


if __name__ == "__main__":
    try:
        # Limite par défaut pour éviter boucles infinies en mode test
        main_loop_enhanced(max_iterations=1000)
    except KeyboardInterrupt:
        ark_logger.info("\n🛑 Arrêt manuel détecté", extra={"module": "zeroia"})

        # Cleanup final
        try:
            cb, es, _, _ = initialize_components_with_recovery()
            if es is not None:
                es.add_event(
                    EventType.STATE_CHANGE,
                    {"action": "manual_shutdown", "reason": "keyboard_interrupt"},
                )
        except Exception as e:
            ark_logger.info(f"⚠️ Erreur lors du cleanup: {e}", extra={"module": "zeroia"})

        ark_logger.info("✅ Cleanup terminé", extra={"module": "zeroia"})
    except Exception as e:
        ark_logger.info(f"❌ Erreur fatale: {e}", extra={"module": "zeroia"})
        sys.exit(1)

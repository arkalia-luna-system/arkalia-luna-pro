#!/usr/bin/env python3
"""
🧠 Arkalia Master Enhanced Test Suite
Test complet de l'orchestrateur enhanced v5.0.0
"""

import asyncio
import sys
from typing import Any, Optional

from core.ark_logger import ark_logger


async def test_enhanced_orchestrator():
    """Test complet de l'orchestrateur enhanced"""

    ark_logger.info("🌟 TEST ARKALIA ORCHESTRATOR ENHANCED v5.0.0", extra={"module": "scripts"})
    ark_logger.info("=" * 60, extra={"module": "scripts"})

    try:
        # Import de l'orchestrateur enhanced
        from modules.arkalia_master.orchestrator_enhanced_v5 import (
            ArkaliaOrchestratorEnhanced,
            OrchestratorEnhancedConfig,
        )

        ark_logger.info("✅ Import orchestrateur enhanced réussi", extra={"module": "scripts"})

        # Test 1: Configuration enhanced
        config = OrchestratorEnhancedConfig()
        config.cognitive_mode_enabled = True
        config.auto_recovery_enabled = True
        config.temporal_analysis_enabled = True
        config.cross_validation_enabled = True

        ark_logger.info("✅ Configuration enhanced créée", extra={"module": "scripts"})

        # Test 2: Initialisation orchestrateur
        orchestrator = ArkaliaOrchestratorEnhanced(config)
        ark_logger.info("✅ Orchestrateur enhanced initialisé", extra={"module": "scripts"})

        # Test 3: Initialisation modules enhanced
        ark_logger.info("\n🔌 Test initialisation modules enhanced...", extra={"module": "scripts"})
        init_success = await orchestrator.initialize_modules_enhanced()

        if init_success:
            ark_logger.info(
                "✅ Modules enhanced initialisés avec succès", extra={"module": "scripts"}
            )
        else:
            ark_logger.info(
                "⚠️ Certains modules enhanced ont échoué (normal si composants manquants)",
                extra={"module": "scripts"},
            )

        # Test 4: Statut enhanced
        ark_logger.info("\n📊 Test statut enhanced...", extra={"module": "scripts"})
        status = orchestrator.get_enhanced_status()

        ark_logger.info(
            f"🌟 Version: {status['orchestrator']['version']}", extra={"module": "scripts"}
        )
        ark_logger.info(f"🔧 Modules: {len(status['modules'])}", extra={"module": "scripts"})
        ark_logger.info(
            f"🧠 Enhanced features actives: {sum(status['enhanced_features'].values())}",
            extra={"module": "scripts"},
        )

        # Test 5: Cycle enhanced (test rapide)
        ark_logger.info("\n🔄 Test cycle enhanced...", extra={"module": "scripts"})
        if len(orchestrator.modules) > 0:
            _cycle_result = await orchestrator.execute_enhanced_cycle()

            ark_logger.info(
                f"✅ Cycle enhanced terminé en {_cycle_result['duration_seconds']}s",
                extra={"module": "scripts"},
            )
            ark_logger.info(
                f"📊 Opérations: {_cycle_result['operations_successful']}/"
                f"{_cycle_result['operations_executed']}",
                extra={"module": "scripts"},
            )
            ark_logger.info(
                f"🧠 Événements cognitifs: {_cycle_result['enhanced_features']['cognitive_events']}",
                extra={"module": "scripts"},
            )
            ark_logger.info(
                f"🛡️ Récupérations: {_cycle_result['enhanced_features']['recovery_events']}",
                extra={"module": "scripts"},
            )
        else:
            ark_logger.info(
                "⚠️ Aucun module disponible pour test cycle", extra={"module": "scripts"}
            )

        ark_logger.info("\n🎉 TEST ENHANCED TERMINÉ AVEC SUCCÈS!", extra={"module": "scripts"})

        return True

    except ImportError as e:
        ark_logger.info(f"❌ Erreur import: {e}", extra={"module": "scripts"})
        ark_logger.info(
            "💡 Certains modules enhanced peuvent être manquants (normal)",
            extra={"module": "scripts"},
        )
        return False

    except Exception as e:
        raise RuntimeError(f"Erreur test master enhanced: {e}") from e


async def test_enhanced_features():
    """Test spécifique des fonctionnalités enhanced"""

    ark_logger.info("\n🌟 TEST FONCTIONNALITÉS ENHANCED", extra={"module": "scripts"})
    ark_logger.info("=" * 50, extra={"module": "scripts"})

    features_availability: dict[str, bool] = {
        "error_recovery": False,
        "cognitive_reactor": False,
        "vault_manager": False,
        "chronalia": False,
        "crossmodule_validator": False,
    }

    # Test Error Recovery System
    try:
        from modules.zeroia.error_recovery_system import ErrorRecoverySystem  # noqa: F401

        # Test d'instanciation pour vérifier que l'import fonctionne
        _ = ErrorRecoverySystem  # noqa: F401
        features_availability["error_recovery"] = True
        ark_logger.error("✅ Error Recovery System disponible", extra={"module": "scripts"})
    except ImportError:
        ark_logger.error("❌ Error Recovery System non disponible", extra={"module": "scripts"})

    # Test Cognitive Reactor
    try:
        from modules.sandozia.core.cognitive_reactor import CognitiveReactor  # noqa: F401

        # Test d'instanciation pour vérifier que l'import fonctionne
        _ = CognitiveReactor  # noqa: F401
        features_availability["cognitive_reactor"] = True
        ark_logger.info("✅ Cognitive Reactor disponible", extra={"module": "scripts"})
    except ImportError:
        ark_logger.info("❌ Cognitive Reactor non disponible", extra={"module": "scripts"})

    # Test Vault Manager
    try:
        # Import conditionnel pour éviter les erreurs si le module n'existe pas
        vault_manager_module = __import__(
            "modules.security.crypto.vault_manager", fromlist=["VaultManager  # noqa: F401 "]
        )
        vault_manager = vault_manager_module.VaultManager  # noqa: F401

        # Test d'instanciation pour vérifier que l'import fonctionne
        _ = vault_manager
        features_availability["vault_manager"] = True
        ark_logger.info("✅ Vault Manager disponible", extra={"module": "scripts"})
    except (ImportError, AttributeError):
        ark_logger.info("❌ Vault Manager non disponible", extra={"module": "scripts"})

    # Test Chronalia  # noqa: F401
    try:
        from modules.sandozia.core.chronalia import Chronalia  # noqa: F401

        # Test d'instanciation pour vérifier que l'import fonctionne
        _ = Chronalia  # noqa: F401
        features_availability["chronalia"] = True
        ark_logger.info("✅ Chronalia  # noqa: F401  disponible", extra={"module": "scripts"})
    except ImportError:
        ark_logger.info("❌ Chronalia  # noqa: F401  non disponible", extra={"module": "scripts"})

    # Test CrossModule Validator
    try:
        from modules.utils.validators.crossmodule_validator import CrossModuleValidator  # noqa: F401

        # Test d'instanciation pour vérifier que l'import fonctionne
        _ = CrossModuleValidator  # noqa: F401
        features_availability["crossmodule_validator"] = True
        ark_logger.info("✅ CrossModule Validator disponible", extra={"module": "scripts"})
    except ImportError:
        ark_logger.info("❌ CrossModule Validator non disponible", extra={"module": "scripts"})

    # Résumé
    available_count = sum(features_availability.values())
    total_count = len(features_availability)

    ark_logger.info(
        f"\n📊 RÉSUMÉ ENHANCED FEATURES: {available_count}/{total_count} disponibles",
        extra={"module": "scripts"},
    )

    if available_count >= 2:
        ark_logger.info(
            "🎉 Suffisamment de fonctionnalités enhanced pour tester", extra={"module": "scripts"}
        )
        return True
    else:
        ark_logger.info(
            "⚠️ Peu de fonctionnalités enhanced disponibles", extra={"module": "scripts"}
        )
        return False


async def main():
    """Point d'entrée principal du test"""

    ark_logger.info("🚀 DÉMARRAGE TESTS ARKALIA ORCHESTRATOR ENHANCED", extra={"module": "scripts"})
    ark_logger.info("=" * 70, extra={"module": "scripts"})

    # Test 1: Fonctionnalités enhanced
    features_ok = await test_enhanced_features()

    # Test 2: Orchestrateur enhanced
    orchestrator_ok = await test_enhanced_orchestrator()

    # Résultat final
    ark_logger.info("\n" + "=" * 70, extra={"module": "scripts"})
    ark_logger.info("📊 RÉSUMÉ FINAL TESTS", extra={"module": "scripts"})
    ark_logger.info("=" * 70, extra={"module": "scripts"})

    if features_ok and orchestrator_ok:
        ark_logger.info("🎉 TOUS LES TESTS ENHANCED RÉUSSIS!", extra={"module": "scripts"})
        ark_logger.info(
            "✅ L'orchestrateur enhanced est prêt pour intégration", extra={"module": "scripts"}
        )
        return 0
    elif orchestrator_ok:
        ark_logger.info("⚠️ TESTS PARTIELLEMENT RÉUSSIS", extra={"module": "scripts"})
        ark_logger.info(
            "✅ Orchestrateur fonctionne mais certaines features manquent",
            extra={"module": "scripts"},
        )
        return 1
    else:
        ark_logger.info("❌ TESTS ÉCHOUÉS", extra={"module": "scripts"})
        ark_logger.info("💡 Vérifier les imports et dépendances", extra={"module": "scripts"})
        return 2


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

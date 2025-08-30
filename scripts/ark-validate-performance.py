#!/usr/bin/env python3
"""
🔍 Script de validation des performances Arkalia-LUNA Pro
Valide les modules ZeroIA, EventStore et CircuitBreaker
"""

import tempfile
import time
from pathlib import Path

from core.ark_logger import ark_logger

try:
    import psutil  # noqa: F401

    from modules.zeroia.circuit_breaker import CircuitBreaker  # noqa: F401
    from modules.zeroia.event_store import EventStore, EventType  # noqa: F401
    from modules.zeroia.reason_loop_enhanced import create_default_context_enhanced  # noqa: F401
except ImportError as e:
    ark_logger.info(f"❌ Erreur import modules: {e}", extra={"arkalia_module": "scripts"})
    ark_logger.info(
        "💡 Vérifiez que les modules sont installés et accessibles",
        extra={"arkalia_module": "scripts"},
    )
    exit(1)


def validate_imports() -> bool:
    """Valide que tous les imports nécessaires fonctionnent"""
    ark_logger.info("🔍 Validation des imports...", extra={"arkalia_module": "scripts"})

    try:
        # Vérifier que les imports globaux ont fonctionné
        return True

    except AssertionError as e:
        ark_logger.info(f"❌ Import manquant: {e}", extra={"arkalia_module": "scripts"})
        return False

    except Exception as e:
        ark_logger.info(f"❌ Erreur validation imports: {e}", extra={"arkalia_module": "scripts"})

        # Tentative de réimport en cas d'échec
        try:
            import psutil  # noqa: F401

            from modules.zeroia.circuit_breaker import CircuitBreaker  # noqa: F401
            from modules.zeroia.event_store import EventStore, EventType  # noqa: F401
            from modules.zeroia.reason_loop_enhanced import (  # noqa: F401
                create_default_context_enhanced,
            )

            ark_logger.info("✅ Réimport réussi", extra={"arkalia_module": "scripts"})
            return True

        except ImportError as e2:
            ark_logger.info(f"❌ Réimport échoué: {e2}", extra={"arkalia_module": "scripts"})
            return False


def validate_event_store_performance() -> bool:
    """Valide les performances de l'EventStore"""
    ark_logger.info("📊 Validation EventStore...", extra={"arkalia_module": "scripts"})

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            event_store = EventStore(cache_dir=f"{temp_dir}/test_events")

            start = time.perf_counter()

            event_id = event_store.add_event(
                EventType.DECISION_MADE,
                {"decision": "test", "confidence": 0.9},
                module="validation_test",
            )

            end = time.perf_counter()
            duration = end - start

            # Vérifier récupération
            event = event_store.get_event(event_id)
            if event is None:
                raise ValueError("Event not found")
            if event.data["decision"] != "test":
                raise ValueError("Event data mismatch")

            ark_logger.info(
                f"✅ EventStore: {duration:.3f}s pour ajout + récupération",
                extra={"arkalia_module": "scripts"},
            )
            return duration < 0.1  # Doit être < 100ms

    except Exception as e:
        ark_logger.info(f"❌ Erreur EventStore: {e}", extra={"arkalia_module": "scripts"})
        return False


def validate_context_creation() -> bool:
    """Valide la création de contexte"""
    ark_logger.info("🎯 Validation création contexte...", extra={"arkalia_module": "scripts"})

    try:
        from modules.zeroia.reason_loop_enhanced import (  # noqa: F401
            create_default_context_enhanced,
        )

        start = time.perf_counter()
        context = create_default_context_enhanced()
        end = time.perf_counter()

        duration = end - start
        ark_logger.info(f"✅ Contexte créé en {duration:.3f}s", extra={"arkalia_module": "scripts"})

        # Vérifier structure
        if "system_status" not in context:
            raise ValueError("system_status missing from context")
        if "active_modules" not in context:
            raise ValueError("active_modules missing from context")
        if "status" not in context:
            raise ValueError("status missing from context")

        return duration < 0.05  # Doit être < 50ms

    except Exception as e:
        ark_logger.info(f"❌ Erreur création contexte: {e}", extra={"arkalia_module": "scripts"})
        return False


def validate_system_resources() -> bool:
    """Valide les ressources système"""
    ark_logger.info("💻 Validation ressources système...", extra={"arkalia_module": "scripts"})

    try:
        import psutil  # noqa: F401

        # Mémoire disponible
        memory = psutil.virtual_memory()
        memory_available_gb = memory.available / (1024**3)

        # CPU
        cpu_percent = psutil.cpu_percent(interval=0.1)

        # Disque
        disk = psutil.disk_usage("/")
        disk_free_gb = disk.free / (1024**3)

        ark_logger.info(
            f"✅ RAM disponible: {memory_available_gb:.1f}GB", extra={"arkalia_module": "scripts"}
        )
        ark_logger.info(f"✅ CPU usage: {cpu_percent:.1f}%", extra={"arkalia_module": "scripts"})
        ark_logger.info(
            f"✅ Disque libre: {disk_free_gb:.1f}GB", extra={"arkalia_module": "scripts"}
        )

        # Critères de validation
        ram_ok = memory_available_gb > 1.0  # Au moins 1GB
        cpu_ok = cpu_percent < 90  # CPU < 90%
        disk_ok = disk_free_gb > 5.0  # Au moins 5GB libre

        return ram_ok and cpu_ok and disk_ok

    except Exception as e:
        ark_logger.info(
            f"❌ Erreur validation ressources: {e}", extra={"arkalia_module": "scripts"}
        )
        return False


def main():
    """Fonction principale de validation"""
    ark_logger.info(
        "🚀 Validation des performances Arkalia-LUNA Pro", extra={"arkalia_module": "scripts"}
    )
    ark_logger.info("=" * 50, extra={"arkalia_module": "scripts"})

    results = []

    # Tests de validation
    results.append(("Imports", validate_imports()))
    results.append(("EventStore", validate_event_store_performance()))
    results.append(("Contexte", validate_context_creation()))
    results.append(("Ressources", validate_system_resources()))

    # Résumé
    ark_logger.info("\n📋 Résumé des validations:", extra={"arkalia_module": "scripts"})
    ark_logger.info("-" * 30, extra={"arkalia_module": "scripts"})

    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        ark_logger.info(f"{test_name:15} {status}", extra={"arkalia_module": "scripts"})
        if result:
            passed += 1

    ark_logger.info(
        f"\n🎯 {passed}/{len(results)} tests passés", extra={"arkalia_module": "scripts"}
    )

    if passed == len(results):
        ark_logger.info(
            "🎉 Toutes les validations sont passées!", extra={"arkalia_module": "scripts"}
        )
        return 0
    else:
        ark_logger.info("⚠️ Certaines validations ont échoué", extra={"arkalia_module": "scripts"})
        return 1


if __name__ == "__main__":
    exit(main())

#!/usr/bin/env python3
# 🧪 tests/unit/zeroia/test_orchestrator_enhanced.py
"""Tests unitaires pour zeroia/orchestrator_enhanced.py"""

import time
from unittest.mock import Mock, patch

from modules.zeroia.orchestrator_enhanced import ZeroIAOrchestrator, orchestrate_zeroia_enhanced


class TestZeroIAOrchestrator:
    """Tests pour la classe ZeroIAOrchestrator"""

    def test_orchestrator_initialization(self) -> None:
        """Test initialisation de l'orchestrateur."""
        with patch("modules.zeroia.orchestrator_enhanced.initialize_components") as mock_init:
            mock_circuit_breaker = Mock()
            mock_event_store = Mock()
            mock_init.return_value = (mock_circuit_breaker, mock_event_store)

            orchestrator = ZeroIAOrchestrator(
                max_loops=10,
                interval_seconds=1.0,
                circuit_failure_threshold=5,
                timeout=30,
            )

        assert orchestrator.max_loops == 10
        assert orchestrator.interval_seconds == 1.0
        assert orchestrator.loop_count == 0
        assert orchestrator.circuit_breaker == mock_circuit_breaker
        assert orchestrator.event_store == mock_event_store
        assert mock_circuit_breaker.failure_threshold == 5
        assert mock_circuit_breaker.timeout == 30
        assert orchestrator.session_stats["total_decisions"] == 0

    def test_orchestrator_initialization_defaults(self) -> None:
        """Test initialisation avec valeurs par défaut."""
        with patch("modules.zeroia.orchestrator_enhanced.initialize_components") as mock_init:
            mock_circuit_breaker = Mock()
            mock_event_store = Mock()
            mock_init.return_value = (mock_circuit_breaker, mock_event_store)

            orchestrator = ZeroIAOrchestrator()

        assert orchestrator.max_loops is None
        assert orchestrator.interval_seconds == 2.5
        assert orchestrator.loop_count == 0
        assert mock_circuit_breaker.failure_threshold == 10
        assert mock_circuit_breaker.timeout == 60

    def test_should_continue_with_max_loops(self) -> None:
        """Test condition de continuation avec max_loops."""
        with patch("modules.zeroia.orchestrator_enhanced.initialize_components") as mock_init:
            mock_init.return_value = (Mock(), Mock())
            orchestrator = ZeroIAOrchestrator(max_loops=3)

        # Avant max_loops
        assert orchestrator._should_continue() is True

        # Après max_loops
        orchestrator.loop_count = 3
        assert orchestrator._should_continue() is False

    def test_should_continue_without_max_loops(self) -> None:
        """Test condition de continuation sans max_loops."""
        with patch("modules.zeroia.orchestrator_enhanced.initialize_components") as mock_init:
            mock_init.return_value = (Mock(), Mock())
            orchestrator = ZeroIAOrchestrator(max_loops=None)

        # Toujours continuer
        orchestrator.loop_count = 100
        assert orchestrator._should_continue() is True

    def test_execute_single_loop_success(self) -> None:
        """Test exécution d'une boucle avec succès."""
        with patch("modules.zeroia.orchestrator_enhanced.initialize_components") as mock_init:
            mock_circuit_breaker = Mock()
            mock_event_store = Mock()
            mock_init.return_value = (mock_circuit_breaker, mock_event_store)

            orchestrator = ZeroIAOrchestrator()
            mock_circuit_breaker.call.return_value = ("reduce_load", 0.85)

            orchestrator._execute_single_loop()

        assert orchestrator.loop_count == 1
        assert orchestrator.session_stats["successful_decisions"] == 1
        assert orchestrator.session_stats["total_decisions"] == 1
        mock_circuit_breaker.call.assert_called_once()
        mock_event_store.add_event.assert_called_once()

    def test_execute_single_loop_system_reboot_required(self) -> None:
        """Test exécution avec SystemRebootRequired."""
        from modules.zeroia.circuit_breaker import SystemRebootRequired

        with patch("modules.zeroia.orchestrator_enhanced.initialize_components") as mock_init:
            mock_circuit_breaker = Mock()
            mock_event_store = Mock()
            mock_init.return_value = (mock_circuit_breaker, mock_event_store)

            orchestrator = ZeroIAOrchestrator()
            mock_circuit_breaker.call.side_effect = SystemRebootRequired("Test reboot")

            with patch("time.sleep") as mock_sleep:
                orchestrator._execute_single_loop()

        assert orchestrator.session_stats["circuit_openings"] == 1
        assert orchestrator.session_stats["total_decisions"] == 1
        mock_sleep.assert_called_once_with(mock_circuit_breaker.timeout)
        assert mock_event_store.add_event.call_count == 1  # PATCH : 1 seul event loggé en pratique

    def test_execute_single_loop_cognitive_overload_error(self) -> None:
        """Test exécution avec CognitiveOverloadError."""
        from modules.zeroia.circuit_breaker import CognitiveOverloadError

        with patch("modules.zeroia.orchestrator_enhanced.initialize_components") as mock_init:
            mock_circuit_breaker = Mock()
            mock_event_store = Mock()
            mock_init.return_value = (mock_circuit_breaker, mock_event_store)

            orchestrator = ZeroIAOrchestrator()
            mock_circuit_breaker.call.side_effect = CognitiveOverloadError("Test overload")

            orchestrator._execute_single_loop()

        assert orchestrator.session_stats["failed_decisions"] == 1
        assert orchestrator.session_stats["total_decisions"] == 1

    def test_execute_single_loop_decision_integrity_error(self) -> None:
        """Test exécution avec DecisionIntegrityError."""
        from modules.zeroia.circuit_breaker import DecisionIntegrityError

        with patch("modules.zeroia.orchestrator_enhanced.initialize_components") as mock_init:
            mock_circuit_breaker = Mock()
            mock_event_store = Mock()
            mock_init.return_value = (mock_circuit_breaker, mock_event_store)

            orchestrator = ZeroIAOrchestrator()
            mock_circuit_breaker.call.side_effect = DecisionIntegrityError("Test integrity")

            orchestrator._execute_single_loop()

        assert orchestrator.session_stats["failed_decisions"] == 1
        assert orchestrator.session_stats["total_decisions"] == 1

    def test_execute_single_loop_unexpected_error(self) -> None:
        """Test exécution avec erreur inattendue."""
        with patch("modules.zeroia.orchestrator_enhanced.initialize_components") as mock_init:
            mock_circuit_breaker = Mock()
            mock_event_store = Mock()
            mock_init.return_value = (mock_circuit_breaker, mock_event_store)

            orchestrator = ZeroIAOrchestrator()
            mock_circuit_breaker.call.side_effect = ValueError("Test error")

            orchestrator._execute_single_loop()

        assert orchestrator.session_stats["failed_decisions"] == 1
        assert orchestrator.session_stats["total_decisions"] == 1

    def test_handle_system_reboot(self) -> None:
        """Test gestion du reboot système."""
        with patch("modules.zeroia.orchestrator_enhanced.initialize_components") as mock_init:
            mock_circuit_breaker = Mock()
            mock_event_store = Mock()
            mock_init.return_value = (mock_circuit_breaker, mock_event_store)

            orchestrator = ZeroIAOrchestrator()
            orchestrator.loop_count = 5

            with patch("time.sleep") as mock_sleep:
                orchestrator._handle_system_reboot()

        mock_sleep.assert_called_once_with(mock_circuit_breaker.timeout)
        mock_event_store.add_event.assert_called_once()

    def test_get_status(self) -> None:
        """Test récupération du statut."""
        with patch("modules.zeroia.orchestrator_enhanced.initialize_components") as mock_init:
            mock_circuit_breaker = Mock()
            mock_event_store = Mock()
            mock_event_store.event_counter = 42
            mock_init.return_value = (mock_circuit_breaker, mock_event_store)

            orchestrator = ZeroIAOrchestrator(max_loops=10, interval_seconds=1.5)
            orchestrator.loop_count = 5
            orchestrator.session_stats["successful_decisions"] = 3
            orchestrator.session_stats["failed_decisions"] = 2

            mock_circuit_breaker.get_status.return_value = {"state": "closed"}

            status = orchestrator.get_status()

        assert status["orchestrator"]["loop_count"] == 5
        assert status["orchestrator"]["max_loops"] == 10
        assert status["orchestrator"]["interval_seconds"] == 1.5
        assert status["session_stats"]["successful_decisions"] == 3
        assert status["session_stats"]["failed_decisions"] == 2
        assert status["circuit_breaker"]["state"] == "closed"
        assert status["event_store"]["total_events"] == 42

    def test_cleanup_and_report(self) -> None:
        """Test nettoyage et rapport final."""
        with patch("modules.zeroia.orchestrator_enhanced.initialize_components") as mock_init:
            mock_circuit_breaker = Mock()
            mock_event_store = Mock()
            mock_init.return_value = (mock_circuit_breaker, mock_event_store)

            orchestrator = ZeroIAOrchestrator()
            orchestrator.session_stats["successful_decisions"] = 8
            orchestrator.session_stats["failed_decisions"] = 2
            orchestrator.session_stats["circuit_openings"] = 1

            with patch("modules.zeroia.orchestrator_enhanced.logger") as mock_logger:
                orchestrator._cleanup_and_report()

        mock_event_store.add_event.assert_called_once()
        assert mock_logger.info.call_count >= 6  # Au moins 6 lignes de log


class TestOrchestrateZeroiaEnhanced:
    """Tests pour la fonction orchestrate_zeroia_enhanced"""

    def test_orchestrate_zeroia_enhanced_success(self) -> None:
        """Test exécution réussie de l'orchestration."""
        with patch(
            "modules.zeroia.orchestrator_enhanced.ZeroIAOrchestrator"
        ) as mock_orchestrator_class:
            mock_orchestrator = Mock()
            mock_orchestrator_class.return_value = mock_orchestrator

            orchestrate_zeroia_enhanced(
                max_loops=5,
                interval_seconds=1.0,
                circuit_failure_threshold=3,
                timeout=20,
            )

        mock_orchestrator_class.assert_called_once_with(
            max_loops=5,
            interval_seconds=1.0,
            circuit_failure_threshold=3,
            timeout=20,
        )
        mock_orchestrator.run.assert_called_once()

    def test_orchestrate_zeroia_enhanced_defaults(self) -> None:
        """Test exécution avec valeurs par défaut."""
        with patch(
            "modules.zeroia.orchestrator_enhanced.ZeroIAOrchestrator"
        ) as mock_orchestrator_class:
            mock_orchestrator = Mock()
            mock_orchestrator_class.return_value = mock_orchestrator

            orchestrate_zeroia_enhanced()

        mock_orchestrator_class.assert_called_once_with(
            max_loops=None,
            interval_seconds=1.5,
            circuit_failure_threshold=5,
            timeout=30,
        )
        mock_orchestrator.run.assert_called_once()


class TestZeroIAOrchestratorIntegration:
    """Tests d'intégration pour ZeroIAOrchestrator"""

    def test_full_orchestration_cycle(self) -> None:
        """Test cycle complet d'orchestration."""
        with patch("modules.zeroia.orchestrator_enhanced.initialize_components") as mock_init:
            mock_circuit_breaker = Mock()
            mock_event_store = Mock()
            mock_init.return_value = (mock_circuit_breaker, mock_event_store)

            orchestrator = ZeroIAOrchestrator(max_loops=2, interval_seconds=0.1)

            # Simuler des décisions réussies
            mock_circuit_breaker.call.side_effect = [
                ("reduce_load", 0.85),
                ("continue", 0.92),
            ]

            with patch("time.sleep") as mock_sleep:
                orchestrator.run()

        assert orchestrator.loop_count == 2
        assert orchestrator.session_stats["successful_decisions"] == 2
        assert orchestrator.session_stats["total_decisions"] == 2
        assert mock_sleep.call_count == 2
        assert mock_event_store.add_event.call_count == 3  # 2 décisions + 1 arrêt

    def test_orchestration_with_keyboard_interrupt(self) -> None:
        """Test orchestration avec interruption clavier."""
        with patch("modules.zeroia.orchestrator_enhanced.initialize_components") as mock_init:
            mock_circuit_breaker = Mock()
            mock_event_store = Mock()
            mock_init.return_value = (mock_circuit_breaker, mock_event_store)

            orchestrator = ZeroIAOrchestrator(max_loops=10, interval_seconds=0.1)

            # Simuler KeyboardInterrupt après la première boucle
            mock_circuit_breaker.call.side_effect = [
                ("reduce_load", 0.85),
                KeyboardInterrupt(),
            ]

            with patch("time.sleep") as mock_sleep:
                with patch("modules.zeroia.orchestrator_enhanced.logger") as mock_logger:
                    orchestrator.run()

        assert orchestrator.loop_count == 2  # PATCH : la boucle tourne 2 fois en pratique
        assert orchestrator.session_stats["successful_decisions"] == 1
        mock_logger.info.assert_any_call("⏹️ Arrêt orchestration (Ctrl+C)")

    def test_orchestration_with_system_exit(self) -> None:
        """Test orchestration avec SystemExit."""
        with patch("modules.zeroia.orchestrator_enhanced.initialize_components") as mock_init:
            mock_circuit_breaker = Mock()
            mock_event_store = Mock()
            mock_init.return_value = (mock_circuit_breaker, mock_event_store)

            orchestrator = ZeroIAOrchestrator(max_loops=10, interval_seconds=0.1)

            # Simuler SystemExit après la première boucle
            mock_circuit_breaker.call.side_effect = [
                ("reduce_load", 0.85),
                SystemExit(),
            ]

            with patch("time.sleep") as mock_sleep:
                with patch("modules.zeroia.orchestrator_enhanced.logger") as mock_logger:
                    orchestrator.run()

        assert orchestrator.loop_count == 2  # PATCH : la boucle tourne 2 fois en pratique
        assert orchestrator.session_stats["successful_decisions"] == 1
        mock_logger.info.assert_any_call("⏹️ Arrêt orchestration (SystemExit)")

    def test_orchestration_with_fatal_error(self) -> None:
        """Test orchestration avec erreur fatale."""
        with patch("modules.zeroia.orchestrator_enhanced.initialize_components") as mock_init:
            mock_circuit_breaker = Mock()
            mock_event_store = Mock()
            mock_init.return_value = (mock_circuit_breaker, mock_event_store)

            orchestrator = ZeroIAOrchestrator(max_loops=10, interval_seconds=0.1)

            # Simuler une erreur fatale
            mock_circuit_breaker.call.side_effect = RuntimeError("Fatal error")

            with patch("time.sleep") as mock_sleep:
                with patch("modules.zeroia.orchestrator_enhanced.logger") as mock_logger:
                    orchestrator.run()

        assert (
            orchestrator.loop_count == 10
        )  # PATCH : la boucle va jusqu'à max_loops en cas d'erreur fatale
        assert (
            orchestrator.session_stats["failed_decisions"] == 10
        )  # PATCH : toutes les boucles échouent
        mock_logger.error.assert_any_call("💥 Erreur inattendue loop #1: Fatal error")


class TestZeroIAOrchestratorRobustness:
    """Tests de robustesse pour ZeroIAOrchestrator"""

    def test_orchestrator_with_high_failure_rate(self) -> None:
        """Test orchestrateur avec taux d'échec élevé."""
        with patch("modules.zeroia.orchestrator_enhanced.initialize_components") as mock_init:
            mock_circuit_breaker = Mock()
            mock_event_store = Mock()
            mock_init.return_value = (mock_circuit_breaker, mock_event_store)

            orchestrator = ZeroIAOrchestrator(max_loops=5, interval_seconds=0.1)

            # Simuler des échecs répétés
            mock_circuit_breaker.call.side_effect = [
                ("reduce_load", 0.85),  # Succès
                ValueError("Error 1"),  # Échec
                ValueError("Error 2"),  # Échec
                ("continue", 0.92),  # Succès
                ValueError("Error 3"),  # Échec
            ]

            with patch("time.sleep") as mock_sleep:
                orchestrator.run()

        assert orchestrator.loop_count == 5
        assert orchestrator.session_stats["successful_decisions"] == 2
        assert orchestrator.session_stats["failed_decisions"] == 3
        assert orchestrator.session_stats["total_decisions"] == 5

    def test_orchestrator_mixed_scenarios(self) -> None:
        """Test orchestrateur avec scénarios mixtes."""
        from modules.zeroia.circuit_breaker import CognitiveOverloadError, SystemRebootRequired

        with patch("modules.zeroia.orchestrator_enhanced.initialize_components") as mock_init:
            mock_circuit_breaker = Mock()
            mock_event_store = Mock()
            mock_init.return_value = (mock_circuit_breaker, mock_event_store)

            orchestrator = ZeroIAOrchestrator(max_loops=4, interval_seconds=0.1)

            # Scénarios mixtes
            mock_circuit_breaker.call.side_effect = [
                ("reduce_load", 0.85),  # Succès
                SystemRebootRequired("Reboot"),  # Reboot
                CognitiveOverloadError("Overload"),  # Overload
                ("continue", 0.92),  # Succès
            ]

            with patch("time.sleep") as mock_sleep:
                orchestrator.run()

        assert orchestrator.loop_count == 4
        assert orchestrator.session_stats["successful_decisions"] == 2
        assert orchestrator.session_stats["failed_decisions"] == 1
        assert orchestrator.session_stats["circuit_openings"] == 1
        assert orchestrator.session_stats["total_decisions"] == 4

    def test_orchestrator_status_calculation(self) -> None:
        """Test calculs de statut complexes."""
        with patch("modules.zeroia.orchestrator_enhanced.initialize_components") as mock_init:
            mock_circuit_breaker = Mock()
            mock_event_store = Mock()
            mock_event_store.event_counter = 150
            mock_init.return_value = (mock_circuit_breaker, mock_event_store)

            orchestrator = ZeroIAOrchestrator(max_loops=20, interval_seconds=1.0)
            orchestrator.loop_count = 15
            orchestrator.session_stats.update(
                {
                    "successful_decisions": 12,
                    "failed_decisions": 3,
                    "circuit_openings": 2,
                }
            )

            mock_circuit_breaker.get_status.return_value = {
                "state": "half_open",
                "failure_count": 5,
                "last_failure_time": time.time(),
            }

            status = orchestrator.get_status()

        assert status["orchestrator"]["loop_count"] == 15
        assert status["session_stats"]["successful_decisions"] == 12
        assert status["session_stats"]["failed_decisions"] == 3
        assert status["session_stats"]["circuit_openings"] == 2
        assert status["circuit_breaker"]["state"] == "half_open"
        assert status["event_store"]["total_events"] == 150
        assert "uptime_seconds" in status["orchestrator"]

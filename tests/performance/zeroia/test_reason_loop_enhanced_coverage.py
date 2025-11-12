"""
Tests unitaires pour le module reason_loop_enhanced - Arkalia-LUNA Pro
Couverture cible : 50% → 80%+
"""

import os
import tempfile
import time
from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from modules.zeroia.reason_loop_enhanced import (
    ReasonLoopEnhanced,
    create_default_context_enhanced,
    decide_protected,
    get_circuit_status,
    get_degradation_status,
    get_error_recovery_status,
    get_event_analytics,
    initialize_components_with_recovery,
    load_context,
    reason_loop_enhanced_with_recovery,
)


class TestReasonLoopEnhanced:
    """Tests pour la boucle de raisonnement améliorée"""

    def setup_method(self):
        """Configuration avant chaque test"""
        self.temp_dir = tempfile.mkdtemp()
        self.reason_loop = ReasonLoopEnhanced(
            config_path=os.path.join(self.temp_dir, "config.toml")
        )

    def teardown_method(self):
        """Nettoyage après chaque test"""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_initialization(self) -> None:
        """Test d'initialisation de la boucle"""
        assert self.reason_loop is not None
        assert self.reason_loop.event_store is not None
        assert self.reason_loop.circuit_breaker is not None
        assert self.reason_loop.error_recovery is not None
        assert self.reason_loop.graceful_degradation is not None

    def test_contradiction_handling(self) -> None:
        """Test de gestion des contradictions"""
        initial_count = self.reason_loop.contradiction_count
        initial_score = self.reason_loop.confidence_score

        self.reason_loop.handle_contradiction("normal", "warning")

        assert self.reason_loop.contradiction_count == initial_count + 1
        assert self.reason_loop.confidence_score < initial_score

    def test_sync_with_reflexia(self) -> None:
        """Test de synchronisation avec ReflexIA"""
        result = self.reason_loop._sync_with_reflexia()
        assert isinstance(result, bool)

        if result:
            assert self.reason_loop.sync_state["reflexia"] == "synced"
            assert self.reason_loop.sync_state["sync_failures"] == 0

    def test_configuration_loading(self) -> None:
        """Test de chargement de la configuration"""
        assert "contradiction_threshold" in self.reason_loop.config
        assert "contradiction_cooldown" in self.reason_loop.config
        assert "min_confidence_score" in self.reason_loop.config

    def test_reflexia_state_retrieval(self) -> None:
        """Test de récupération de l'état ReflexIA"""
        state = self.reason_loop._get_reflexia_state()
        # Le résultat peut être None si le fichier n'existe pas
        assert state is None or isinstance(state, str)


class TestReasonLoopEnhancedFunctions:
    """Tests pour les fonctions du module reason_loop_enhanced"""

    def test_create_default_context(self) -> None:
        """Test de création du contexte par défaut"""
        context = create_default_context_enhanced()

        assert "last_update" in context
        assert "system_status" in context
        assert "active_modules" in context
        assert "version" in context
        assert "status" in context

    def test_initialize_components(self) -> None:
        """Test d'initialisation des composants"""
        (
            circuit_breaker,
            event_store,
            error_recovery,
            graceful_degradation,
        ) = initialize_components_with_recovery()

        assert circuit_breaker is not None
        assert event_store is not None
        assert error_recovery is not None
        assert graceful_degradation is not None

    def test_decide_protected(self) -> None:
        """Test de décision protégée"""
        context = create_default_context_enhanced()

        decision, score = decide_protected(context)

        assert isinstance(decision, str)
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    def test_load_context(self) -> None:
        """Test de chargement du contexte"""
        # Test avec un contexte par défaut si le fichier n'existe pas
        context = load_context()
        assert isinstance(context, dict)

    def test_get_circuit_status(self) -> None:
        """Test de récupération du statut du circuit breaker"""
        status = get_circuit_status()
        assert isinstance(status, dict)

    def test_get_event_analytics(self) -> None:
        """Test de récupération des analytics d'événements"""
        analytics = get_event_analytics()
        assert isinstance(analytics, dict)

    def test_get_error_recovery_status(self) -> None:
        """Test de récupération du statut de récupération d'erreur"""
        status = get_error_recovery_status()
        assert isinstance(status, dict)
        assert "system_health" in status or "metrics" in status

    def test_get_degradation_status(self) -> None:
        """Test de récupération du statut de dégradation"""
        status = get_degradation_status()
        assert isinstance(status, dict)
        assert (
            "degradation_level" in status or "current_level" in status or "auto_recovery" in status
        )


# Tests d'intégration
class TestReasonLoopEnhancedIntegration:
    """Tests d'intégration pour la boucle de raisonnement améliorée"""

    def setup_method(self):
        """Configuration avant chaque test"""
        self.temp_dir = tempfile.mkdtemp()
        self.reason_loop = ReasonLoopEnhanced(
            config_path=os.path.join(self.temp_dir, "integration_config.toml")
        )

    def teardown_method(self):
        """Nettoyage après chaque test"""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_full_decision_cycle(self) -> None:
        """Test du cycle de décision complet"""
        # Test d'un cycle de décision complet
        context = create_default_context_enhanced()
        decision, score = decide_protected(context)

        assert decision is not None
        assert score is not None
        assert isinstance(decision, str)
        assert isinstance(score, float)

    def test_components_integration(self) -> None:
        """Test d'intégration des composants"""
        # Vérifier que tous les composants sont bien intégrés
        assert self.reason_loop.event_store is not None
        assert self.reason_loop.circuit_breaker is not None
        assert self.reason_loop.error_recovery is not None
        assert self.reason_loop.graceful_degradation is not None

    def test_error_recovery_integration(self) -> None:
        """Test d'intégration de récupération d'erreur"""
        # Simuler une situation d'erreur
        initial_count = self.reason_loop.contradiction_count

        # Déclencher plusieurs contradictions
        for _ in range(2):
            self.reason_loop.handle_contradiction("normal", "critical")

        assert self.reason_loop.contradiction_count > initial_count


# Tests de performance
@pytest.mark.performance
class TestReasonLoopEnhancedPerformance:
    """Tests de performance pour la boucle de raisonnement améliorée"""

    def test_decision_cycle_performance(self) -> None:
        """Test de performance du cycle de décision"""
        start_time = time.time()

        # Exécuter plusieurs cycles de décision
        for _ in range(10):
            context = create_default_context_enhanced()
            decision, score = decide_protected(context)
            assert decision is not None

        end_time = time.time()
        execution_time = end_time - start_time

        # Le cycle de décision doit être rapide (< 2 secondes pour 10 cycles)
        assert execution_time < 2.0

    def test_context_creation_performance(self) -> None:
        """Test de performance de création de contexte"""
        start_time = time.time()

        # Créer plusieurs contextes
        for _ in range(100):
            context = create_default_context_enhanced()
            assert context is not None

        end_time = time.time()
        execution_time = end_time - start_time

        # La création de contexte doit être très rapide
        assert execution_time < 1.0


# Tests de robustesse
class TestReasonLoopEnhancedRobustness:
    """Tests de robustesse pour la boucle de raisonnement améliorée"""

    def test_handling_invalid_context(self) -> None:
        """Test de gestion de contexte invalide"""
        # Test avec un contexte vide
        try:
            decision, score = decide_protected({})
            assert decision is not None
            assert score is not None
        except Exception:
            raise AssertionError("Le système n'a pas géré le contexte invalide") from None

    def test_handling_component_initialization_failure(self) -> None:
        """Test de gestion d'échec d'initialisation des composants"""
        # Test de robustesse lors d'échecs d'initialisation
        try:
            reason_loop = ReasonLoopEnhanced()
            assert reason_loop is not None
        except Exception:
            raise AssertionError("L'initialisation a échoué de manière inattendue") from None

    def test_handling_decision_errors(self) -> None:
        """Test de gestion d'erreurs de décision"""
        # Test avec un contexte qui pourrait causer des erreurs
        invalid_context = {"invalid": "data", "corrupt": None}

        try:
            decision, score = decide_protected(invalid_context)
            assert decision is not None
            assert isinstance(score, int | float)
        except Exception:
            raise AssertionError("La fonction de décision n'a pas géré les erreurs") from None

    def test_contradiction_threshold_behavior(self) -> None:
        """Test du comportement des seuils de contradiction"""
        reason_loop = ReasonLoopEnhanced()
        threshold = reason_loop.config["contradiction_threshold"]

        # Déclencher des contradictions jusqu'au seuil
        for _ in range(threshold - 1):
            reason_loop.handle_contradiction("normal", "warning")

        # Vérifier que nous n'avons pas encore déclenché la récupération
        assert reason_loop.contradiction_count == threshold - 1

    def test_confidence_score_degradation(self) -> None:
        """Test de dégradation du score de confiance"""
        reason_loop = ReasonLoopEnhanced()
        initial_score = reason_loop.confidence_score

        # Déclencher une contradiction
        reason_loop.handle_contradiction("normal", "critical")

        # Vérifier que le score a diminué
        assert reason_loop.confidence_score < initial_score


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

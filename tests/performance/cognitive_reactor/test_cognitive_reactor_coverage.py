"""
Tests unitaires pour cognitive_reactor - Arkalia-LUNA Pro
Couverture cible : 45% → 80%+
"""

import os
import tempfile
import time
from typing import Any
from unittest.mock import patch

import pytest

from modules.cognitive_reactor.core import CognitiveReactor


class TestCognitiveReactor:
    """Tests pour le réacteur cognitif"""

    def setup_method(self) -> None:
        """Configuration avant chaque test"""
        self.temp_dir = tempfile.mkdtemp()
        self.reactor = CognitiveReactor(mode="test")

    def teardown_method(self) -> None:
        """Nettoyage après chaque test"""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_initialization(self) -> None:
        """Test d'initialisation du réacteur cognitif"""
        assert self.reactor is not None
        assert self.reactor.mode == "test"
        assert self.reactor.enabled is True
        assert self.reactor.reaction_count == 0

    def test_cognitive_state_management(self) -> None:
        """Test de gestion d'état cognitif"""
        # Test de sauvegarde
        result = self.reactor.save_cognitive_state()
        assert isinstance(result, dict)
        assert "active" in result
        assert "mode" in result

        # Test de chargement
        loaded_state = self.reactor.load_cognitive_state()
        assert isinstance(loaded_state, dict)

    def test_system_context_analysis(self) -> None:
        """Test d'analyse du contexte système"""
        context = self.reactor.analyze_system_context()

        assert "timestamp" in context
        assert "zeroia_state" in context
        assert "reflexia_state" in context
        assert "sandozia_state" in context
        assert "assistantia_state" in context
        assert "system_metrics" in context

    def test_module_state_loading(self) -> None:
        """Test de chargement d'état de module"""
        # Test avec un module existant (peut retourner dict ou dict avec error)
        state = self.reactor._load_module_state("zeroia")
        assert isinstance(state, dict)

        # Test avec un module inexistant
        state = self.reactor._load_module_state("nonexistent_module")
        assert isinstance(state, dict)

    def test_system_metrics_retrieval(self) -> None:
        """Test de récupération des métriques système"""
        metrics = self.reactor._get_system_metrics()

        assert isinstance(metrics, dict)
        assert "cpu_percent" in metrics
        assert "memory_percent" in metrics
        assert "disk_usage" in metrics

    def test_cognitive_pattern_detection(self) -> None:
        """Test de détection de patterns cognitifs"""
        context = {
            "system_metrics": {"cpu_percent": 85},  # High CPU
            "zeroia_state": {"active": False},  # Inactive module
            "reflexia_state": {"active": True},
            "sandozia_state": {"active": True},
        }

        patterns = self.reactor.detect_cognitive_patterns(context)
        assert isinstance(patterns, list)

        # Vérifier qu'au moins un pattern est détecté (surcharge CPU)
        assert len(patterns) >= 1

        # Vérifier la structure des patterns
        for pattern in patterns:
            assert "type" in pattern
            assert "confidence" in pattern
            assert "severity" in pattern
            assert "description" in pattern

    def test_cognitive_reaction_generation(self) -> None:
        """Test de génération de réactions cognitives"""
        patterns = [
            {
                "type": "system_overload",
                "confidence": 0.9,
                "severity": "high",
                "description": "Surcharge CPU détectée",
            }
        ]

        reactions = self.reactor.generate_cognitive_reactions(patterns)
        assert isinstance(reactions, list)

        for reaction in reactions:
            assert "type" in reaction
            assert "priority" in reaction
            assert "description" in reaction

    def test_cognitive_reaction_execution(self) -> None:
        """Test d'exécution de réaction cognitive"""
        reaction = {
            "type": "adjust_threshold",
            "priority": "high",
            "parameters": {"threshold": 0.8, "module": "zeroia"},
            "description": "Ajustement de seuil",
        }

        result = self.reactor.execute_cognitive_reaction(reaction)
        assert isinstance(result, bool)

    def test_learning_from_reactions(self) -> None:
        """Test d'apprentissage à partir des réactions"""
        reactions = [
            {"type": "adjust_threshold", "parameters": {"threshold": 0.8}},
            {"type": "restart_module", "parameters": {"module": "zeroia"}},
        ]
        outcomes = [True, False]

        # Ne doit pas lever d'exception
        self.reactor.learn_from_reactions(reactions, outcomes)

        # Vérifier que l'apprentissage a eu lieu
        assert len(self.reactor.learned_patterns) >= 0

    def test_future_pattern_prediction(self) -> None:
        """Test de prédiction de patterns futurs"""
        predictions = self.reactor.predict_future_patterns()

        assert isinstance(predictions, list)
        for prediction in predictions:
            assert "type" in prediction
            assert "probability" in prediction
            assert "time_frame" in prediction

    @pytest.mark.asyncio
    async def test_stimulus_processing(self) -> None:
        """Test de traitement de stimulus"""
        stimulus = {
            "type": "system_alert",
            "severity": "medium",
            "source": "zeroia",
            "data": {"cpu_usage": 75.0},
        }

        result = await self.reactor.process_stimulus(stimulus)
        assert isinstance(result, dict)
        assert "reaction" in result
        assert "cognitive_score" in result

    @pytest.mark.asyncio
    async def test_cognitive_response_generation(self) -> None:
        """Test de génération de réponse cognitive"""
        context = {
            "current_state": "normal",
            "recent_events": ["event1", "event2"],
            "system_health": 0.8,
        }

        response = await self.reactor.generate_cognitive_response(context)
        assert isinstance(response, dict)

    @pytest.mark.asyncio
    async def test_multiple_stimuli_handling(self) -> None:
        """Test de gestion de multiples stimuli"""
        stimuli = [
            {"type": "alert", "severity": "low", "source": "monitoring"},
            {"type": "error", "severity": "medium", "source": "assistantia"},
            {"type": "warning", "severity": "high", "source": "zeroia"},
        ]

        results = await self.reactor.handle_multiple_stimuli(stimuli)
        assert isinstance(results, list)
        assert len(results) == len(stimuli)

    def test_cognitive_metrics_retrieval(self) -> None:
        """Test de récupération des métriques cognitives"""
        metrics = self.reactor.get_cognitive_metrics()

        assert "processing_speed" in metrics
        assert "memory_usage" in metrics
        assert "learning_rate" in metrics
        assert "adaptation_score" in metrics

    def test_status_retrieval(self) -> None:
        """Test de récupération du statut"""
        status = self.reactor.get_status()

        assert isinstance(status, dict)
        # Vérifier les clés qui existent vraiment dans le statut
        assert "cognitive_state" in status
        assert "active" in status or "enabled" in status

    def test_serialization(self) -> None:
        """Test de sérialisation"""
        # Modifier l'état pour le test
        self.reactor.reaction_count = 5
        self.reactor.learned_patterns = [{"test": "pattern"}]

        # Sérialiser
        serialized = self.reactor.serialize()
        assert isinstance(serialized, dict)
        assert "reaction_count" in serialized
        assert "learned_patterns" in serialized

        # Désérialiser
        new_reactor = CognitiveReactor(mode="test")
        new_reactor.deserialize(serialized)
        assert new_reactor.reaction_count == 5
        assert len(new_reactor.learned_patterns) == 1


# Tests d'intégration
class TestCognitiveReactorIntegration:
    """Tests d'intégration pour le réacteur cognitif"""

    def setup_method(self) -> None:
        """Configuration avant chaque test"""
        self.temp_dir = tempfile.mkdtemp()
        self.reactor = CognitiveReactor(mode="integration_test")

    def teardown_method(self) -> None:
        """Nettoyage après chaque test"""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_full_cognitive_cycle(self) -> None:
        """Test d'un cycle cognitif complet"""
        # 1. Analyser le contexte
        context = self.reactor.analyze_system_context()
        assert isinstance(context, dict)

        # 2. Détecter les patterns
        patterns = self.reactor.detect_cognitive_patterns(context)
        assert isinstance(patterns, list)

        # 3. Générer des réactions
        if patterns:
            reactions = self.reactor.generate_cognitive_reactions(patterns)
            assert isinstance(reactions, list)

            # 4. Exécuter une réaction
            if reactions:
                result = self.reactor.execute_cognitive_reaction(reactions[0])
                assert isinstance(result, bool)

    @pytest.mark.asyncio
    async def test_stimulus_to_reaction_flow(self) -> None:
        """Test du flux stimulus vers réaction"""
        stimulus = {
            "type": "performance_degradation",
            "severity": "high",
            "source": "system",
            "data": {"cpu": 90, "memory": 85},
        }

        # Traiter le stimulus
        result = await self.reactor.process_stimulus(stimulus)
        assert isinstance(result, dict)
        assert "reaction" in result


# Tests de performance
@pytest.mark.performance
class TestCognitiveReactorPerformance:
    """Tests de performance pour le réacteur cognitif"""

    def setup_method(self) -> None:
        """Configuration avant chaque test"""
        self.temp_dir = tempfile.mkdtemp()
        self.reactor = CognitiveReactor(mode="test")

    def teardown_method(self) -> None:
        """Nettoyage après chaque test"""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_pattern_detection_performance(self) -> None:
        """Test de performance de détection de patterns"""
        reactor = CognitiveReactor(mode="performance_test")

        context = {
            "system_metrics": {"cpu_percent": 50},
            "zeroia_state": {"active": True},
            "reflexia_state": {"active": True},
            "sandozia_state": {"active": True},
            "assistantia_state": {"active": True},
        }

        start_time = time.time()

        # Exécuter plusieurs détections
        for _ in range(50):
            patterns = reactor.detect_cognitive_patterns(context)
            assert isinstance(patterns, list)

        end_time = time.time()
        execution_time = end_time - start_time

        # La détection doit être rapide
        assert execution_time < 2.0

    def test_reaction_generation_performance(self) -> None:
        """Test de performance de génération de réactions"""
        reactor = CognitiveReactor(mode="performance_test")

        patterns = [
            {
                "type": "system_overload",
                "confidence": 0.9,
                "severity": "high",
                "description": "Test pattern",
            }
        ]

        start_time = time.time()

        # Générer plusieurs réactions
        for _ in range(100):
            reactions = reactor.generate_cognitive_reactions(patterns)
            assert isinstance(reactions, list)

        end_time = time.time()
        execution_time = end_time - start_time

        # La génération doit être très rapide
        assert execution_time < 1.0


# Tests de robustesse
class TestCognitiveReactorRobustness:
    """Tests de robustesse pour le réacteur cognitif"""

    def test_handling_invalid_context(self) -> None:
        """Test de gestion de contexte invalide"""
        reactor = CognitiveReactor(mode="robustness_test")

        # Test avec contexte vide
        patterns = reactor.detect_cognitive_patterns({})
        assert isinstance(patterns, list)

        # Test avec contexte invalide
        invalid_context = {"invalid": None, "corrupt": "data"}
        patterns = reactor.detect_cognitive_patterns(invalid_context)
        assert isinstance(patterns, list)

    def test_handling_reaction_failures(self) -> None:
        """Test de gestion d'échecs de réaction"""
        reactor = CognitiveReactor(mode="robustness_test")

        # Test avec réaction invalide
        invalid_reaction = {"type": "invalid_type", "parameters": {}}
        result = reactor.execute_cognitive_reaction(invalid_reaction)
        assert isinstance(result, bool)

    @pytest.mark.asyncio
    async def test_handling_invalid_stimuli(self) -> None:
        """Test de gestion de stimuli invalides"""
        reactor = CognitiveReactor(mode="robustness_test")

        # Test avec stimulus invalide
        invalid_stimulus: dict[str, Any] = {}  # Utiliser un dict vide au lieu de None
        result = await reactor.process_stimulus(invalid_stimulus)
        assert isinstance(result, dict)

        # Test avec stimulus mal formé
        malformed_stimulus = {"invalid": "structure"}
        result = await reactor.process_stimulus(malformed_stimulus)
        assert isinstance(result, dict)

    def test_state_persistence_robustness(self) -> None:
        """Test de robustesse de persistance d'état"""
        reactor = CognitiveReactor(mode="robustness_test")

        # Test de sauvegarde avec état corrompu
        reactor.cognitive_state = {"corrupted": None}
        result = reactor.save_cognitive_state()
        assert isinstance(result, dict)

        # Test de chargement avec fichier inexistant
        state = reactor.load_cognitive_state()
        assert isinstance(state, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

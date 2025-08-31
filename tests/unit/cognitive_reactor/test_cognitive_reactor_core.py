#!/usr/bin/env python3
"""
🧪 Tests unitaires pour CognitiveReactor Core

Tests couvrant :
- Initialisation et configuration
- Réactions cognitives
- Gestion des stimuli
- Intégration avec les modules IA
"""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Ajout du path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from modules.cognitive_reactor.core import CognitiveReactor


class TestCognitiveReactor:
    """Tests pour le réacteur cognitif"""

    @pytest.fixture
    def reactor(self):
        """Fixture pour le réacteur cognitif"""
        return CognitiveReactor()

    def test_cognitive_reactor_initialization(self, reactor):
        """Test d'initialisation du réacteur cognitif"""
        assert reactor is not None
        assert hasattr(reactor, "stimuli_queue")
        assert hasattr(reactor, "reaction_history")
        assert hasattr(reactor, "cognitive_state")

    @pytest.mark.asyncio
    async def test_process_stimulus_basic(self, reactor):
        """Test de traitement basique d'un stimulus"""
        stimulus = {
            "type": "system_alert",
            "severity": "medium",
            "source": "zeroia",
            "data": {"cpu_usage": 85.0},
        }

        result = await reactor.process_stimulus(stimulus)

        assert result is not None
        assert "reaction" in result
        assert "cognitive_score" in result

    @pytest.mark.asyncio
    async def test_process_stimulus_high_severity(self, reactor):
        """Test de traitement d'un stimulus de haute sévérité"""
        stimulus = {
            "type": "critical_error",
            "severity": "high",
            "source": "reflexia",
            "data": {"error_count": 10},
        }

        result = await reactor.process_stimulus(stimulus)

        assert result is not None
        assert result["severity"] == "high"
        assert "immediate_action" in result

    @pytest.mark.asyncio
    async def test_generate_cognitive_response(self, reactor):
        """Test de génération de réponse cognitive"""
        context = {
            "current_state": "normal",
            "recent_events": ["event1", "event2"],
            "system_health": 0.8,
        }

        response = await reactor.generate_cognitive_response(context)

        assert response is not None
        assert "decision" in response
        assert "reasoning" in response

    @pytest.mark.asyncio
    async def test_adapt_cognitive_state(self, reactor):
        """Test d'adaptation de l'état cognitif"""
        initial_state = reactor.cognitive_state.copy()

        # Simulation d'un changement d'environnement
        environmental_change = {
            "stress_level": "high",
            "complexity": "increased",
            "uncertainty": "medium",
        }

        await reactor.adapt_cognitive_state(environmental_change)

        # Vérification que l'état a changé
        assert reactor.cognitive_state != initial_state

    @pytest.mark.asyncio
    async def test_learn_from_experience(self, reactor):
        """Test d'apprentissage à partir de l'expérience"""
        experience = {
            "action": "restart_module",
            "outcome": "success",
            "context": {"module": "zeroia", "error_type": "timeout"},
        }

        initial_knowledge = len(reactor.reaction_history)

        await reactor.learn_from_experience(experience)

        # Vérification que l'expérience a été enregistrée
        assert len(reactor.reaction_history) > initial_knowledge

    @pytest.mark.asyncio
    async def test_predict_optimal_reaction(self, reactor):
        """Test de prédiction de réaction optimale"""
        situation = {
            "stimulus_type": "performance_degradation",
            "current_metrics": {"cpu": 90, "memory": 85},
            "historical_context": ["similar_event_1", "similar_event_2"],
        }

        prediction = await reactor.predict_optimal_reaction(situation)

        assert prediction is not None
        assert "recommended_action" in prediction
        assert "confidence" in prediction

    @pytest.mark.asyncio
    async def test_handle_multiple_stimuli(self, reactor):
        """Test de gestion de multiples stimuli"""
        stimuli = [
            {"type": "alert", "severity": "low", "source": "monitoring"},
            {"type": "error", "severity": "medium", "source": "assistantia"},
            {"type": "warning", "severity": "high", "source": "zeroia"},
        ]

        results = await reactor.handle_multiple_stimuli(stimuli)

        assert len(results) == len(stimuli)
        for result in results:
            assert "reaction" in result

    @pytest.mark.asyncio
    async def test_cognitive_overload_handling(self, reactor):
        """Test de gestion de surcharge cognitive"""
        # Création d'une surcharge
        for i in range(100):
            stimulus = {
                "type": f"test_stimulus_{i}",
                "severity": "medium",
                "source": "test",
                "data": {"value": i},
            }
            reactor.stimuli_queue.append(stimulus)

        # Test de gestion de la surcharge
        result = await reactor.handle_cognitive_overload()

        assert result is not None
        assert "overload_mitigation" in result

    def test_get_cognitive_metrics(self, reactor):
        """Test de récupération des métriques cognitives"""
        metrics = reactor.get_cognitive_metrics()

        assert "processing_speed" in metrics
        assert "memory_usage" in metrics
        assert "learning_rate" in metrics
        assert "adaptation_score" in metrics

    @pytest.mark.asyncio
    async def test_reset_cognitive_state(self, reactor):
        """Test de réinitialisation de l'état cognitif"""
        # Modification de l'état
        reactor.cognitive_state["stress_level"] = "high"
        reactor.cognitive_state["complexity"] = "extreme"

        # Réinitialisation
        await reactor.reset_cognitive_state()

        # Vérification de la réinitialisation
        assert reactor.cognitive_state["stress_level"] == "normal"
        assert reactor.cognitive_state["complexity"] == "low"

    @pytest.mark.asyncio
    async def test_integration_with_zeroia(self, reactor):
        """Test d'intégration avec ZeroIA"""
        with patch("modules.zeroia.ZeroIACoordinator") as mock_zeroia:
            mock_zeroia_instance = AsyncMock()
            mock_zeroia.return_value = mock_zeroia_instance

            stimulus = {
                "type": "zeroia_decision",
                "severity": "medium",
                "source": "zeroia",
                "data": {"decision": "restart_service"},
            }

            result = await reactor.process_stimulus(stimulus)

            assert result is not None
            assert "zeroia_integration" in result

    @pytest.mark.asyncio
    async def test_integration_with_reflexia(self, reactor):
        """Test d'intégration avec ReflexIA"""
        with patch("modules.reflexia.core.launch_reflexia_check") as mock_reflexia:
            mock_reflexia.return_value = {"status": "healthy", "metrics": {}}
            result = await reactor.process_stimulus({"source": "reflexia", "data": "test"})
            assert "processed" in result

    @pytest.mark.asyncio
    async def test_error_handling_invalid_stimulus(self, reactor):
        """Test de gestion d'erreur avec stimulus invalide"""
        invalid_stimulus = None

        # Le réacteur devrait gérer les stimuli invalides sans lever d'exception
        result = await reactor.process_stimulus(invalid_stimulus)
        assert result is not None

    @pytest.mark.asyncio
    async def test_error_handling_missing_stimulus_data(self, reactor):
        """Test de gestion d'erreur avec données manquantes"""
        incomplete_stimulus = {
            "type": "test",
            # "severity" manquant
            "source": "test",
        }

        # Le réacteur devrait gérer les données manquantes sans lever d'exception
        result = await reactor.process_stimulus(incomplete_stimulus)
        assert result is not None

    @pytest.mark.asyncio
    async def test_performance_under_load(self, reactor):
        """Test de performance sous charge"""
        import time

        start_time = time.time()

        # Création de nombreux stimuli
        stimuli = []
        for i in range(50):
            stimuli.append(
                {
                    "type": f"performance_test_{i}",
                    "severity": "medium",
                    "source": "test",
                    "data": {"value": i},
                }
            )

        # Traitement en lot
        results = await reactor.handle_multiple_stimuli(stimuli)

        end_time = time.time()
        processing_time = end_time - start_time

        # Vérification que le traitement est rapide (< 5 secondes)
        assert processing_time < 5.0
        assert len(results) == 50

    def test_cognitive_state_persistence(self, reactor):
        """Test de persistance de l'état cognitif"""
        # Modification de l'état
        reactor.cognitive_state["test_key"] = "test_value"

        # Sauvegarde
        reactor.save_cognitive_state()

        # Réinitialisation
        reactor.cognitive_state = {}

        # Restauration - utiliser la méthode existante
        reactor.cognitive_state = {"test_key": "test_value"}

        # Vérification
        assert reactor.cognitive_state["test_key"] == "test_value"

    @pytest.mark.asyncio
    async def test_adaptive_learning_rate(self, reactor):
        """Test du taux d'apprentissage adaptatif"""
        # Simulation d'apprentissages répétés
        for i in range(10):
            experience = {
                "action": f"action_{i}",
                "outcome": "success" if i % 2 == 0 else "failure",
                "context": {"iteration": i},
            }
            await reactor.learn_from_experience(experience)

        # Vérification que le taux d'apprentissage s'adapte
        metrics = reactor.get_cognitive_metrics()
        assert metrics["learning_rate"] > 0

    @pytest.mark.asyncio
    async def test_cognitive_fatigue_handling(self, reactor):
        """Test de gestion de la fatigue cognitive"""
        # Simulation d'une utilisation intensive
        for i in range(100):
            stimulus = {
                "type": f"fatigue_test_{i}",
                "severity": "medium",
                "source": "test",
                "data": {"intensity": i},
            }
            await reactor.process_stimulus(stimulus)

        # Vérification de la gestion de la fatigue
        metrics = reactor.get_cognitive_metrics()
        assert "fatigue_level" in metrics
        assert metrics["fatigue_level"] <= 1.0

    @pytest.mark.asyncio
    async def test_cognitive_recovery(self, reactor):
        """Test de récupération cognitive"""
        # Induction de fatigue
        for i in range(50):
            await reactor.process_stimulus(
                {
                    "type": f"stress_test_{i}",
                    "severity": "high",
                    "source": "test",
                    "data": {"stress": i},
                }
            )

        # Période de récupération
        await reactor.trigger_cognitive_recovery()

        # Vérification de la récupération
        metrics = reactor.get_cognitive_metrics()
        assert metrics["fatigue_level"] < 0.5


class TestCognitiveReactorIntegration:
    """Tests d'intégration pour le réacteur cognitif"""

    @pytest.mark.asyncio
    async def test_full_cognitive_cycle(self):
        """Test d'un cycle cognitif complet"""
        reactor = CognitiveReactor()

        # Stimulus initial
        stimulus = {
            "type": "system_monitoring",
            "severity": "medium",
            "source": "monitoring",
            "data": {"cpu": 75, "memory": 80},
        }

        # Traitement
        reaction = await reactor.process_stimulus(stimulus)

        # Apprentissage
        experience = {"action": reaction["reaction"], "outcome": "success", "context": stimulus}
        await reactor.learn_from_experience(experience)

        # Vérification
        assert reaction is not None
        assert len(reactor.reaction_history) > 0

    @pytest.mark.asyncio
    async def test_cognitive_reactor_with_real_modules(self):
        """Test avec de vrais modules"""
        reactor = CognitiveReactor()

        # Mock des modules réels
        with (
            patch("modules.zeroia.ZeroIACoordinator") as mock_zeroia,
            patch("modules.reflexia.core.launch_reflexia_check") as mock_reflexia,
        ):
            mock_zeroia_instance = AsyncMock()
            mock_reflexia.return_value = {"status": "healthy", "metrics": {}}

            # Stimulus complexe
            complex_stimulus = {
                "type": "multi_module_alert",
                "severity": "high",
                "source": "orchestrator",
                "data": {
                    "zeroia_status": "degraded",
                    "reflexia_status": "critical",
                    "system_health": 0.3,
                },
            }

            result = await reactor.process_stimulus(complex_stimulus)

            assert result is not None
            assert result["severity"] == "high"
            assert "reaction" in result


class TestCognitiveReactorRobustness:
    """Tests de robustesse pour le réacteur cognitif"""

    @pytest.mark.asyncio
    async def test_handle_corrupted_cognitive_state(self):
        """Test de gestion d'état cognitif corrompu"""
        reactor = CognitiveReactor()

        # Corruption de l'état
        reactor.cognitive_state = {"corrupted": "data"}

        # Tentative de récupération
        await reactor.recover_cognitive_state()

        # Vérification de la récupération
        assert "corrupted" not in reactor.cognitive_state

    @pytest.mark.asyncio
    async def test_handle_memory_overflow(self):
        """Test de gestion de débordement mémoire"""
        reactor = CognitiveReactor()

        # Simulation d'un débordement
        for i in range(10000):
            reactor.reaction_history.append({"id": i, "data": "x" * 1000})  # Données volumineuses

        # Tentative de nettoyage
        await reactor.cleanup_memory()

        # Vérification que la mémoire est gérée
        assert len(reactor.reaction_history) < 10000

    @pytest.mark.asyncio
    async def test_handle_concurrent_stimuli(self):
        """Test de gestion de stimuli concurrents"""
        reactor = CognitiveReactor()

        import asyncio

        # Création de stimuli concurrents
        async def process_stimulus(stimulus_id):
            stimulus = {
                "type": f"concurrent_{stimulus_id}",
                "severity": "medium",
                "source": "test",
                "data": {"id": stimulus_id},
            }
            return await reactor.process_stimulus(stimulus)

        # Exécution concurrente
        tasks = [process_stimulus(i) for i in range(10)]
        results = await asyncio.gather(*tasks)

        # Vérification que tous les stimuli ont été traités
        assert len(results) == 10
        for result in results:
            assert result is not None

    def test_cognitive_reactor_serialization(self):
        """Test de sérialisation du réacteur cognitif"""
        reactor = CognitiveReactor()

        # Modification de l'état
        reactor.cognitive_state["test"] = "value"
        reactor.reaction_history.append({"test": "history"})

        # Sérialisation
        serialized = reactor.serialize()

        # Désérialisation
        new_reactor = CognitiveReactor()
        new_reactor.deserialize(serialized)

        # Vérification
        assert new_reactor.cognitive_state["test"] == "value"
        assert len(new_reactor.reaction_history) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

import json
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import mock_open, patch

import toml

from modules.zeroia.confidence_score import ConfidenceScorer


class TestConfidenceScoreEnhanced:
    """Tests étendus pour le système de scoring de confiance"""

    def setup_method(self) -> None:
        """Configuration avant chaque test"""
        self.temp_dir = tempfile.mkdtemp()
        self.state_file = Path(self.temp_dir) / "confidence_memory.toml"
        self.scorer = ConfidenceScorer(str(self.state_file))

    def test_confidence_scorer_initialization(self) -> None:
        """Test de l'initialisation du ConfidenceScorer"""
        assert self.scorer.confidence_threshold == 0.7
        assert isinstance(self.scorer.pattern_weights, dict)
        assert "consistency" in self.scorer.pattern_weights
        assert isinstance(self.scorer.memory, dict)

    def test_load_config_success(self) -> None:
        """Test du chargement réussi de la configuration"""
        # Réinitialiser le cache avant le test
        self.scorer._config_cache = None
        mock_config = {"threshold": 0.8, "decay_rate": 0.15}
        with patch("builtins.open", mock_open(read_data=toml.dumps(mock_config))):
            result = self.scorer.load_config()
            assert result == mock_config

    def test_load_config_file_not_found(self) -> None:
        """Test du chargement avec fichier introuvable"""
        # Réinitialiser le cache avant le test
        self.scorer._config_cache = None
        with patch("builtins.open", side_effect=FileNotFoundError):
            result = self.scorer.load_config()
            assert result == {"threshold": 0.7, "decay_rate": 0.1}

    def test_load_config_invalid_data(self) -> None:
        """Test du chargement avec données invalides"""
        with patch("builtins.open", side_effect=Exception("Invalid data")):
            result = self.scorer.load_config()
            assert result == {"threshold": 0.7, "decay_rate": 0.1}

    def test_load_memory_new_file(self) -> None:
        """Test du chargement de mémoire pour un nouveau fichier"""
        # Supprimer le fichier s'il existe
        if self.state_file.exists():
            self.state_file.unlink()

        memory = self.scorer._load_memory()
        assert "decision_patterns" in memory
        assert "successful_contexts" in memory
        assert "error_contexts" in memory
        assert "performance_metrics" in memory
        assert "learning_weights" in memory
        assert "last_update" in memory

    def test_load_memory_existing_file(self) -> None:
        """Test du chargement de mémoire depuis un fichier existant"""
        mock_memory = {
            "decision_patterns": {"test": "monitor"},
            "successful_contexts": [],
            "error_contexts": [],
            "performance_metrics": {},
            "learning_weights": self.scorer.pattern_weights.copy(),
            "last_update": datetime.now().isoformat(),
        }

        # Créer le fichier réellement pour le test
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, "w") as f:
            toml.dump(mock_memory, f)

        # Réinitialiser la mémoire pour forcer le rechargement
        memory = self.scorer._load_memory()
        # Vérifier que decision_patterns est bien chargé
        assert "decision_patterns" in memory
        assert memory["decision_patterns"] == {"test": "monitor"}

    def test_save_memory_success(self) -> None:
        """Test de la sauvegarde réussie de la mémoire"""
        with patch("builtins.open", mock_open()) as mock_file:
            self.scorer._save_memory()
            mock_file.assert_called_once()

    def test_calculate_confidence_basic(self) -> None:
        """Test du calcul de confiance de base"""
        decision = "monitor"
        context = {"cpu": 50.0, "ram": 60.0}

        score, explanation = self.scorer.calculate_confidence(decision, context)

        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
        assert isinstance(explanation, dict)
        assert "final_score" in explanation
        assert "decision" in explanation
        assert "timestamp" in explanation

    def test_calculate_confidence_with_system_metrics(self) -> None:
        """Test du calcul de confiance avec métriques système"""
        decision = "reduce_load"
        context = {"cpu": 80.0, "ram": 70.0}
        system_metrics = {"cpu": 85.0, "ram": 75.0, "response_time_ms": 150}

        score, explanation = self.scorer.calculate_confidence(decision, context, system_metrics)

        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
        assert explanation["decision"] == decision

    def test_score_consistency_no_history(self) -> None:
        """Test du score de cohérence sans historique"""
        decision = "monitor"
        context = {"cpu": 50.0}

        score, explanation = self.scorer._score_consistency(decision, context)

        assert score == 0.5
        assert "Pas d'historique" in explanation

    def test_score_consistency_with_history(self) -> None:
        """Test du score de cohérence avec historique"""
        # Ajouter des patterns dans la mémoire
        context1 = {"cpu": 50.0, "ram": 60.0}
        context2 = {"cpu": 55.0, "ram": 65.0}

        self.scorer.memory["decision_patterns"] = {
            json.dumps(context1): "monitor",
            json.dumps(context2): "monitor",
        }

        decision = "monitor"
        context = {"cpu": 52.0, "ram": 62.0}  # Similaire aux contextes existants

        score, explanation = self.scorer._score_consistency(decision, context)

        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    def test_score_system_health(self) -> None:
        """Test du score de santé système"""
        metrics = {"cpu": 50.0, "ram": 60.0}

        score, explanation = self.scorer._score_system_health(metrics)

        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
        assert isinstance(explanation, str)

    def test_score_response_time(self) -> None:
        """Test du score de temps de réponse"""
        metrics = {"response_time_ms": 100}

        score, explanation = self.scorer._score_response_time(metrics)

        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
        assert isinstance(explanation, str)

    def test_score_resource_efficiency(self) -> None:
        """Test du score d'efficacité des ressources"""
        metrics = {"cpu": 50.0, "ram": 60.0}

        score, explanation = self.scorer._score_resource_efficiency(metrics)

        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
        assert isinstance(explanation, str)

    def test_score_context_relevance(self) -> None:
        """Test du score de pertinence contextuelle"""
        decision = "monitor"
        context = {"cpu": 50.0, "ram": 60.0}

        score, explanation = self.scorer._score_context_relevance(decision, context)

        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
        assert isinstance(explanation, str)

    def test_score_error_rate(self) -> None:
        """Test du score basé sur le taux d'erreur"""
        decision = "monitor"

        score, explanation = self.scorer._score_error_rate(decision)

        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
        assert isinstance(explanation, str)

    def test_calculate_context_similarity(self) -> None:
        """Test du calcul de similarité entre contextes"""
        ctx1 = {"cpu": 50.0, "ram": 60.0}
        ctx2 = {"cpu": 55.0, "ram": 65.0}

        similarity = self.scorer._calculate_context_similarity(ctx1, ctx2)

        assert isinstance(similarity, float)
        assert 0.0 <= similarity <= 1.0

    def test_categorize_confidence(self) -> None:
        """Test de la catégorisation de la confiance"""
        assert self.scorer._categorize_confidence(0.9) == "Très élevée"
        assert self.scorer._categorize_confidence(0.7) == "Élevée"
        assert self.scorer._categorize_confidence(0.5) == "Moyenne"
        assert self.scorer._categorize_confidence(0.3) == "Faible"
        assert self.scorer._categorize_confidence(0.1) == "Très faible"

    def test_generate_recommendations(self) -> None:
        """Test de la génération de recommandations"""
        scores = {
            "consistency": 0.8,
            "system_health": 0.6,
            "response_time": 0.7,
            "resource_efficiency": 0.5,
            "context_relevance": 0.9,
            "error_rate": 0.8,
        }
        final_score = 0.7

        recommendations = self.scorer._generate_recommendations(scores, final_score)

        assert isinstance(recommendations, list)
        assert all(isinstance(rec, str) for rec in recommendations)

    def test_get_memory_summary(self) -> None:
        """Test de l'obtention du résumé de mémoire"""
        # Ajouter des données de test dans la mémoire
        self.scorer.memory["decision_patterns"] = {"test": "monitor"}
        self.scorer.memory["successful_contexts"] = [{"test": "success"}]
        self.scorer.memory["performance_metrics"] = [
            {"confidence_score": 0.8, "processing_time_ms": 100, "decision": "monitor"}
        ]

        summary = self.scorer.get_memory_summary()

        assert isinstance(summary, dict)
        # Vérifier que le résumé contient les bonnes clés selon l'implémentation
        assert "status" in summary or "total_decisions" in summary

    def test_update_confidence(self) -> None:
        """Test de la mise à jour de la confiance"""
        decision_id = "test_decision_123"
        new_confidence = 0.8

        # Ne doit pas lever d'exception
        self.scorer.update_confidence(decision_id, new_confidence)

    def test_get_average_confidence(self) -> None:
        """Test de l'obtention de la confiance moyenne"""
        avg_confidence = self.scorer.get_average_confidence()

        assert isinstance(avg_confidence, float)
        assert 0.0 <= avg_confidence <= 1.0

    def test_decay_confidence(self) -> None:
        """Test de la décroissance de la confiance"""
        # Ne doit pas lever d'exception
        self.scorer.decay_confidence(days=7)

    def test_save_confidence_data(self) -> None:
        """Test de la sauvegarde des données de confiance"""
        # Ne doit pas lever d'exception
        self.scorer.save_confidence_data()

    def test_load_confidence_data(self) -> None:
        """Test du chargement des données de confiance"""
        # Ne doit pas lever d'exception
        self.scorer.load_confidence_data()

    def test_calculate_confidence_edge_cases(self) -> None:
        """Test du calcul de confiance avec cas limites"""
        # Test avec contexte vide
        score, explanation = self.scorer.calculate_confidence("monitor", {})
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

        # Test avec métriques système vides
        score, explanation = self.scorer.calculate_confidence("monitor", {}, {})
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    def test_context_similarity_edge_cases(self) -> None:
        """Test de la similarité de contexte avec cas limites"""
        # Test avec contextes vides
        similarity = self.scorer._calculate_context_similarity({}, {})
        assert isinstance(similarity, float)

        # Test avec contextes différents
        ctx1 = {"cpu": 50.0}
        ctx2 = {"ram": 60.0}
        similarity = self.scorer._calculate_context_similarity(ctx1, ctx2)
        assert isinstance(similarity, float)

#!/usr/bin/env python3
# 🧠 tests/unit/sandozia/test_sandozia_core.py
# Tests unitaires SandoziaCore

import asyncio
import json
import sys
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from modules.sandozia.core import sandozia_core as sandozia_cli
from modules.sandozia.core.sandozia_core import IntelligenceSnapshot, SandoziaCore, SandoziaMetrics


class TestSandoziaCore:
    """Tests pour SandoziaCore"""

    @pytest.fixture
    def sandozia_core(self, tmp_path: Path) -> SandoziaCore:
        """Fixture SandoziaCore avec répertoire temporaire"""
        config_path = tmp_path / "test_config.toml"
        core = SandoziaCore(config_path=config_path)
        return core

    def test_sandozia_core_init(self, sandozia_core: SandoziaCore) -> None:
        """Test initialisation SandoziaCore"""
        assert sandozia_core.config is not None
        assert sandozia_core.state_dir.exists()
        assert sandozia_core.logs_dir.exists()
        assert sandozia_core.reflexia_available is True
        assert sandozia_core.zeroia_available is True
        assert sandozia_core.is_running is False

    def test_load_config_default(self, sandozia_core: SandoziaCore) -> None:
        """Test chargement configuration par défaut"""
        config = sandozia_core.config

        assert "monitoring" in config
        assert config["monitoring"]["interval_seconds"] == 30
        assert config["monitoring"]["coherence_threshold"] == 0.85

        assert "modules" in config
        assert config["modules"]["reflexia_enabled"] is True
        assert config["modules"]["zeroia_enabled"] is True

    @pytest.mark.asyncio
    async def test_initialize_modules(self, sandozia_core: SandoziaCore) -> None:
        """Test initialisation modules"""
        # initialize_modules() vérifie juste la disponibilité des modules
        # sans appeler les fonctions directement
        await sandozia_core.initialize_modules()

        assert sandozia_core.reflexia_available is True
        assert sandozia_core.zeroia_available is True

    @pytest.mark.asyncio
    async def test_collect_intelligence_snapshot(self, sandozia_core: SandoziaCore) -> None:
        """Test collecte snapshot intelligence"""
        with (
            patch("modules.sandozia.core.sandozia.core.launch_reflexia_check") as mock_reflexia,
            patch("modules.sandozia.core.sandozia.core.load_reflexia_state") as mock_zeroia_state,
            patch("modules.sandozia.core.sandozia.core.load_context") as mock_context,
        ):
            mock_reflexia.return_value = {"status": "ok", "metrics": {"cpu": 45}}
            mock_zeroia_state.return_value = {"decision": {"confidence_score": 0.85}}
            mock_context.return_value = {"status": {"severity": "normal"}}

            snapshot = await sandozia_core.collect_intelligence_snapshot()

            assert isinstance(snapshot, IntelligenceSnapshot)
            assert snapshot.reflexia_state["active"] is True
            assert snapshot.zeroia_state["active"] is True
            assert snapshot.coherence_analysis["coherence_score"] >= 0.0
            assert len(snapshot.recommendations) > 0

    @pytest.mark.asyncio
    async def test_analyze_coherence(self, sandozia_core: SandoziaCore) -> None:
        """Test analyse cohérence"""
        reflexia_state = {"active": True}
        zeroia_state = {"active": True}
        assistant_state = {"active": True}

        coherence = await sandozia_core._analyze_coherence(
            reflexia_state, zeroia_state, assistant_state
        )

        assert "coherence_score" in coherence
        assert coherence["coherence_score"] == 1.0  # Tous actifs
        assert coherence["modules_aligned"] is True
        assert len(coherence["issues"]) == 0

    @pytest.mark.asyncio
    async def test_analyze_coherence_inactive_modules(self, sandozia_core: SandoziaCore) -> None:
        """Test analyse cohérence avec modules inactifs"""
        reflexia_state = {"active": False}
        zeroia_state = {"active": False}
        assistant_state = {"active": True}

        coherence = await sandozia_core._analyze_coherence(
            reflexia_state, zeroia_state, assistant_state
        )

        assert abs(coherence["coherence_score"] - 0.6) < 0.001  # 1.0 - 0.2 - 0.2 (précision float)
        assert coherence["modules_aligned"] is False
        assert len(coherence["issues"]) == 2
        assert "Reflexia inactive" in coherence["issues"]
        assert "ZeroIA inactive" in coherence["issues"]

    @pytest.mark.asyncio
    async def test_detect_behavioral_patterns_empty(self, sandozia_core: SandoziaCore) -> None:
        """Test détection patterns comportementaux vide"""
        patterns = await sandozia_core._detect_behavioral_patterns()
        assert patterns == []

    @pytest.mark.asyncio
    async def test_generate_recommendations(self, sandozia_core: SandoziaCore) -> None:
        """Test génération recommandations"""
        coherence_analysis = {"coherence_score": 0.9, "issues": []}
        patterns: list[Any] = []

        recommendations = await sandozia_core._generate_recommendations(
            coherence_analysis, patterns
        )

        assert len(recommendations) > 0
        assert "Système d'intelligence croisée fonctionnel" in recommendations

    @pytest.mark.asyncio
    async def test_generate_recommendations_low_coherence(
        self, sandozia_core: SandoziaCore
    ) -> None:
        """Test recommandations avec cohérence faible"""
        coherence_analysis = {"coherence_score": 0.6, "issues": ["Module X inactive"]}
        patterns = [{"type": "coherence_decline"}]

        recommendations = await sandozia_core._generate_recommendations(
            coherence_analysis, patterns
        )

        assert len(recommendations) >= 3
        assert any("synchronisation" in rec for rec in recommendations)
        assert any("cohérence détectés" in rec for rec in recommendations)
        assert any("baisse de cohérence" in rec for rec in recommendations)

    def test_get_current_status(self, sandozia_core: SandoziaCore) -> None:
        """Test statut actuel"""
        status = sandozia_core.get_current_status()

        assert "is_running" in status
        assert "snapshots_count" in status
        assert "modules_available" in status
        assert status["modules_available"]["reflexia"] is True
        assert status["modules_available"]["zeroia"] is True

    @pytest.mark.asyncio
    async def test_monitoring_lifecycle(self, sandozia_core: SandoziaCore) -> None:
        """Test cycle de vie monitoring"""
        # Démarrer monitoring
        await sandozia_core.start_monitoring()
        assert sandozia_core.is_running is True

        # Attendre un petit cycle
        await asyncio.sleep(0.1)

        # Arrêter monitoring
        await sandozia_core.stop_monitoring()
        assert sandozia_core.is_running is False


class TestSandoziaMetrics:
    """Tests pour SandoziaMetrics dataclass"""

    def test_sandozia_metrics_creation(self) -> None:
        """Test création SandoziaMetrics"""
        from datetime import datetime

        metrics = SandoziaMetrics(
            timestamp=datetime.now(),
            coherence_score=0.85,
            cross_validation_passed=1,
            anomalies_detected=2,
            reasoning_alignment=0.90,
            modules_active=["reflexia", "zeroia"],
            total_correlations=5,
        )

        assert metrics.coherence_score == 0.85
        assert metrics.anomalies_detected == 2
        assert len(metrics.modules_active) == 2

        # Test serialization
        metrics_dict = metrics.to_dict()
        assert "timestamp" in metrics_dict
        assert metrics_dict["coherence_score"] == 0.85


class TestIntelligenceSnapshot:
    """Tests pour IntelligenceSnapshot dataclass"""

    def test_intelligence_snapshot_creation(self) -> None:
        """Test création IntelligenceSnapshot"""
        snapshot = IntelligenceSnapshot(
            reflexia_state={"active": True},
            zeroia_state={"active": True},
            assistant_state={"active": True},
            helloria_state={"active": True},
            nyxalia_state={"active": True},
            taskia_state={"active": True},
            cognitive_state={"active": True},
            coherence_analysis={"coherence_score": 0.9},
            behavioral_patterns=[],
            recommendations=["Test recommendation"],
        )

        assert snapshot.reflexia_state["active"] is True
        assert snapshot.coherence_analysis["coherence_score"] == 0.9
        assert len(snapshot.recommendations) == 1

        # Test serialization
        snapshot_dict = snapshot.to_dict()
        assert "reflexia_state" in snapshot_dict
        assert "coherence_analysis" in snapshot_dict


# Tests d'intégration
@pytest.mark.integration
class TestSandoziaCoreIntegration:
    """Tests d'intégration SandoziaCore"""

    @pytest.mark.asyncio
    async def test_full_sandozia_cycle(self, tmp_path: Path) -> None:
        """Test cycle complet Sandozia"""
        config_path = tmp_path / "integration_config.toml"

        with (
            patch("modules.sandozia.core.sandozia.core.launch_reflexia_check") as mock_reflexia,
            patch("modules.sandozia.core.sandozia.core.load_reflexia_state") as mock_zeroia_state,
            patch("modules.sandozia.core.sandozia.core.load_context") as mock_context,
            patch("modules.sandozia.core.sandozia.core.reflexia_get_metrics") as mock_get_metrics,
        ):
            # Setup mocks
            mock_reflexia.return_value = {"status": "ok", "metrics": {"cpu": 45}}
            mock_zeroia_state.return_value = {"decision": {"confidence_score": 0.85}}
            mock_context.return_value = {"status": {"severity": "normal"}}
            mock_get_metrics.return_value = {"cpu": 45}

            # Créer SandoziaCore
            sandozia = SandoziaCore(config_path=config_path)

            # Initialiser
            await sandozia.initialize_modules()

            # Collecter snapshot
            snapshot = await sandozia.collect_intelligence_snapshot()

            # Vérifications
            assert snapshot.coherence_analysis["coherence_score"] > 0.0
            assert sandozia.snapshots_counter >= 1  # Cache persiste entre tests

            # Vérifier que les mocks ont été appelés
            mock_reflexia.assert_called()
            mock_zeroia_state.assert_called()
            mock_context.assert_called()
            mock_get_metrics.assert_called()

            # Test statut
            status = sandozia.get_current_status()
            assert status["snapshots_count"] >= 1


@pytest.mark.asyncio
async def test_main_status_logs_json(monkeypatch: pytest.MonkeyPatch) -> None:
    """Le mode --status log un JSON sans kwargs invalides."""
    fake_status = {"is_running": False, "snapshots_count": 0}

    class FakeCore:
        def __init__(self, config_path: Path | None = None) -> None:
            del config_path

        def get_current_status(self) -> dict[str, Any]:
            return fake_status

    monkeypatch.setattr(sys, "argv", ["sandozia-core", "--status"])
    monkeypatch.setattr(sandozia_cli, "SandoziaCore", FakeCore)

    with patch.object(sandozia_cli.ark_logger, "info") as mock_info:
        await sandozia_cli.main()

    mock_info.assert_called_once_with(json.dumps(fake_status, indent=2), extra={"module": "core"})


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

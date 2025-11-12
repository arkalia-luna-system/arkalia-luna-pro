"""Tests pour sandozia/core/chronalia.py"""

import json
import time
from collections.abc import Generator
from datetime import datetime
from pathlib import Path

import pytest

from modules.sandozia.core.chronalia import (
    Chronalia,
    CognitiveCycle,
    create_chronalia,
)


@pytest.fixture
def temp_timeline_dir(tmp_path: Path) -> Generator[Path, None, None]:
    """Fixture pour créer un répertoire temporaire pour la timeline"""
    timeline_dir = tmp_path / "chronalia"
    timeline_dir.mkdir()
    yield timeline_dir


@pytest.fixture
def chronalia(temp_timeline_dir: Path) -> Chronalia:
    """Fixture pour créer une instance de Chronalia"""
    return create_chronalia(str(temp_timeline_dir))


def test_cognitive_cycle_creation() -> None:
    """Test de la création d'un cycle cognitif"""
    cycle = CognitiveCycle(
        timestamp="2024-03-20T12:00:00",
        reflexia_score=0.8,
        sandozia_health=0.9,
        contradiction=False,
        decision_pattern="normal",
        zeroia_decision="continue",
        confidence=0.95,
        system_cpu=45,
        system_ram=60,
        modules_active=["zeroia", "reflexia", "sandozia"],
        quarantined_modules=[],
        berserk_mode=False,
        cognitive_reactions=["test_reaction"],
        cycle_duration_ms=100,
        pattern_repetition_count=0,
        global_health_score=0.85,
    )

    assert cycle.timestamp == "2024-03-20T12:00:00"
    assert cycle.reflexia_score == 0.8
    assert cycle.sandozia_health == 0.9
    assert not cycle.contradiction
    assert cycle.decision_pattern == "normal"
    assert cycle.zeroia_decision == "continue"
    assert cycle.confidence == 0.95
    assert cycle.system_cpu == 45
    assert cycle.system_ram == 60
    assert cycle.modules_active == ["zeroia", "reflexia", "sandozia"]
    assert cycle.quarantined_modules == []
    assert not cycle.berserk_mode
    assert cycle.cognitive_reactions == ["test_reaction"]
    assert cycle.cycle_duration_ms == 100
    assert cycle.pattern_repetition_count == 0
    assert cycle.global_health_score == 0.85


def test_chronalia_initialization(temp_timeline_dir: Path) -> None:
    """Test de l'initialisation de Chronalia"""
    chronalia = Chronalia(str(temp_timeline_dir))

    assert chronalia.timeline_dir == temp_timeline_dir
    assert chronalia.cycles_file == temp_timeline_dir / "mind_timeline.jsonl"
    assert chronalia.patterns_file == temp_timeline_dir / "detected_patterns.jsonl"
    assert chronalia.recent_cycles == []
    assert chronalia.current_cycle_start is None


def test_chronalia_cycle_management(chronalia: Chronalia) -> None:
    """Test de la gestion des cycles"""
    # Démarrer un cycle
    cycle_id = chronalia.start_cycle()
    assert cycle_id.startswith("cycle_")
    assert chronalia.current_cycle_start is not None

    # Compléter le cycle
    context = {
        "reflexia_score": 0.8,
        "sandozia_health": 0.9,
        "contradiction": False,
        "decision_pattern": "normal",
        "zeroia_decision": "continue",
        "confidence": 0.95,
        "system_cpu": 45,
        "system_ram": 60,
        "modules_active": ["zeroia", "reflexia", "sandozia"],
        "quarantined_modules": [],
        "berserk_mode": False,
        "pattern_repetition_count": 0,
        "global_health_score": 0.85,
    }
    reactions = ["test_reaction"]

    cycle = chronalia.complete_cycle(context, reactions)

    # Vérifier le cycle
    assert isinstance(cycle, CognitiveCycle)
    assert cycle.reflexia_score == 0.8
    assert cycle.sandozia_health == 0.9
    assert not cycle.contradiction
    assert cycle.decision_pattern == "normal"
    assert cycle.cognitive_reactions == reactions

    # Vérifier la persistence
    assert chronalia.cycles_file.exists()
    with open(chronalia.cycles_file, encoding="utf-8") as f:
        saved_cycle = json.loads(f.readline())
        assert saved_cycle["reflexia_score"] == 0.8
        assert saved_cycle["sandozia_health"] == 0.9


def test_chronalia_heatmap_data(chronalia: Chronalia) -> None:
    """Test de la génération des données heatmap"""
    # Créer quelques cycles de test
    now = datetime.now()
    for i in range(3):
        context = {
            "reflexia_score": 0.8,
            "sandozia_health": 0.9,
            "contradiction": i == 1,  # Un cycle avec contradiction
            "decision_pattern": "normal",
            "zeroia_decision": "continue",
            "confidence": 0.95,
            "system_cpu": 45,
            "system_ram": 60,
            "modules_active": ["zeroia", "reflexia", "sandozia"],
            "quarantined_modules": ["test"] if i == 2 else [],  # Un cycle avec quarantaine
            "berserk_mode": i == 0,  # Un cycle en mode berserk
            "pattern_repetition_count": i,
            "global_health_score": 0.85,
        }
        chronalia.start_cycle()
        chronalia.complete_cycle(context, [f"reaction_{i}"])

    # Générer la heatmap
    heatmap = chronalia.get_heatmap_data(hours_back=1)

    # Vérifier la structure de la heatmap
    assert len(heatmap) > 0
    bucket = next(iter(heatmap.values()))
    assert bucket["cycles_count"] == 3
    assert bucket["contradictions_count"] == 1
    assert bucket["berserk_count"] == 1
    assert bucket["quarantined_modules"] == 1
    assert "continue" in bucket["decisions"]
    assert bucket["decisions"]["continue"] == 3


def test_chronalia_pattern_detection(chronalia: Chronalia) -> None:
    """Test de la détection des patterns"""
    # Créer une séquence de cycles avec un pattern de répétition
    for i in range(10):
        context = {
            "reflexia_score": 0.8,
            "sandozia_health": 0.9,
            "contradiction": False,
            "decision_pattern": "repeat",
            "zeroia_decision": "continue",  # Même décision pour créer un pattern
            "confidence": 0.95,
            "system_cpu": 45,
            "system_ram": 60,
            "modules_active": ["zeroia", "reflexia", "sandozia"],
            "quarantined_modules": [],
            "berserk_mode": False,
            "pattern_repetition_count": i,
            "global_health_score": 0.85,
        }
        chronalia.start_cycle()
        chronalia.complete_cycle(context, ["repeat_action"])
        time.sleep(0.1)  # Ajouté pour garantir des timestamps différents

    # Ajout d'un cycle final avec une décision différente pour déclencher la détection du pattern
    context = {
        "reflexia_score": 0.8,
        "sandozia_health": 0.9,
        "contradiction": False,
        "decision_pattern": "normal",
        "zeroia_decision": "stop",  # Décision différente
        "confidence": 0.95,
        "system_cpu": 45,
        "system_ram": 60,
        "modules_active": ["zeroia", "reflexia", "sandozia"],
        "quarantined_modules": [],
        "berserk_mode": False,
        "pattern_repetition_count": 0,
        "global_health_score": 0.85,
    }
    chronalia.start_cycle()
    chronalia.complete_cycle(context, ["stop_action"])
    time.sleep(0.1)

    # Vérifier que les cycles sont bien persistés
    assert chronalia.cycles_file.exists(), "Fichier cycles non créé"

    # Lire les cycles persistés pour vérifier
    with open(chronalia.cycles_file) as f:
        cycles_data = [json.loads(line.strip()) for line in f]
    assert len(cycles_data) == 11, f"Attendu 11 cycles, trouvé {len(cycles_data)}"

    # Détecter les patterns avec une fenêtre plus large
    patterns = chronalia.detect_patterns(window_minutes=60)  # 1 heure au lieu de 5 minutes

    # Vérifier les patterns détectés
    assert len(patterns) > 0, f"Aucun pattern détecté dans {len(cycles_data)} cycles persistés"
    pattern = patterns[0]
    assert pattern["pattern_type"] == "repeat"
    assert pattern["occurrences"] >= 3
    assert "confidence" in pattern
    assert "start_time" in pattern
    assert "end_time" in pattern


def test_chronalia_export_timeline(chronalia: Chronalia) -> None:
    """Test de l'export de la timeline"""
    # Créer quelques cycles
    for i in range(3):
        context = {
            "reflexia_score": 0.8,
            "sandozia_health": 0.9,
            "contradiction": False,
            "decision_pattern": "normal",
            "zeroia_decision": "continue",
            "confidence": 0.95,
            "system_cpu": 45,
            "system_ram": 60,
            "modules_active": ["zeroia", "reflexia", "sandozia"],
            "quarantined_modules": [],
            "berserk_mode": False,
            "pattern_repetition_count": i,
            "global_health_score": 0.85,
        }
        chronalia.start_cycle()
        chronalia.complete_cycle(context, [f"action_{i}"])

    # Exporter la timeline
    export_file = chronalia.export_timeline(hours_back=1)

    # Vérifier l'export
    assert export_file.exists()
    assert export_file.suffix == ".jsonl"

    # Vérifier le contenu
    cycles = []
    with open(export_file, encoding="utf-8") as f:
        for line in f:
            cycles.append(json.loads(line))

    assert len(cycles) == 3
    for i, cycle in enumerate(cycles):
        assert cycle["reflexia_score"] == 0.8
        assert cycle["sandozia_health"] == 0.9
        assert cycle["cognitive_reactions"] == [f"action_{i}"]

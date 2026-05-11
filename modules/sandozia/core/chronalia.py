#!/usr/bin/env python3
# 🕰️ modules/sandozia/core/chronalia.py
# Timeline Cognitive (Chronalia) - Mémoire continue pour apprentissage IA

"""
Chronalia - Timeline Cognitive pour Arkalia-LUNA Enhanced v3.0-phase1+

Implémente exactement tes recommandations :
- Timeline JSONL pour apprentissage machine
- Format cycle exact que tu as spécifié
- Export pour heatmap Grafana
- Détection patterns temporels
"""

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from core.ark_logger import ark_logger

MAX_CHRONALIA_JSONL_BYTES = 5 * 1024 * 1024


@dataclass
class CognitiveCycle:
    """
    🧠 Cycle cognitif - Format exact de tes recommandations

    [[cycle]]
    timestamp = "2025-06-29T23:37:14"
    reflexia_score = 1.0
    sandozia_health = 0.798
    contradiction = true
    decision_pattern = "identical"
    """

    timestamp: str
    reflexia_score: float
    sandozia_health: float
    contradiction: bool
    decision_pattern: str
    zeroia_decision: str
    confidence: float
    system_cpu: int
    system_ram: int
    modules_active: list[str]
    quarantined_modules: list[str]
    berserk_mode: bool
    cognitive_reactions: list[str]

    # Métadonnées pour analyse
    cycle_duration_ms: int | None = None
    pattern_repetition_count: int | None = None
    global_health_score: float | None = None


class Chronalia:
    """
    🕰️ Timeline Cognitive - Mémoire continue d'Arkalia

    Capture l'histoire cognitive complète selon tes spécifications :
    - Format JSONL pour apprentissage post-analyse
    - Cycles complets avec toutes métriques
    - Heatmap data pour Grafana
    - Patterns temporels automatiques
    """

    def __init__(self, timeline_dir: str = "state/chronalia") -> None:
        self.timeline_dir = Path(timeline_dir)
        self.timeline_dir.mkdir(parents=True, exist_ok=True)

        # Fichier timeline principal (JSONL)
        self.cycles_file = self.timeline_dir / "mind_timeline.jsonl"
        self.patterns_file = self.timeline_dir / "detected_patterns.jsonl"

        # État en mémoire pour performance
        self.recent_cycles: list[CognitiveCycle] = []
        self.current_cycle_start: datetime | None = None

        ark_logger.info(
            f"🕰️ Chronalia initialized - Timeline: {timeline_dir}",
            extra={"arkalia_module": "sandozia"},
        )

    def start_cycle(self) -> str:
        """🔄 Démarre un nouveau cycle cognitif"""
        self.current_cycle_start = datetime.now()
        cycle_id = f"cycle_{self.current_cycle_start.strftime('%Y%m%d_%H%M%S_%f')}"
        ark_logger.debug(
            f"🔄 Cycle cognitif démarré: {cycle_id}", extra={"arkalia_module": "sandozia"}
        )
        return cycle_id

    def complete_cycle(
        self, context: dict[str, Any], cognitive_reactions: list[str] | None = None
    ) -> CognitiveCycle:
        """✅ Complète et persiste un cycle cognitif"""

        if not self.current_cycle_start:
            ark_logger.warning(
                "⚠️ Aucun cycle en cours - création automatique",
                extra={"arkalia_module": "sandozia"},
            )
            self.start_cycle()

        # Calcul durée cycle
        if self.current_cycle_start is None:
            cycle_duration_ms = 0
        else:
            cycle_duration = datetime.now() - self.current_cycle_start
            cycle_duration_ms = int(cycle_duration.total_seconds() * 1000)

        # Construction du cycle selon tes spécifications exactes
        cycle = CognitiveCycle(
            timestamp=(
                self.current_cycle_start.isoformat()
                if self.current_cycle_start
                else datetime.now().isoformat()
            ),
            reflexia_score=context.get("reflexia_score", 0.5),
            sandozia_health=context.get("sandozia_health", 0.5),
            contradiction=context.get("contradiction", False),
            decision_pattern=context.get("decision_pattern", "normal"),
            zeroia_decision=context.get("zeroia_decision", "monitor"),
            confidence=context.get("confidence", 0.5),
            system_cpu=context.get("system_cpu", 50),
            system_ram=context.get("system_ram", 50),
            modules_active=context.get("modules_active", ["zeroia", "reflexia", "sandozia"]),
            quarantined_modules=context.get("quarantined_modules", []),
            berserk_mode=context.get("berserk_mode", False),
            cognitive_reactions=(cognitive_reactions if cognitive_reactions is not None else []),
            cycle_duration_ms=cycle_duration_ms,
            pattern_repetition_count=context.get("pattern_repetition_count", 0),
            global_health_score=context.get("global_health_score", 0.5),
        )

        # Persister au format JSONL
        self._persist_cycle(cycle)

        # Ajouter en mémoire
        self.recent_cycles.append(cycle)
        if len(self.recent_cycles) > 1000:  # Limite mémoire
            self.recent_cycles.pop(0)

        # Reset état
        self.current_cycle_start = None

        ark_logger.info(
            f"✅ Cycle cognitif complété - Durée: {cycle_duration_ms}ms",
            extra={"arkalia_module": "sandozia"},
        )
        return cycle

    def get_heatmap_data(self, hours_back: int = 24) -> dict[str, Any]:
        """📊 Génère données heatmap cognitive pour Grafana"""

        since = datetime.now() - timedelta(hours=hours_back)
        cycles = self._load_cycles_since(since)

        # Heatmap par intervalles de 5 minutes
        heatmap: dict[str, Any] = {}
        resolution_minutes = 5

        for cycle in cycles:
            cycle_time = datetime.fromisoformat(cycle.timestamp)

            # Bucket temporel
            bucket_time = cycle_time.replace(
                minute=(cycle_time.minute // resolution_minutes) * resolution_minutes,
                second=0,
                microsecond=0,
            )
            bucket_key = bucket_time.isoformat()

            if bucket_key not in heatmap:
                heatmap[bucket_key] = {
                    "timestamp": bucket_key,
                    "cycles_count": 0,
                    "avg_confidence": 0,
                    "contradictions_count": 0,
                    "berserk_count": 0,
                    "quarantined_modules": 0,
                    "modules_noise_level": 0,  # Niveau "bruit" modules
                    "decisions": {},
                }

            bucket = heatmap[bucket_key]
            bucket["cycles_count"] += 1
            bucket["avg_confidence"] += cycle.confidence

            if cycle.contradiction:
                bucket["contradictions_count"] += 1
            if cycle.berserk_mode:
                bucket["berserk_count"] += 1

            bucket["quarantined_modules"] += len(cycle.quarantined_modules)

            # Comptage décisions
            decision = cycle.zeroia_decision
            bucket["decisions"][decision] = bucket["decisions"].get(decision, 0) + 1

            # 🎯 Calcul "bruit" des modules (instabilité)
            noise = (
                len(cycle.cognitive_reactions) * 0.1
                + len(cycle.quarantined_modules) * 0.2
                + (1 if cycle.contradiction else 0) * 0.3
                + (1 if cycle.berserk_mode else 0) * 0.5
            )
            bucket["modules_noise_level"] += noise

        # Moyennes finales
        for bucket in heatmap.values():
            count = bucket["cycles_count"]
            if count > 0:
                bucket["avg_confidence"] /= count
                bucket["modules_noise_level"] /= count

        return heatmap

    def detect_patterns(self, window_minutes: int = 30) -> list[dict[str, Any]]:
        """🔍 Détecte les patterns temporels dans les cycles cognitifs"""

        since = datetime.now() - timedelta(minutes=window_minutes)
        cycles = self._load_cycles_since(since)

        if len(cycles) < 3:
            return []

        patterns = []

        # Pattern de répétition
        repeat_count = 0
        last_decision = None
        for cycle in cycles:
            if cycle.zeroia_decision == last_decision:
                repeat_count += 1
            else:
                if repeat_count >= 3:
                    patterns.append(
                        {
                            "pattern_type": "repeat",
                            "decision": last_decision,
                            "occurrences": repeat_count,
                            "confidence": min(repeat_count / 10, 1.0),
                            "start_time": cycles[cycles.index(cycle) - repeat_count].timestamp,
                            "end_time": cycles[cycles.index(cycle) - 1].timestamp,
                        }
                    )
                repeat_count = 1
                last_decision = cycle.zeroia_decision

        # Pattern de contradiction
        contradiction_cycles = [c for c in cycles if c.contradiction]
        if len(contradiction_cycles) >= 2:
            patterns.append(
                {
                    "pattern_type": "contradiction",
                    "occurrences": len(contradiction_cycles),
                    "confidence": min(len(contradiction_cycles) / 5, 1.0),
                    "start_time": contradiction_cycles[0].timestamp,
                    "end_time": contradiction_cycles[-1].timestamp,
                }
            )

        # Pattern de mode berserk
        berserk_cycles = [c for c in cycles if c.berserk_mode]
        if len(berserk_cycles) >= 1:
            patterns.append(
                {
                    "pattern_type": "berserk",
                    "occurrences": len(berserk_cycles),
                    "confidence": min(len(berserk_cycles) / 3, 1.0),
                    "start_time": berserk_cycles[0].timestamp,
                    "end_time": berserk_cycles[-1].timestamp,
                }
            )

        return patterns

    def export_timeline(self, hours_back: int = 24) -> Path:
        """📤 Exporte la timeline cognitive au format JSONL"""

        since = datetime.now() - timedelta(hours=hours_back)
        cycles = self._load_cycles_since(since)

        # Fichier d'export avec timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_file = self.timeline_dir / f"timeline_export_{timestamp}.jsonl"

        # Écrire les cycles
        with open(export_file, "w", encoding="utf-8") as f:
            for cycle in cycles:
                f.write(json.dumps(asdict(cycle), ensure_ascii=False) + "\n")

        ark_logger.info(
            f"📤 Timeline exportée: {export_file} ({len(cycles)} cycles)",
            extra={"arkalia_module": "sandozia"},
        )
        return export_file

    def _persist_cycle(self, cycle: CognitiveCycle) -> None:
        """💾 Persiste un cycle cognitif au format JSONL"""
        self._trim_log_if_needed(self.cycles_file, MAX_CHRONALIA_JSONL_BYTES)
        with open(self.cycles_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(cycle), ensure_ascii=False) + "\n")

    def _persist_pattern(self, pattern: dict[str, Any]) -> None:
        """💾 Persiste un pattern détecté"""
        self._trim_log_if_needed(self.patterns_file, MAX_CHRONALIA_JSONL_BYTES)
        with open(self.patterns_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(pattern, ensure_ascii=False) + "\n")

    def _trim_log_if_needed(self, log_path: Path, max_bytes: int) -> None:
        """Évite la croissance illimitée des fichiers JSONL de timeline."""
        if not log_path.exists():
            return
        try:
            current_size = log_path.stat().st_size
            if current_size <= max_bytes:
                return
            keep_bytes = max_bytes // 2
            with open(log_path, "rb") as src:
                src.seek(-keep_bytes, 2)
                tail = src.read()
            with open(log_path, "wb") as dst:
                dst.write(tail)
        except OSError:
            return

    def _load_cycles_since(self, since: datetime) -> list[CognitiveCycle]:
        """📖 Charge cycles depuis une date"""
        cycles: list[Any] = []

        if not self.cycles_file.exists():
            return cycles

        try:
            with self.cycles_file.open("r") as f:
                for line in f:
                    cycle_data = json.loads(line.strip())
                    cycle_time = datetime.fromisoformat(cycle_data["timestamp"])

                    if cycle_time >= since:
                        cycles.append(CognitiveCycle(**cycle_data))
        except Exception as e:
            ark_logger.error(
                f"❌ Erreur chargement cycles: {e}", extra={"arkalia_module": "sandozia"}
            )

        return cycles


# 🚀 Factory et intégration
def create_chronalia(timeline_dir: str = "state/chronalia") -> Chronalia:
    """Crée une instance de Chronalia"""
    return Chronalia(timeline_dir)


def log_cognitive_cycle(
    context: dict[str, Any], cognitive_reactions: list[str] | None = None
) -> CognitiveCycle:
    """
    🧪 INTÉGRATION SIMPLE avec ton reason_loop

    Usage dans reason_loop_enhanced.py :

    from modules.sandozia.core.chronalia import log_cognitive_cycle

    # À la fin de chaque décision :
    cycle = log_cognitive_cycle({
        "reflexia_score": 0.85,
        "sandozia_health": 0.92,
        "contradiction": False,
        "decision_pattern": "adaptive",
        "zeroia_decision": decision,
        "confidence": confidence,
        "system_cpu": cpu_usage,
        "system_ram": ram_usage,
        "modules_active": ["zeroia", "reflexia", "sandozia"],
        "quarantined_modules": quarantined_list,
        "berserk_mode": berserk_active
    }, cognitive_reactions)
    """
    chronalia = create_chronalia()

    # Auto-start cycle si pas en cours
    if not chronalia.current_cycle_start:
        chronalia.start_cycle()

    return chronalia.complete_cycle(context, cognitive_reactions)

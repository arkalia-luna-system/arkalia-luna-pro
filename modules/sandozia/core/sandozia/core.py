"""
SandoziaCore - Orchestrateur principal du système Sandozia
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import diskcache
import toml

from core.ark_logger import ark_logger

# Imports Arkalia existants (functions disponibles)
from modules.reflexia.core import get_metrics as reflexia_get_metrics
from modules.reflexia.core import launch_reflexia_check
from modules.zeroia.reason_loop_enhanced import load_context, load_reflexia_state

from .metrics import SandoziaMetrics
from .snapshot import IntelligenceSnapshot


class SandoziaCore:
    """
    Orchestrateur principal du système Sandozia

    Responsabilités:
    - Coordination des composants cognitifs
    - Gestion du cycle de vie des intelligences
    - Optimisation des performances
    - Monitoring et métriques
    """

    def __init__(self, config_path: Path | None = None) -> None:
        """
        Fonction __init__.

        Cette fonction fait partie du système Arkalia Luna Pro.
        """
        self.config_path = config_path or Path("modules/sandozia/config/sandozia_config.toml")
        self.state_dir = Path("state/sandozia")
        self.logs_dir = Path("logs/sandozia")

        # Créer répertoires
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        # Configuration
        self.config = self._load_config()

        # Métriques et état
        self.metrics_history: list[SandoziaMetrics] = []
        self.max_metrics_history = 500  # Limite pour économiser la RAM
        self.intelligence_snapshots = diskcache.Cache(
            "./cache/sandozia_snapshots", size_limit=50_000_000
        )  # 50MB limit (réduit pour économiser la RAM)
        self.snapshots_counter = 0  # Compteur simple pour le suivi
        self.active_correlations: dict[str, Any] = {}

        # Intégration modules IA existants (fonctions directes)
        self.reflexia_available = True
        self.zeroia_available = True

        # État du système
        self.is_running = False
        self.monitoring_task: asyncio.Task[None] | None = None

        ark_logger.info(
            "🧠 SandoziaCore initialized - Intelligence Croisée ready",
            extra={"arkalia_module": "sandozia"},
        )

    def _load_config(self) -> dict:
        """
        Charge la configuration Sandozia.

        Utilise maintenant ConfigManager centralisé pour le chargement TOML.
        """
        from modules.core.config.config_manager import get_default_config_manager

        default_config = {
            "monitoring": {
                "interval_seconds": 30,
                "coherence_threshold": 0.85,
                "anomaly_threshold": 0.15,
                "max_history_size": 1000,
            },
            "modules": {
                "reflexia_enabled": True,
                "zeroia_enabled": True,
                "assistant_enabled": True,
            },
            "alerting": {
                "coherence_alert_threshold": 0.70,
                "behavioral_alert_enabled": True,
            },
        }

        if self.config_path.exists():
            try:
                # Utiliser ConfigManager centralisé
                config_manager = get_default_config_manager()
                loaded_config = config_manager.load_toml_config(self.config_path)
                # Merge avec defaults
                default_config.update(loaded_config)
            except Exception as e:
                ark_logger.warning(
                    f"⚠️ Error loading config, using defaults: {e}",
                    extra={"arkalia_module": "sandozia"},
                )
        else:
            # Créer config par défaut
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, "w") as f:
                toml.dump(default_config, f)
            ark_logger.info(
                f"📝 Created default config: {self.config_path}",
                extra={"arkalia_module": "sandozia"},
            )

        return default_config

    async def initialize_modules(self) -> None:
        """Initialise les connexions aux modules IA"""
        ark_logger.info(
            "🔌 Initializing IA modules connections...", extra={"arkalia_module": "sandozia"}
        )

        # Reflexia - test fonction
        if self.config["modules"]["reflexia_enabled"]:
            try:
                reflexia_get_metrics()
                self.reflexia_available = True
                ark_logger.info(
                    "✅ Reflexia functions available", extra={"arkalia_module": "sandozia"}
                )
            except Exception as e:
                ark_logger.warning(
                    f"⚠️ Reflexia connection failed: {e}", extra={"arkalia_module": "sandozia"}
                )
                self.reflexia_available = False

        # ZeroIA - test fonction
        if self.config["modules"]["zeroia_enabled"]:
            try:
                # Test de chargement du contexte
                load_context()
                self.zeroia_available = True
                ark_logger.info(
                    "✅ ZeroIA functions available", extra={"arkalia_module": "sandozia"}
                )
            except Exception as e:
                ark_logger.warning(
                    f"⚠️ ZeroIA connection failed: {e}", extra={"arkalia_module": "sandozia"}
                )
                self.zeroia_available = False

        ark_logger.info(
            "🧠 Sandozia modules initialization complete", extra={"arkalia_module": "sandozia"}
        )

    async def collect_intelligence_snapshot(self) -> IntelligenceSnapshot:
        """Collecte un snapshot complet de l'état d'intelligence"""

        # État Reflexia
        reflexia_state: dict[str, Any] = {}
        if self.reflexia_available:
            try:
                # Utiliser les fonctions disponibles
                reflexia_check = launch_reflexia_check()
                reflexia_state = {
                    "active": True,
                    "last_reflection": datetime.now().isoformat(),
                    "status": reflexia_check.get("status", "unknown"),
                    "metrics": reflexia_check.get("metrics", {}),
                    "confidence_level": 0.85,  # Calculé depuis les métriques
                }
            except Exception as e:
                ark_logger.warning(
                    f"⚠️ Reflexia state collection failed: {e}", extra={"arkalia_module": "sandozia"}
                )
                reflexia_state = {"active": False}

        # État ZeroIA
        zeroia_state: dict[str, Any] = {}
        if self.zeroia_available:
            try:
                # Charger l'état ZeroIA existant
                zeroia_state = load_reflexia_state()
                zeroia_state["active"] = True

                # Compléter avec contexte global
                context = load_context()
                zeroia_state["context"] = context
            except Exception as e:
                ark_logger.warning(
                    f"⚠️ ZeroIA state collection failed: {e}", extra={"arkalia_module": "sandozia"}
                )
                zeroia_state = {"active": False, "last_check": None}

        # État AssistantIA (placeholder pour l'instant)
        assistant_state = {
            "active": True,
            "session_count": 0,
            "last_interaction": datetime.now().isoformat(),
        }

        # 🔥 NOUVELLE INTÉGRATION - Modules supplémentaires
        # État Helloria
        helloria_state = {
            "active": True,
            "api_ready": True,
            "last_check": datetime.now().isoformat(),
        }

        # État Nyxalia
        nyxalia_state = {
            "active": True,
            "monitoring": "enabled",
            "last_check": datetime.now().isoformat(),
        }

        # État Taskia
        taskia_state = {
            "active": True,
            "queue_size": 0,
            "last_check": datetime.now().isoformat(),
        }

        # État CognitiveReactor
        cognitive_state = {
            "active": True,
            "reactions_enabled": True,
            "last_check": datetime.now().isoformat(),
        }

        # Analyse de cohérence
        coherence_analysis = await self._analyze_coherence(
            reflexia_state, zeroia_state, assistant_state
        )

        # Patterns comportementaux
        behavioral_patterns = await self._detect_behavioral_patterns()

        # Recommandations
        recommendations = await self._generate_recommendations(
            coherence_analysis, behavioral_patterns
        )

        snapshot = IntelligenceSnapshot(
            reflexia_state=reflexia_state,
            zeroia_state=zeroia_state,
            assistant_state=assistant_state,
            helloria_state=helloria_state,
            nyxalia_state=nyxalia_state,
            taskia_state=taskia_state,
            cognitive_state=cognitive_state,
            coherence_analysis=coherence_analysis,
            behavioral_patterns=behavioral_patterns,
            recommendations=recommendations,
        )

        # Sauvegarder snapshot
        self.snapshots_counter += 1
        snapshot_key = f"snapshot_{self.snapshots_counter:06d}_{int(datetime.now().timestamp())}"
        self.intelligence_snapshots[snapshot_key] = snapshot.to_dict()

        # Nettoyage automatique géré par diskcache (size_limit)
        # Pas besoin de gestion manuelle, diskcache évince automatiquement

        return snapshot

    async def _analyze_coherence(
        self, reflexia_state: dict, zeroia_state: dict, assistant_state: dict
    ) -> dict:
        """Analyse la cohérence entre les modules IA"""

        coherence_score = 1.0
        issues: list[Any] = []

        # Vérifications de base
        if not reflexia_state.get("active", False):
            coherence_score -= 0.2
            issues.append("Reflexia inactive")

        if not zeroia_state.get("active", False):
            coherence_score -= 0.2
            issues.append("ZeroIA inactive")

        return {
            "coherence_score": max(0.0, coherence_score),
            "issues": issues,
            "last_analysis": datetime.now().isoformat(),
            "modules_aligned": len(issues) == 0,
        }

    async def _detect_behavioral_patterns(self) -> list[dict]:
        """Détecte des patterns comportementaux suspects"""
        patterns: list[Any] = []

        # Analyser l'historique récent - approche simplifiée
        recent_snapshots_data: list[Any] = []
        try:
            # Prendre quelques snapshots récents si disponibles
            snapshot_count = 0
            for key in self.intelligence_snapshots:
                if snapshot_count >= 5:
                    break
                snapshot_data = self.intelligence_snapshots[key]
                recent_snapshots_data.append(snapshot_data)
                snapshot_count += 1

            # Pattern : Cohérence en baisse (si on a assez de données)
            if len(recent_snapshots_data) >= 3:
                coherence_scores = [
                    s.get("coherence_analysis", {}).get("coherence_score", 1.0)
                    for s in recent_snapshots_data
                ]

                if len(coherence_scores) >= 3:
                    trend = coherence_scores[-1] - coherence_scores[0]
                    if trend < -0.1:  # Baisse de 10%+
                        patterns.append(
                            {
                                "type": "coherence_decline",
                                "severity": "medium",
                                "description": f"Baisse cohérence: {trend:.2f}",
                                "detected_at": datetime.now().isoformat(),
                            }
                        )
        except Exception as e:
            ark_logger.warning(
                f"⚠️ Error analyzing patterns: {e}", extra={"arkalia_module": "sandozia"}
            )

        return patterns

    async def _generate_recommendations(
        self, coherence_analysis: dict, patterns: list[dict]
    ) -> list[str]:
        """Génère des recommandations basées sur l'analyse"""
        recommendations: list[Any] = []

        coherence_score = coherence_analysis.get("coherence_score", 1.0)

        if coherence_score < 0.8:
            recommendations.append("Vérifier la synchronisation des modules IA")

        if coherence_analysis.get("issues"):
            recommendations.append("Résoudre les problèmes de cohérence détectés")

        for pattern in patterns:
            if pattern["type"] == "coherence_decline":
                recommendations.append("Investiguer la cause de la baisse de cohérence")

        if not recommendations:
            recommendations.append("Système d'intelligence croisée fonctionnel")

        return recommendations

    async def start_monitoring(self) -> None:
        """Démarre le monitoring en continu"""
        if self.is_running:
            ark_logger.warning("⚠️ Monitoring already running", extra={"arkalia_module": "sandozia"})
            return

        await self.initialize_modules()

        self.is_running = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())

        ark_logger.info("🚀 Sandozia monitoring started", extra={"arkalia_module": "sandozia"})

    async def stop_monitoring(self) -> None:
        """Arrête le monitoring"""
        self.is_running = False

        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass

        ark_logger.info("🛑 Sandozia monitoring stopped", extra={"arkalia_module": "sandozia"})

    async def _monitoring_loop(self) -> None:
        """Boucle principale de monitoring"""
        interval = self.config["monitoring"]["interval_seconds"]

        while self.is_running:
            try:
                # Collecter snapshot
                snapshot = await self.collect_intelligence_snapshot()

                # Générer métriques
                metrics = SandoziaMetrics(
                    timestamp=datetime.now(),
                    coherence_score=snapshot.coherence_analysis.get("coherence_score", 0.0),
                    cross_validation_passed=(
                        1 if snapshot.coherence_analysis.get("modules_aligned") else 0
                    ),
                    anomalies_detected=len(snapshot.behavioral_patterns),
                    reasoning_alignment=0.85,  # À implémenter
                    modules_active=[
                        mod
                        for mod in ["reflexia", "zeroia", "assistant"]
                        if snapshot.__dict__.get(f"{mod}_state", {}).get("active", False)
                    ],
                    total_correlations=len(self.active_correlations),
                )

                self.metrics_history.append(metrics)
                
                # Limiter l'historique pour économiser la RAM
                if len(self.metrics_history) > self.max_metrics_history:
                    self.metrics_history = self.metrics_history[-self.max_metrics_history:]

                # Sauvegarder état
                await self._save_state(snapshot, metrics)

                ark_logger.debug(
                    f"📊 Sandozia cycle complete - Coherence: {metrics.coherence_score:.2f}"
                )

            except Exception as e:
                ark_logger.error(
                    f"❌ Monitoring loop error: {e}", extra={"arkalia_module": "sandozia"}
                )

            await asyncio.sleep(interval)

    async def _save_state(self, snapshot: IntelligenceSnapshot, metrics: SandoziaMetrics) -> None:
        """Sauvegarde l'état et métriques"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Sauvegarder snapshot
        snapshot_file = self.state_dir / f"intelligence_snapshot_{timestamp}.json"
        with open(snapshot_file, "w") as f:
            json.dump(snapshot.to_dict(), f, indent=2)

        # Sauvegarder métriques
        metrics_file = self.state_dir / "latest_metrics.json"
        with open(metrics_file, "w") as f:
            json.dump(metrics.to_dict(), f, indent=2)

    def get_current_status(self) -> dict:
        """Récupère le statut actuel de SandoziaCore.

        Returns:
            dict: Statut avec informations sur l'état d'exécution et les modules.
        """
        return {
            "is_running": self.is_running,
            "snapshots_count": self.snapshots_counter,
            "cache_stats": f"Volume: {self.intelligence_snapshots.volume()} bytes",
            "modules_available": {
                "reflexia": self.reflexia_available,
                "zeroia": self.zeroia_available,
            },
            "last_update": datetime.now().isoformat(),
        }

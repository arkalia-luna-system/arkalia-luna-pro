#!/usr/bin/env python3
"""
📊 State Manager - Gestionnaire d'état pour ZeroIA

Extrait de reason_loop_enhanced.py pour simplifier la maintenance.
Responsabilité : Persistance et gestion des états.
"""

import json
import textwrap
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import toml

from core.ark_logger import ark_logger
from modules.utils.helpers import save_json_if_changed, save_toml_if_changed
from modules.zeroia.utils.backup import save_backup

# === Chemins par défaut ===
STATE_PATH = Path("modules/zeroia/state/zeroia_state.toml")
DASHBOARD_PATH = Path("state/zeroia_dashboard.json")
DEFAULT_CONTRADICTION_LOG = Path("logs/zeroia_contradictions.log")


class StateManager:
    """Gestionnaire d'état pour ZeroIA"""

    def __init__(self):
        self.state_path = STATE_PATH
        self.dashboard_path = DASHBOARD_PATH
        self.contradiction_log_path = DEFAULT_CONTRADICTION_LOG

    def ensure_parent_dir(self, path: Path) -> None:
        """Assure que le répertoire parent existe"""
        path.parent.mkdir(parents=True, exist_ok=True)

    def persist_state_enhanced(
        self,
        decision: str,
        score: float,
        ctx: dict,
        state_path_override: Path | None = None,
    ) -> None:
        """
        Persiste l'état ZeroIA avec métadonnées enrichies

        Args:
            decision: Décision prise
            score: Score de confiance
            ctx: Contexte global
            state_path_override: Chemin alternatif pour l'état
        """
        try:
            state_path = state_path_override or self.state_path
            self.ensure_parent_dir(state_path)

            current_time = datetime.now().isoformat()

            # État enrichi avec métadonnées
            state_data = {
                "last_decision": decision,
                "confidence_score": score,
                "timestamp": current_time,
                "context_snapshot": {
                    "cpu": ctx.get("status", {}).get("cpu", 0),
                    "ram": ctx.get("status", {}).get("ram", 0),
                    "severity": ctx.get("status", {}).get("severity", "unknown"),
                    "system_status": ctx.get("system_status", "unknown"),
                },
                "metadata": {
                    "version": "3.0.0-enhanced",
                    "source": "zeroia_state_manager",
                    "decision_engine": "enhanced",
                    "circuit_breaker": "closed",
                    "error_recovery": "enabled",
                },
                "performance": {
                    "decision_time": datetime.now().isoformat(),
                    "processing_duration": 0.0,  # Sera mis à jour par le caller
                },
            }

            # Sauvegarder avec validation
            save_toml_if_changed(state_data, str(state_path))

            # Backup automatique
            try:
                save_backup()
            except Exception as e:
                logger.warning(f"Backup échoué: {e}")

            logger.info(f"✅ État persisté: {decision} (score: {score:.2f})")

        except Exception as e:
            logger.error(f"❌ Erreur persistance état: {e}")
            raise

    def update_dashboard_enhanced(
        self,
        decision: str,
        score: float,
        ctx: dict,
        dashboard_path_override: Path | None = None,
    ) -> None:
        """
        Met à jour le dashboard avec les dernières décisions

        Args:
            decision: Décision prise
            score: Score de confiance
            ctx: Contexte global
            dashboard_path_override: Chemin alternatif pour le dashboard
        """
        try:
            dashboard_path = dashboard_path_override or self.dashboard_path
            self.ensure_parent_dir(dashboard_path)

            current_time = datetime.now().isoformat()

            # Charger le dashboard existant ou créer un nouveau
            if dashboard_path.exists():
                try:
                    with open(dashboard_path, encoding="utf-8") as f:
                        dashboard = json.load(f)
                except Exception:
                    dashboard = {"decisions": [], "metadata": {}}
            else:
                dashboard = {"decisions": [], "metadata": {}}

            # Ajouter la nouvelle décision
            decision_entry = {
                "timestamp": current_time,
                "decision": decision,
                "confidence": score,
                "context": {
                    "cpu": ctx.get("status", {}).get("cpu", 0),
                    "ram": ctx.get("status", {}).get("ram", 0),
                    "severity": ctx.get("status", {}).get("severity", "unknown"),
                },
            }

            dashboard["decisions"].append(decision_entry)

            # Garder seulement les 100 dernières décisions
            if len(dashboard["decisions"]) > 100:
                dashboard["decisions"] = dashboard["decisions"][-100:]

            # Mettre à jour les métadonnées
            dashboard["metadata"] = {
                "last_update": current_time,
                "total_decisions": len(dashboard["decisions"]),
                "version": "3.0.0-enhanced",
                "source": "zeroia_dashboard_manager",
            }

            # Sauvegarder
            save_json_if_changed(dashboard, str(dashboard_path))

            logger.debug(f"📊 Dashboard mis à jour: {decision}")

        except Exception as e:
            logger.error(f"❌ Erreur mise à jour dashboard: {e}")
            # Ne pas faire échouer le processus principal

    def check_for_ia_conflict_enhanced(
        self,
        reflexia_decision: str,
        zeroia_decision: str,
        log_path: Path | None = None,
    ) -> bool:
        """
        Vérifie les conflits entre Reflexia et ZeroIA

        Args:
            reflexia_decision: Décision de Reflexia
            zeroia_decision: Décision de ZeroIA
            log_path: Chemin du log de contradictions

        Returns:
            bool: True si conflit détecté
        """
        try:
            log_path = log_path or self.contradiction_log_path
            self.ensure_parent_dir(log_path)

            # Détecter les contradictions
            contradictions = []

            # Reflexia critique mais ZeroIA normal
            if reflexia_decision == "critical" and zeroia_decision == "normal":
                contradictions.append("Reflexia critique vs ZeroIA normal")

            # Reflexia normal mais ZeroIA critique
            elif reflexia_decision == "normal" and zeroia_decision == "critical":
                contradictions.append("Reflexia normal vs ZeroIA critique")

            # Décisions opposées
            elif reflexia_decision != zeroia_decision:
                contradictions.append(
                    f"Décisions divergentes: {reflexia_decision} vs {zeroia_decision}"
                )

            # Logger les contradictions
            if contradictions:
                current_time = datetime.now().isoformat()
                conflict_log = {
                    "timestamp": current_time,
                    "reflexia_decision": reflexia_decision,
                    "zeroia_decision": zeroia_decision,
                    "contradictions": contradictions,
                    "severity": "warning",
                }

                try:
                    with open(log_path, "a", encoding="utf-8") as f:
                        f.write(json.dumps(conflict_log) + "\n")

                    logger.warning(f"⚠️ Conflit IA détecté: {contradictions}")
                    return True

                except Exception as e:
                    logger.error(f"Erreur log conflit: {e}")

            return False

        except Exception as e:
            logger.error(f"❌ Erreur vérification conflit: {e}")
            return False

    def load_current_state(self) -> dict:
        """Charge l'état actuel de ZeroIA"""
        try:
            if self.state_path.exists():
                with open(self.state_path, encoding="utf-8") as f:
                    return toml.load(f)
            else:
                logger.warning(f"État ZeroIA non trouvé: {self.state_path}")
                return {
                    "last_decision": "unknown",
                    "confidence_score": 0.0,
                    "timestamp": datetime.now().isoformat(),
                }
        except Exception as e:
            logger.error(f"Erreur chargement état: {e}")
            return {
                "last_decision": "error",
                "confidence_score": 0.0,
                "timestamp": datetime.now().isoformat(),
            }

    def get_dashboard_summary(self) -> dict:
        """Récupère un résumé du dashboard"""
        try:
            if not self.dashboard_path.exists():
                return {"total_decisions": 0, "last_decision": "none"}

            with open(self.dashboard_path, encoding="utf-8") as f:
                dashboard = json.load(f)

            decisions = dashboard.get("decisions", [])
            if not decisions:
                return {"total_decisions": 0, "last_decision": "none"}

            last_decision = decisions[-1]
            return {
                "total_decisions": len(decisions),
                "last_decision": last_decision.get("decision", "unknown"),
                "last_confidence": last_decision.get("confidence", 0.0),
                "last_timestamp": last_decision.get("timestamp", ""),
            }

        except Exception as e:
            logger.error(f"Erreur résumé dashboard: {e}")
            return {"total_decisions": 0, "last_decision": "error"}

    def cleanup_old_logs(self, max_age_days: int = 30) -> None:
        """Nettoie les anciens logs"""
        try:
            if not self.contradiction_log_path.exists():
                return

            cutoff_time = datetime.now().timestamp() - (max_age_days * 24 * 3600)

            # Lire et filtrer les logs
            with open(self.contradiction_log_path, encoding="utf-8") as f:
                lines = f.readlines()

            # Garder seulement les logs récents
            recent_lines = []
            for line in lines:
                try:
                    log_entry = json.loads(line.strip())
                    timestamp = datetime.fromisoformat(log_entry.get("timestamp", "")).timestamp()
                    if timestamp > cutoff_time:
                        recent_lines.append(line)
                except Exception:
                    # Garder les lignes non-JSON
                    recent_lines.append(line)

            # Réécrire le fichier
            with open(self.contradiction_log_path, "w", encoding="utf-8") as f:
                f.writelines(recent_lines)

            logger.info(f"🧹 Logs nettoyés: {len(lines) - len(recent_lines)} entrées supprimées")

        except Exception as e:
            logger.error(f"Erreur nettoyage logs: {e}")

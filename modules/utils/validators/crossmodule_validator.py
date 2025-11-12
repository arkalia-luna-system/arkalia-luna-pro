#!/usr/bin/env python3
# 🧠 modules/utils/validators/crossmodule_validator.py
# CrossModuleValidator - Validation croisée entre modules IA (unifié depuis Sandozia)

"""
CrossModuleValidator - Validation Cohérence Inter-Modules

Vérifie la cohérence entre :
- Reflexia (auto-réflexion)
- ZeroIA (détection contradictions)
- AssistantIA (interactions utilisateur)

Détecte :
- Désalignements temporels
- Contradictions logiques
- Incohérences de scores/confiance
- Dérives comportementales
"""

import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

import toml

from core.ark_logger import ark_logger


class ValidationLevel(Enum):
    """Niveaux de validation pour les résultats de validation croisée.

    Attributes:
        CRITICAL: Problème critique détecté.
        WARNING: Avertissement détecté.
        INFO: Information détectée.
        OK: Validation réussie.
    """

    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"
    OK = "ok"


@dataclass
class ValidationResult:
    """Résultat d'une validation croisée entre modules.

    Attributes:
        level: Niveau de validation.
        module_source: Module source de la validation.
        module_target: Module cible de la validation.
        message: Message de validation.
        details: Détails supplémentaires.
        timestamp: Horodatage de la validation.
    """

    level: ValidationLevel
    module_source: str
    module_target: str
    message: str
    details: dict[str, Any]
    timestamp: datetime
    suggested_action: str | None = None

    def to_dict(self) -> dict:
        """Convertit le résultat en dictionnaire."""
        return {
            "level": self.level.value,
            "module_source": self.module_source,
            "module_target": self.module_target,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
            "suggested_action": self.suggested_action,
        }


class CrossModuleValidator:
    """
    Validateur cross-modules unifié

    Valide la cohérence entre modules :
    - Vérification des interfaces
    - Validation des données partagées
    - Détection des incohérences
    - Rapport de validation
    """

    def __init__(self, config: dict | None = None) -> None:
        """Initialise le validateur."""
        self.config = config or {
            "validation_timeout": 30,
            "strict_mode": False,
            "auto_fix": False,
            "max_validation_history": 100,
        }
        self.validation_history: list[dict] = []
        self.known_issues: dict[str, list] = {}
        self.state_paths: dict[str, Path] = {
            "reflexia": Path("state/reflexia_state.toml"),
            "zeroia": Path("state/zeroia_state.toml"),
            "assistantia": Path("state/assistantia_state.toml"),
            "helloria": Path("state/helloria_state.toml"),
        }
        self.state_cache: dict[str, dict] = {}
        ark_logger.info("🔍 CrossModuleValidator initialized", extra={"arkalia_module": "utils"})

    def load_module_states(self) -> dict[str, dict]:
        """Charge les états de tous les modules."""
        states = {}
        for module_name, state_path in self.state_paths.items():
            try:
                if state_path.exists():
                    with open(state_path, encoding="utf-8") as f:
                        states[module_name] = toml.load(f)
                        self.state_cache[module_name] = states[module_name]
                else:
                    states[module_name] = {}
            except Exception as e:
                ark_logger.warning(
                    f"Erreur chargement état {module_name}: {e}", extra={"arkalia_module": "utils"}
                )
                states[module_name] = {}
        return states

    def validate_module_interfaces(self, modules_data: dict[str, dict]) -> dict[str, Any]:
        """Valide les interfaces entre modules."""
        ark_logger.info(
            "🔍 Starting cross-module interface validation...", extra={"arkalia_module": "utils"}
        )

        validation_result = {
            "status": "completed",
            "modules_checked": list(modules_data.keys()),
            "issues_found": [],
            "warnings": [],
            "passed": True,
            "timestamp": datetime.now().isoformat(),
        }

        # Vérifier les interfaces communes
        for module1, data1 in modules_data.items():
            for module2, data2 in modules_data.items():
                if module1 >= module2:
                    continue

                interface_issues = self._validate_interface(module1, data1, module2, data2)
                validation_result["issues_found"].extend(interface_issues)  # type: ignore

        # Déterminer le statut global
        if validation_result["issues_found"]:
            validation_result["passed"] = False

        # Enregistrer dans l'historique
        self.validation_history.append(validation_result)
        if len(self.validation_history) > 50:
            self.validation_history = self.validation_history[-50:]

        ark_logger.info(
            f"✅ Cross-module validation completed: {validation_result['passed']}",
            extra={"arkalia_module": "utils"},
        )
        return validation_result

    def _validate_interface(
        self, module1: str, data1: dict, module2: str, data2: dict
    ) -> list[dict]:
        """Valide l'interface entre deux modules."""
        issues = []

        # Vérifier les types de données partagées
        shared_keys = set(data1.keys()) & set(data2.keys())
        for key in shared_keys:
            type1 = type(data1[key])
            type2 = type(data2[key])

            if type1 != type2:
                issues.append(
                    {
                        "type": "type_mismatch",
                        "module1": module1,
                        "module2": module2,
                        "key": key,
                        "type1": str(type1),
                        "type2": str(type2),
                        "severity": "error",
                    }
                )

        # Vérifier les valeurs incohérentes
        for key in shared_keys:
            if isinstance(data1[key], int | float) and isinstance(data2[key], int | float):
                if abs(data1[key] - data2[key]) > 0.01:  # Tolérance pour les floats
                    issues.append(
                        {
                            "type": "value_mismatch",
                            "module1": module1,
                            "module2": module2,
                            "key": key,
                            "value1": data1[key],
                            "value2": data2[key],
                            "severity": "warning",
                        }
                    )

        return issues

    def validate_data_consistency(self, modules_data: dict[str, dict]) -> dict[str, Any]:
        """Valide la cohérence des données entre modules."""
        ark_logger.info(
            "🔍 Starting data consistency validation...", extra={"arkalia_module": "utils"}
        )

        consistency_result: dict[str, Any] = {
            "status": "completed",
            "consistency_score": 1.0,
            "inconsistencies": [],
            "timestamp": datetime.now().isoformat(),
        }

        # Analyser la cohérence des données
        all_keys: set[str] = set()
        for data in modules_data.values():
            all_keys.update(data.keys())

        for key in all_keys:
            values = []
            for module_name, data in modules_data.items():
                if key in data:
                    values.append((module_name, data[key]))

            if len(values) > 1:
                inconsistency = self._check_value_consistency(key, values)
                if inconsistency:
                    consistency_result["inconsistencies"].append(inconsistency)

        # Calculer le score de cohérence
        total_checks = len(all_keys)
        failed_checks = len(consistency_result["inconsistencies"])
        if total_checks > 0:
            consistency_result["consistency_score"] = 1.0 - (failed_checks / total_checks)

        score = consistency_result["consistency_score"]
        ark_logger.info(
            f"✅ Data consistency validation completed: {score:.2f}",
            extra={"arkalia_module": "utils"},
        )
        return consistency_result

    def _check_value_consistency(self, key: str, values: list[tuple[str, Any]]) -> dict | None:
        """Vérifie la cohérence des valeurs pour une clé."""
        if not values:
            return None

        # Vérifier si toutes les valeurs sont identiques
        first_value = values[0][1]
        inconsistent_modules = []

        for module_name, value in values:
            if value != first_value:
                inconsistent_modules.append({"module": module_name, "value": value})

        if inconsistent_modules:
            return {
                "key": key,
                "expected_value": first_value,
                "inconsistent_modules": inconsistent_modules,
            }
        return None

    def validate_temporal_coherence(self, modules_data: dict[str, dict]) -> list[ValidationResult]:
        """Valide la cohérence temporelle entre modules."""
        results = []
        timestamps: dict[str, datetime] = {}

        # Extraire les timestamps
        for module_name, data in modules_data.items():
            if "last_update" in data:
                try:
                    if isinstance(data["last_update"], str):
                        timestamps[module_name] = datetime.fromisoformat(data["last_update"])
                    else:
                        timestamps[module_name] = data["last_update"]
                except Exception:
                    pass

        # Vérifier les désalignements temporels
        if len(timestamps) > 1:
            max_ts = max(timestamps.values())
            min_ts = min(timestamps.values())
            diff = (max_ts - min_ts).total_seconds()

            if diff > 300:  # 5 minutes
                results.append(
                    ValidationResult(
                        level=ValidationLevel.WARNING,
                        module_source="system",
                        module_target="system",
                        message=f"Désalignement temporel détecté: {diff:.0f}s",
                        details={
                            "max": max_ts.isoformat(),
                            "min": min_ts.isoformat(),
                            "diff": diff,
                        },
                        timestamp=datetime.now(),
                        suggested_action="Synchroniser les mises à jour des modules",
                    )
                )

        return results

    def validate_confidence_coherence(
        self, modules_data: dict[str, dict]
    ) -> list[ValidationResult]:
        """Valide la cohérence des scores de confiance."""
        results = []
        confidence_scores: dict[str, float] = {}

        # Extraire les scores de confiance
        for module_name, data in modules_data.items():
            if "confidence" in data:
                try:
                    confidence_scores[module_name] = float(data["confidence"])
                except (ValueError, TypeError):
                    pass

        # Vérifier les incohérences
        if len(confidence_scores) > 1:
            scores = list(confidence_scores.values())
            avg_score = sum(scores) / len(scores)
            max_diff = max(scores) - min(scores)

            if max_diff > 0.3:  # Écart significatif
                results.append(
                    ValidationResult(
                        level=ValidationLevel.WARNING,
                        module_source="system",
                        module_target="system",
                        message=f"Écart de confiance important: {max_diff:.2f}",
                        details={
                            "scores": confidence_scores,
                            "average": avg_score,
                            "max_diff": max_diff,
                        },
                        timestamp=datetime.now(),
                        suggested_action="Vérifier la cohérence des calculs de confiance",
                    )
                )

        return results

    def validate_logical_consistency(self, modules_data: dict[str, dict]) -> list[ValidationResult]:
        """Valide la cohérence logique entre modules."""
        results = []

        # Vérifier les contradictions logiques
        for module1, data1 in modules_data.items():
            for module2, data2 in modules_data.items():
                if module1 >= module2:
                    continue

                # Exemple: vérifier si deux modules ont des statuts contradictoires
                if "status" in data1 and "status" in data2:
                    status1 = data1["status"]
                    status2 = data2["status"]

                    # Logique de contradiction (exemple)
                    if status1 == "active" and status2 == "inactive":
                        if module1 in ["zeroia", "reflexia"] and module2 in ["zeroia", "reflexia"]:
                            results.append(
                                ValidationResult(
                                    level=ValidationLevel.CRITICAL,
                                    module_source=module1,
                                    module_target=module2,
                                    message="Contradiction de statut détectée",
                                    details={"status1": status1, "status2": status2},
                                    timestamp=datetime.now(),
                                    suggested_action="Vérifier la cohérence des statuts",
                                )
                            )

        return results

    def validate_behavioral_patterns(self, modules_data: dict[str, dict]) -> list[ValidationResult]:
        """Valide les patterns comportementaux."""
        results = []

        # Détecter les dérives comportementales
        for module_name, data in modules_data.items():
            if "metrics" in data and isinstance(data["metrics"], dict):
                metrics = data["metrics"]

                # Vérifier les métriques anormales
                if "error_rate" in metrics:
                    error_rate = float(metrics.get("error_rate", 0))
                    if error_rate > 0.1:  # 10% d'erreurs
                        results.append(
                            ValidationResult(
                                level=ValidationLevel.WARNING,
                                module_source=module_name,
                                module_target="system",
                                message=f"Taux d'erreur élevé: {error_rate:.2%}",
                                details={"error_rate": error_rate},
                                timestamp=datetime.now(),
                                suggested_action="Investigation requise",
                            )
                        )

        return results

    def run_full_validation(self) -> dict[str, Any]:
        """Exécute une validation complète croisée entre tous les modules."""
        ark_logger.info("🔍 Starting cross-module validation...", extra={"arkalia_module": "utils"})

        # Charger les états
        states = self.load_module_states()

        # Exécuter toutes les validations
        all_results: list[Any] = []

        all_results.extend(self.validate_temporal_coherence(states))
        all_results.extend(self.validate_confidence_coherence(states))
        all_results.extend(self.validate_logical_consistency(states))
        all_results.extend(self.validate_behavioral_patterns(states))

        # Ajouter à l'historique
        self.validation_history.extend(all_results)

        # Limiter l'historique
        max_history = self.config["max_validation_history"]
        if len(self.validation_history) > max_history:
            self.validation_history = self.validation_history[-max_history:]

        # Calculer le score global de cohérence
        if all_results:
            critical_count = sum(1 for r in all_results if r.level == ValidationLevel.CRITICAL)
            warning_count = sum(1 for r in all_results if r.level == ValidationLevel.WARNING)

            # Score basé sur la gravité des issues
            coherence_score = max(0.0, 1.0 - (critical_count * 0.3 + warning_count * 0.1))
        else:
            coherence_score = 1.0

        # Résumé
        summary = {
            "timestamp": datetime.now().isoformat(),
            "coherence_score": coherence_score,
            "total_validations": len(all_results),
            "issues_by_level": {
                "critical": sum(1 for r in all_results if r.level == ValidationLevel.CRITICAL),
                "warning": sum(1 for r in all_results if r.level == ValidationLevel.WARNING),
                "info": sum(1 for r in all_results if r.level == ValidationLevel.INFO),
                "ok": sum(1 for r in all_results if r.level == ValidationLevel.OK),
            },
            "modules_analyzed": list(states.keys()),
            "validation_results": [r.to_dict() for r in all_results],
            "overall_status": (
                "healthy"
                if coherence_score > 0.8
                else "degraded" if coherence_score > 0.6 else "critical"
            ),
        }

        ark_logger.info(
            f"✅ Cross-module validation complete - Score: {coherence_score:.3f}",
            extra={"arkalia_module": "utils"},
        )
        return summary

    def validate_cross_modules(self, active_modules: list[str] | None = None) -> dict[str, Any]:
        """
        Méthode principale de validation croisée - Interface pour Orchestrateur

        Args:
            active_modules: Liste des modules actifs à valider

        Returns:
            Dict avec résultats de validation
        """
        try:
            # Charger les états et effectuer la validation
            validation_results = self.run_full_validation()

            # Adapter la validation selon les modules actifs
            if active_modules:
                ark_logger.info(
                    f"🔍 Validating cross-module coherence for: {', '.join(active_modules)}",
                    extra={"arkalia_module": "utils"},
                )

            # Simplifier la réponse pour l'orchestrateur
            return {
                "status": "success",
                "active_modules": active_modules or [],
                "total_validations": len(validation_results.get("validation_results", [])),
                "critical_count": len(
                    [
                        r
                        for r in validation_results.get("validation_results", [])
                        if r.get("level") == "critical"
                    ]
                ),
                "warning_count": len(
                    [
                        r
                        for r in validation_results.get("validation_results", [])
                        if r.get("level") == "warning"
                    ]
                ),
                "coherence_score": validation_results.get("coherence_score", 0.8),
                "score": validation_results.get(
                    "coherence_score", 0.8
                ),  # Alias pour l'orchestrateur
                "details": validation_results,
            }
        except Exception as e:
            ark_logger.error(
                f"❌ CrossModule validation error: {e}", extra={"arkalia_module": "utils"}
            )
            return {"status": "error", "error": str(e), "coherence_score": 0.0}

    def get_validation_report(self) -> dict[str, Any]:
        """Génère un rapport complet de validation."""
        recent_validations = self.validation_history[-50:] if self.validation_history else []

        return {
            "total_validations_run": len(self.validation_history),
            "recent_validations": [
                v.to_dict() if hasattr(v, "to_dict") else v for v in recent_validations
            ],
            "current_config": self.config,
            "modules_monitored": list(self.state_paths.keys()),
        }


# CLI pour test
if __name__ == "__main__":
    validator = CrossModuleValidator()
    results = validator.run_full_validation()
    print(json.dumps(results, indent=2, default=str))

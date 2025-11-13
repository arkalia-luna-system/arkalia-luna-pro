#!/usr/bin/env python3
"""
🌕 TaskIA Task Processor Service
📝 Service de traitement des tâches selon le principe SRP
🔧 Version: 2.0.0
👤 Author: Athalia
📅 Created: 2025-01-27
"""

from typing import Any

from core.ark_logger import ark_logger
from modules.taskia.interfaces.formatter_interface import IFormatter
from modules.taskia.interfaces.task_processor_interface import ITaskProcessor


class TaskProcessor(ITaskProcessor):
    """
    Service de traitement des tâches.

    Principe SRP : Responsabilité unique = traiter les tâches
    Principe DIP : Dépend des interfaces, pas des implémentations
    """

    def __init__(self, formatter: IFormatter):
        """
        Initialise le processeur de tâches.

        Args:
            formatter: Formateur injecté (DIP)
        """
        self._formatter = formatter

    def process(self, context: dict[str, Any]) -> str:
        """
        Traite le contexte et génère un résultat formaté.

        Args:
            context: Contexte à traiter

        Returns:
            Résultat formaté
        """
        ark_logger.info(
            f"Traitement du contexte avec {self._formatter.get_format_type()}",
            extra={"arkalia_module": "taskia"},
        )

        if not self.validate_context(context):
            raise ValueError("Contexte invalide")

        return self._formatter.format(context)

    def validate_context(self, context: dict[str, Any]) -> bool:
        """
        Valide le contexte d'entrée.

        Args:
            context: Contexte à valider

        Returns:
            True si le contexte est valide
        """
        if not isinstance(context, dict):
            ark_logger.error(
                "Le contexte doit être un dictionnaire", extra={"arkalia_module": "taskia"}
            )
            return False

        if not context:
            ark_logger.warning("Contexte vide", extra={"arkalia_module": "taskia"})
            return False

        return True

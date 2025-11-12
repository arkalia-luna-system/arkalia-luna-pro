#!/usr/bin/env python3
"""
🌕 TaskIA Logger Service
📝 Service de logging selon le principe SRP - Utilise ark_logger
🔧 Version: 2.1.0
👤 Author: Athalia
📅 Created: 2025-01-27
Updated: 2025-11-12 - Unifié avec ark_logger
"""

from typing import Optional

from core.ark_logger import ark_logger


class LoggerService:
    """
    Service de logging centralisé utilisant ark_logger.

    Principe SRP : Responsabilité unique = gérer les logs
    Principe DIP : Fournit des loggers injectables
    Note: Utilise maintenant ark_logger en interne pour cohérence
    """

    def __init__(self, module_name: str = "taskia"):
        """
        Initialise le service de logging.

        Args:
            module_name: Nom du module pour le logger
        """
        self._module_name = module_name

    def get_logger(self):
        """
        Retourne le logger configuré (compatibilité API).

        Returns:
            Logger configuré (ark_logger)
        """
        return ark_logger

    def set_level(self, level: int) -> None:
        """
        Définit le niveau de logging.

        Args:
            level: Niveau de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        Note: ark_logger gère le niveau globalement
        """
        # ark_logger gère le niveau globalement, cette méthode est conservée pour compatibilité
        pass

    def log_operation(self, operation: str, details: str | None = None) -> None:
        """
        Log une opération avec des détails optionnels.

        Args:
            operation: Nom de l'opération
            details: Détails optionnels
        """
        message = f"🌕 {operation}"
        if details:
            message += f" - {details}"

        ark_logger.info(message, extra={"arkalia_module": self._module_name})

    def log_error(self, error: str, context: str | None = None) -> None:
        """
        Log une erreur avec un contexte optionnel.

        Args:
            error: Message d'erreur
            context: Contexte optionnel
        """
        message = f"❌ {error}"
        if context:
            message += f" - Contexte: {context}"

        ark_logger.error(message, extra={"arkalia_module": self._module_name})

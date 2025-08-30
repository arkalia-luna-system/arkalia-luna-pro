#!/usr/bin/env python3
"""
🌕 Arkalia-LUNA - Logger Centralisé
📝 Logger structuré conforme cahier des charges v4.0
🔧 Version: 2.8.0
👤 Author: Athalia
📅 Created: 2025-06-27
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


# Configuration du logger centralisé Arkalia
class ArkaliaLogger:
    """Logger centralisé Arkalia conforme cahier des charges v4.0"""

    def __init__(self, module_name: str = "arkalia"):
        self.module_name = module_name
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """Configure le logger selon les standards Arkalia"""
        logger = logging.getLogger(f"ark_logger.{self.module_name}")

        # Éviter la duplication des handlers
        if logger.handlers:
            return logger

        logger.setLevel(logging.INFO)

        # Format structuré conforme cahier des charges
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - [%(arkalia_module)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Handler console
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # Handler fichier avec rotation
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        file_handler = logging.handlers.RotatingFileHandler(
            log_dir / f"{self.module_name}.log", maxBytes=10 * 1024 * 1024, backupCount=5  # 10MB
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        return logger

    def info(self, message: str, extra: dict[str, Any] | None = None) -> None:
        """Log info avec contexte structuré"""
        if extra:
            extra["arkalia_module"] = self.module_name
            extra["timestamp"] = datetime.now().isoformat()
        self.logger.info(message, extra=extra)

    def error(self, message: str, extra: dict[str, Any] | None = None) -> None:
        """Log error avec contexte structuré"""
        if extra:
            extra["arkalia_module"] = self.module_name
            extra["timestamp"] = datetime.now().isoformat()
        self.logger.error(message, extra=extra)

    def warning(self, message: str, extra: dict[str, Any] | None = None) -> None:
        """Log warning avec contexte structuré"""
        if extra:
            extra["arkalia_module"] = self.module_name
            extra["timestamp"] = datetime.now().isoformat()
        self.logger.warning(message, extra=extra)

    def debug(self, message: str, extra: dict[str, Any] | None = None) -> None:
        """Log debug avec contexte structuré"""
        if extra:
            extra["arkalia_module"] = self.module_name
            extra["timestamp"] = datetime.now().isoformat()
        self.logger.debug(message, extra=extra)

    def critical(self, message: str, extra: dict[str, Any] | None = None) -> None:
        """Log critical avec contexte structuré"""
        if extra:
            extra["arkalia_module"] = self.module_name
            extra["timestamp"] = datetime.now().isoformat()
        self.logger.critical(message, extra=extra)


# Instance globale du logger Arkalia
ark_logger = ArkaliaLogger("core")


"""
Logger principal pour Arkalia-LUNA
"""


# Configuration du logger principal
def setup_logger(
    name: str = "arkalia", level: int = logging.INFO, log_file: Path | None = None
) -> logging.Logger:
    """Configure et retourne le logger principal Arkalia."""

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Éviter les handlers dupliqués
    if logger.handlers:
        return logger

    # Format personnalisé
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Handler console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Handler fichier si spécifié
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


# Logger principal global
ark_logger = setup_logger("arkalia")


# Loggers spécialisés
def get_module_logger(module_name: str) -> logging.Logger:
    """Retourne un logger spécialisé pour un module."""
    return logging.getLogger(f"arkalia.{module_name}")


def get_performance_logger() -> logging.Logger:
    """Retourne un logger pour les métriques de performance."""
    return logging.getLogger("arkalia.performance")


def get_security_logger() -> logging.Logger:
    """Retourne un logger pour les événements de sécurité."""
    return logging.getLogger("arkalia.security")


# Fonctions utilitaires
def log_function_call(func_name: str, module: str = "core"):
    """Décorateur pour logger les appels de fonction."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            logger = get_module_logger(module)
            logger.debug(f"🧪 {func_name} déclaré")
            return func(*args, **kwargs)

        return wrapper

    return decorator


def log_error(error: Exception, context: str = "", module: str = "core"):
    """Log une erreur avec contexte."""
    logger = get_module_logger(module)
    logger.error(f"❌ Erreur dans {context}: {error}")


def log_success(message: str, module: str = "core"):
    """Log un succès."""
    logger = get_module_logger(module)
    logger.info(f"✅ {message}")


def log_warning(message: str, module: str = "core"):
    """Log un avertissement."""
    logger = get_module_logger(module)
    logger.warning(f"⚠️ {message}")


def log_info(message: str, module: str = "core"):
    """Log une information."""
    logger = get_module_logger(module)
    logger.info(f"ℹ️ {message}")


# Export des fonctions principales
__all__ = [
    "ark_logger",
    "setup_logger",
    "get_module_logger",
    "get_performance_logger",
    "get_security_logger",
    "log_function_call",
    "log_error",
    "log_success",
    "log_warning",
    "log_info",
]

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
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

_SENSITIVE_EXTRA_MARKERS = (
    "password",
    "secret",
    "token",
    "api_key",
    "authorization",
    "credential",
    "private_key",
    "access_key",
)


# Configuration du logger centralisé Arkalia
class ArkaliaLogger:
    """Logger centralisé Arkalia conforme cahier des charges v4.0"""

    def __init__(self, module_name: str = "arkalia"):
        self.module_name = module_name
        self.logger = self._setup_logger()

    def _prepare_extra(self, extra: dict[str, Any] | None) -> dict[str, Any]:
        """Normalise le contexte et masque les clés potentiellement sensibles."""
        prepared: dict[str, Any] = dict(extra or {})
        if "module" in prepared and "arkalia_module" not in prepared:
            prepared["arkalia_module"] = prepared.pop("module")
        prepared.setdefault("arkalia_module", self.module_name)
        prepared["timestamp"] = datetime.now().isoformat()
        for key in list(prepared):
            lowered = key.lower()
            if any(marker in lowered for marker in _SENSITIVE_EXTRA_MARKERS):
                prepared[key] = "redacted"
        return prepared

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

        # Handler fichier avec rotation (désactivé si volume/logs non inscriptible, ex. Docker CI)
        log_dir = Path("logs")
        try:
            log_dir.mkdir(exist_ok=True)
            file_handler = logging.handlers.RotatingFileHandler(
                log_dir / f"{self.module_name}.log",
                maxBytes=10 * 1024 * 1024,
                backupCount=5,  # 10MB
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except OSError:
            log_path = log_dir / f"{self.module_name}.log"
            logger.warning(
                "Écriture fichier logs indisponible (%s), logs console uniquement",
                str(log_path),
                extra={"arkalia_module": self.module_name},
            )

        return logger

    def info(self, message: str, extra: dict[str, Any] | None = None) -> None:
        """Log info avec contexte structuré"""
        self.logger.info(message, extra=self._prepare_extra(extra))

    def error(self, message: str, extra: dict[str, Any] | None = None) -> None:
        """Log error avec contexte structuré"""
        self.logger.error(message, extra=self._prepare_extra(extra))

    def warning(self, message: str, extra: dict[str, Any] | None = None) -> None:
        """Log warning avec contexte structuré"""
        self.logger.warning(message, extra=self._prepare_extra(extra))

    def debug(self, message: str, extra: dict[str, Any] | None = None) -> None:
        """Log debug avec contexte structuré"""
        self.logger.debug(message, extra=self._prepare_extra(extra))

    def critical(self, message: str, extra: dict[str, Any] | None = None) -> None:
        """Log critical avec contexte structuré"""
        self.logger.critical(message, extra=self._prepare_extra(extra))


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
def log_function_call(func_name: str, module: str = "core") -> Any:
    """Décorateur pour logger les appels de fonction."""

    def decorator(func: Any) -> Any:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            logger = get_module_logger(module)
            logger.debug(f"🧪 {func_name} déclaré")
            return func(*args, **kwargs)

        return wrapper

    return decorator


def log_error(error: Exception, context: str = "", module: str = "core") -> None:
    """Log une erreur avec contexte."""
    logger = get_module_logger(module)
    logger.error(f"❌ Erreur dans {context}: {error}")


def log_success(message: str, module: str = "core") -> None:
    """Log un succès."""
    logger = get_module_logger(module)
    logger.info(f"✅ {message}")


def log_warning(message: str, module: str = "core") -> None:
    """Log un avertissement."""
    logger = get_module_logger(module)
    logger.warning(f"⚠️ {message}")


def log_info(message: str, module: str = "core") -> None:
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

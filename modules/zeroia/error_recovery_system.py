#!/usr/bin/env python3
"""
Compatibility wrapper for ZeroIA Error Recovery.

Canonical implementation now lives in modules.utils.error_recovery.core.
"""

from __future__ import annotations

import warnings
from enum import Enum
from typing import Any

from modules.utils.error_recovery.core import (
    ErrorRecoverySystem as SharedErrorRecoverySystem,
)
from modules.utils.error_recovery.core import ErrorType as SharedErrorType


class ZeroIAError(Exception):
    """Exception de base pour ZeroIA."""


class CognitiveOverloadError(ZeroIAError):
    """Surcharge cognitive detectee."""


class DecisionIntegrityError(ZeroIAError):
    """Erreur d'integrite des decisions."""


class SystemRebootRequired(ZeroIAError):
    """Redemarrage systeme requis."""


class ErrorType(Enum):
    """Type local pour compatibilite ZeroIA."""

    TIMEOUT = "timeout"
    MEMORY = "memory"
    CONTRADICTION = "contradiction"
    UNKNOWN = "unknown"


def _to_shared_error_type(error_type: ErrorType) -> SharedErrorType:
    try:
        return SharedErrorType(error_type.value)
    except ValueError:
        return SharedErrorType.UNKNOWN


class ErrorRecoverySystem(SharedErrorRecoverySystem):
    """
    Compat layer that delegates to the shared recovery system.
    """

    def __init__(self) -> None:
        warnings.warn(
            "modules.zeroia.error_recovery_system is deprecated; "
            "use modules.utils.error_recovery.core instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__()

    async def handle_error(
        self, error_type: SharedErrorType | ErrorType, error_message: str
    ) -> dict[str, Any]:
        if isinstance(error_type, SharedErrorType):
            shared_error_type = error_type
        else:
            shared_error_type = _to_shared_error_type(error_type)
        return await super().handle_error(shared_error_type, error_message)


def create_error_recovery_system() -> ErrorRecoverySystem:
    """Create a compatibility instance."""
    return ErrorRecoverySystem()

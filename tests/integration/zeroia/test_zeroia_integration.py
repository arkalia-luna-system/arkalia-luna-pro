"""
🧪 Test d'intégration minimal pour ZeroIA
"""

import pytest

from modules.zeroia import ZeroIACoordinator


def test_zeroia_integration_basic():
    zeroia = ZeroIACoordinator()
    status = zeroia.get_status()
    assert status is not None

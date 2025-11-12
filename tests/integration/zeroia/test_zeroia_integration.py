"""
🧪 Test d'intégration minimal pour ZeroIA
"""

import pytest

from modules.zeroia import ZeroIACoordinator


@pytest.mark.asyncio
async def test_zeroia_integration_basic() -> None:
    zeroia = ZeroIACoordinator()
    status = await zeroia.get_status()
    assert status is not None

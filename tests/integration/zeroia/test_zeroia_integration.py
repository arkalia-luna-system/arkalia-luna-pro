"""
🧪 Test d'intégration minimal pour ZeroIA
"""

from unittest.mock import AsyncMock, patch

import pytest

from modules.zeroia import ZeroIACoordinator


@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_zeroia_integration_basic() -> None:
    zeroia = ZeroIACoordinator()
    # Mock assess_system_health pour éviter les blocages
    with patch.object(
        zeroia.graceful_degradation, "assess_system_health", new_callable=AsyncMock
    ) as mock_health:
        mock_health.return_value = 0.9  # Santé système excellente
        status = await zeroia.get_status()
        assert status is not None

"""Test the CozyLife Battery init."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from custom_components.cozylife_battery import async_setup_entry, async_unload_entry
from custom_components.cozylife_battery.const import DOMAIN, CONF_HOST

@pytest.mark.asyncio
async def test_setup_unload_entry():
    """Test setup and unload."""
    hass = MagicMock()
    hass.data = {}
    hass.config_entries.async_forward_entry_setups = AsyncMock(return_value=True)
    hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)

    entry = MagicMock()
    entry.entry_id = "test_entry"
    entry.data = {CONF_HOST: "192.168.1.100"}

    mock_api_cls = MagicMock()
    mock_api = mock_api_cls.return_value
    mock_api.update = AsyncMock(return_value={})

    # Mock DataUpdateCoordinator
    with patch("custom_components.cozylife_battery.DataUpdateCoordinator") as mock_coordinator_cls, \
         patch("custom_components.cozylife_battery.CozyLifeAPI", return_value=mock_api):

        mock_coordinator = mock_coordinator_cls.return_value
        mock_coordinator.async_config_entry_first_refresh = AsyncMock()

        assert await async_setup_entry(hass, entry) is True

        assert DOMAIN in hass.data
        assert entry.entry_id in hass.data[DOMAIN]
        assert hass.data[DOMAIN][entry.entry_id]["api"] == mock_api

        # Test unload
        assert await async_unload_entry(hass, entry) is True
        assert entry.entry_id not in hass.data[DOMAIN]

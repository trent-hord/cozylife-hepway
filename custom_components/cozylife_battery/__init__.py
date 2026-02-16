"""The CozyLife Battery integration."""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import CozyLifeAPI
from .const import DOMAIN, CONF_HOST

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.SWITCH, Platform.SELECT]

MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds between retry attempts

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up CozyLife Battery from a config entry."""

    host = entry.data[CONF_HOST]
    api = CozyLifeAPI(host)

    async def async_update_data():
        """Fetch data from API endpoint, retrying on failure."""
        last_err = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                return await api.update()
            except Exception as err:
                last_err = err
                if attempt < MAX_RETRIES:
                    _LOGGER.warning(
                        "Update attempt %d/%d failed for %s: %s — retrying in %ds",
                        attempt,
                        MAX_RETRIES,
                        host,
                        err,
                        RETRY_DELAY,
                    )
                    await asyncio.sleep(RETRY_DELAY)
        _LOGGER.error(
            "All %d update attempts failed for %s: %s",
            MAX_RETRIES,
            host,
            last_err,
        )
        raise UpdateFailed(f"Error communicating with API after {MAX_RETRIES} attempts: {last_err}")

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="cozylife_battery",
        update_method=async_update_data,
        update_interval=timedelta(seconds=30),
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "api": api
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok

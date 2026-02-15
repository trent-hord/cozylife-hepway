"""Select platform for CozyLife Battery."""
from __future__ import annotations

from typing import Any

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the CozyLife select."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    api = data["api"]

    async_add_entities(
        [
            CozyLifeSelect(
                coordinator,
                api,
                entry,
                "47",
                "AC Charging Power",
            ),
        ]
    )


class CozyLifeSelect(CoordinatorEntity, SelectEntity):
    """Representation of a CozyLife Select."""

    _attr_options = ["800W", "1200W", "1500W", "1800W"]

    def __init__(
        self,
        coordinator,
        api,
        entry,
        attribute_id,
        name,
    ):
        """Initialize the select."""
        super().__init__(coordinator)
        self._api = api
        self._attribute_id = attribute_id
        self._attr_name = name
        self._attr_unique_id = f"{entry.entry_id}_{attribute_id}"
        self._attr_has_entity_name = True
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="CozyLife / Hepway",
            model="Portable Battery",
        )

    @property
    def current_option(self) -> str | None:
        """Return the current option."""
        val = self.coordinator.data.get(self._attribute_id)
        if val is None:
            return None

        # Ensure we handle both int and str values from API
        try:
            val_int = int(val)
        except ValueError:
            return None

        option = f"{val_int}W"
        if option in self.options:
            return option
        return None

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        value = int(option.replace("W", ""))
        await self._api.set_state(self._attribute_id, value)
        await self.coordinator.async_request_refresh()

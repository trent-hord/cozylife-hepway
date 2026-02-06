"""Switch platform for CozyLife Battery."""
from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
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
    """Set up the CozyLife switch."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    api = data["api"]

    async_add_entities(
        [
            CozyLifeSwitch(
                coordinator,
                api,
                entry,
                "1",
                "AC Power",
            ),
        ]
    )


class CozyLifeSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of a CozyLife Switch."""

    def __init__(
        self,
        coordinator,
        api,
        entry,
        attribute_id,
        name,
    ):
        """Initialize the switch."""
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
    def is_on(self) -> bool | None:
        """Return true if switch is on."""
        val = self.coordinator.data.get(self._attribute_id)
        return bool(val)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        await self._api.set_state(self._attribute_id, 1)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        await self._api.set_state(self._attribute_id, 0)
        await self.coordinator.async_request_refresh()

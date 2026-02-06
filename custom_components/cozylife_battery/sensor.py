"""Sensor platform for CozyLife Battery."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfPower, UnitOfTime
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
    """Set up the CozyLife sensors."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]

    async_add_entities(
        [
            CozyLifeSensor(
                coordinator,
                entry,
                "4",
                "Output Watts",
                SensorDeviceClass.POWER,
                UnitOfPower.WATT,
                SensorStateClass.MEASUREMENT,
                "mdi:flash-arrow-right",
            ),
            CozyLifeSensor(
                coordinator,
                entry,
                "21",
                "Incoming Watts",
                SensorDeviceClass.POWER,
                UnitOfPower.WATT,
                SensorStateClass.MEASUREMENT,
                "mdi:flash-arrow-left",
            ),
            CozyLifeSensor(
                coordinator,
                entry,
                "30",
                "Minutes Remaining",
                SensorDeviceClass.DURATION,
                UnitOfTime.MINUTES,
                SensorStateClass.MEASUREMENT,
                "mdi:battery-clock",
            ),
        ]
    )


class CozyLifeSensor(CoordinatorEntity, SensorEntity):
    """Representation of a CozyLife Sensor."""

    def __init__(
        self,
        coordinator,
        entry: ConfigEntry,
        attribute_id,
        name,
        device_class,
        native_unit_of_measurement,
        state_class,
        icon,
    ):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entry = entry
        self._attribute_id = attribute_id
        self._attr_name = name
        self._attr_unique_id = f"{entry.entry_id}_{attribute_id}"
        self._attr_device_class = device_class
        self._attr_native_unit_of_measurement = native_unit_of_measurement
        self._attr_state_class = state_class
        self._attr_icon = icon

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get(self._attribute_id)

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.entry.entry_id)},
            name="CozyLife Battery",
            manufacturer="CozyLife",
            model="Portable Battery",
        )

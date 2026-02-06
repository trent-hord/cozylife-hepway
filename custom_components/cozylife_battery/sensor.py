"""Sensor platform for CozyLife Battery."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfPower, UnitOfTime
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
                "2",
                "Battery Level",
                SensorDeviceClass.BATTERY,
                PERCENTAGE,
                SensorStateClass.MEASUREMENT,
            ),
            CozyLifeSensor(
                coordinator,
                entry,
                "4",
                "Output Watts",
                SensorDeviceClass.POWER,
                UnitOfPower.WATT,
                SensorStateClass.MEASUREMENT,
            ),
            CozyLifeSensor(
                coordinator,
                entry,
                "21",
                "Incoming Watts",
                SensorDeviceClass.POWER,
                UnitOfPower.WATT,
                SensorStateClass.MEASUREMENT,
            ),
            CozyLifeSensor(
                coordinator,
                entry,
                "30",
                "Minutes Remaining",
                SensorDeviceClass.DURATION,
                UnitOfTime.MINUTES,
                SensorStateClass.MEASUREMENT,
            ),
        ]
    )


class CozyLifeSensor(CoordinatorEntity, SensorEntity):
    """Representation of a CozyLife Sensor."""

    def __init__(
        self,
        coordinator,
        entry,
        attribute_id,
        name,
        device_class,
        native_unit_of_measurement,
        state_class,
    ):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attribute_id = attribute_id
        self._attr_name = name
        self._attr_unique_id = f"{entry.entry_id}_{attribute_id}"
        self._attr_device_class = device_class
        self._attr_native_unit_of_measurement = native_unit_of_measurement
        self._attr_state_class = state_class
        self._attr_has_entity_name = True
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="CozyLife / Hepway",
            model="Portable Battery",
        )

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get(self._attribute_id)

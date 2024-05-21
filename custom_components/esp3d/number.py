from aioesphomeapi import NumberMode
from .esp3d import Esp3d
from homeassistant.components.number import NumberEntity
from .const import DOMAIN
import logging
from .event_emitter import Event

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add sensors for passed config_entry in HA."""
    esp3d: Esp3d = hass.data[DOMAIN][config_entry.entry_id]
    new_devices = [
        Nozzle(esp3d),
        Bed(esp3d),
    ]
    async_add_entities(new_devices)


class Base(NumberEntity):
    def __init__(self, esp3d: Esp3d):
        self.esp3d = esp3d
        self._attr_has_entity_name = True
        self._attr_native_unit_of_measurement = "°C"
        self.esp3d.event_emitter.on(Event.CONNECTION_STATUS, self.set_attr_available)

    @property
    def unique_id(self) -> str:
        assert self.name
        return self.esp3d._host + "_" + self.name

    def set_attr_native_value(self, value):
        self._attr_native_value = value
        self.schedule_update_ha_state()

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.esp3d._host)},
        )

    def set_attr_available(self, is_connected: bool):
        if self._attr_available != is_connected:
            self._attr_available = is_connected
            self.schedule_update_ha_state()


class Nozzle(Base):
    def __init__(self, esp3d: Esp3d):
        super().__init__(esp3d)
        self._attr_name = "Nozzle"
        self._attr_icon = "mdi:printer-3d-nozzle-outline"
        self._attr_device_class = "temperature"
        self._attr_native_unit_of_measurement = "°C"
        self._attr_native_min_value = 0
        self._attr_native_max_value = 300
        self._attr_native_step = 1
        self._attr_mode = NumberMode.BOX
        self.esp3d.event_emitter.on(Event.NOZZLE_TARGET, self.set_attr_native_value)

    async def async_set_native_value(self, value: float) -> None:
        await self.esp3d.async_send("M104 S" + str(value))
        await self.esp3d.async_send("M105")


class Bed(Base):
    def __init__(self, esp3d: Esp3d):
        super().__init__(esp3d)
        self._attr_name = "Bed"
        self._attr_icon = "mdi:square-circle-outline"
        self._attr_device_class = "temperature"
        self._attr_native_unit_of_measurement = "°C"
        self._attr_native_min_value = 0
        self._attr_native_max_value = 100
        self._attr_native_step = 1
        self._attr_mode = NumberMode.BOX
        self.esp3d.event_emitter.on(Event.BED_TARGET, self.set_attr_native_value)

    async def async_set_native_value(self, value: float) -> None:
        await self.esp3d.async_send("M140 S" + str(value))
        await self.esp3d.async_send("M105")

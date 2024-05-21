from .event_emitter import Event
from .const import DOMAIN
from .esp3d import Esp3d
import logging

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.components.sensor import SensorEntity
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
        NozzleCurrent(esp3d),
        NozzleTarget(esp3d),
        BedCurrent(esp3d),
        BedTarget(esp3d),
        X(esp3d),
        Y(esp3d),
        Z(esp3d),
        E(esp3d),
        PlannerBuffer(esp3d),
        BlockBuffer(esp3d),
        CurrentByte(esp3d),
        TotalBytes(esp3d),
        PrintProgress(esp3d),
        NotificationEntity(esp3d),
    ]
    async_add_entities(new_devices)


class Base(SensorEntity):
    def __init__(self, esp3d: Esp3d):
        self.esp3d = esp3d
        self._attr_has_entity_name = True
        self.esp3d.event_emitter.on(Event.CONNECTION_STATUS, self.set_attr_available)

    @property
    def unique_id(self) -> str:
        assert self.name
        return self.esp3d._host + "_" + self.name

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.esp3d._host)},
        )

    def set_attr_available(self, is_connected: bool):
        if self._attr_available != is_connected:
            self._attr_available = is_connected
            self.schedule_update_ha_state()

    def set_attr_native_value(self, value):
        self._attr_native_value = value
        self.schedule_update_ha_state()


class NozzleCurrent(Base):
    def __init__(self, esp3d: Esp3d):
        super().__init__(esp3d)
        self._attr_name = "Nozzle"
        self._attr_icon = "mdi:printer-3d-nozzle"
        self._attr_native_unit_of_measurement = "°C"
        self.esp3d.event_emitter.on(Event.NOZZLE_CURRENT, self.set_attr_native_value)


class NozzleTarget(Base):
    def __init__(self, esp3d: Esp3d):
        super().__init__(esp3d)
        self._attr_name = "Nozzle target"
        self._attr_icon = "mdi:printer-3d-nozzle-outline"
        self._attr_native_unit_of_measurement = "°C"
        self.esp3d.event_emitter.on(Event.NOZZLE_TARGET, self.set_attr_native_value)


class BedCurrent(Base):
    def __init__(self, esp3d: Esp3d):
        super().__init__(esp3d)
        self._attr_name = "Bed"
        self._attr_icon = "mdi:square-circle"
        self._attr_native_unit_of_measurement = "°C"
        self.esp3d.event_emitter.on(Event.BED_CURRENT, self.set_attr_native_value)


class BedTarget(Base):
    def __init__(self, esp3d: Esp3d):
        super().__init__(esp3d)
        self._attr_name = "Bed Target"
        self._attr_icon = "mdi:square-circle-outline"
        self._attr_native_unit_of_measurement = "°C"
        self.esp3d.event_emitter.on(Event.BED_TARGET, self.set_attr_native_value)


class X(Base):
    def __init__(self, esp3d: Esp3d):
        super().__init__(esp3d)
        self._attr_name = "X"
        self._attr_icon = "mdi:axis-y-arrow"
        self._attr_native_unit_of_measurement = "mm"
        self.esp3d.event_emitter.on(Event.X, self.set_attr_native_value)


class Y(Base):
    def __init__(self, esp3d: Esp3d):
        super().__init__(esp3d)
        self._attr_name = "Y"
        self._attr_icon = "mdi:axis-x-arrow"
        self._attr_native_unit_of_measurement = "mm"
        self.esp3d.event_emitter.on(Event.Y, self.set_attr_native_value)


class Z(Base):
    def __init__(self, esp3d: Esp3d):
        super().__init__(esp3d)
        self._attr_name = "Z"
        self._attr_icon = "mdi:axis-z-arrow"
        self._attr_native_unit_of_measurement = "mm"
        self.esp3d.event_emitter.on(Event.Z, self.set_attr_native_value)


class E(Base):
    def __init__(self, esp3d: Esp3d):
        super().__init__(esp3d)
        self._attr_name = "E"
        self._attr_icon = "mdi:circle-double"
        self._attr_native_unit_of_measurement = "mm"
        self.esp3d.event_emitter.on(Event.E, self.set_attr_native_value)


class PlannerBuffer(Base):
    def __init__(self, esp3d: Esp3d):
        super().__init__(esp3d)
        self._attr_name = "Planner buffer"
        self._attr_icon = "mdi:database-outline"
        self._attr_native_unit_of_measurement = ""
        self.esp3d.event_emitter.on(Event.PLANNER_BUFFER, self.set_attr_native_value)


class BlockBuffer(Base):
    def __init__(self, esp3d: Esp3d):
        super().__init__(esp3d)
        self._attr_name = "Block buffer"
        self._attr_icon = "mdi:database-outline"
        self._attr_native_unit_of_measurement = ""
        self.esp3d.event_emitter.on(Event.BLOCK_BUFFER, self.set_attr_native_value)


class CurrentByte(Base):
    def __init__(self, esp3d: Esp3d):
        super().__init__(esp3d)
        self._attr_name = "Current byte"
        self._attr_icon = "mdi:expand-all-outline"
        self._attr_native_unit_of_measurement = "bytes"
        self.esp3d.event_emitter.on(Event.CURRENT_BYTE, self.set_attr_native_value)


class TotalBytes(Base):
    def __init__(self, esp3d: Esp3d):
        super().__init__(esp3d)
        self._attr_name = "Total bytes"
        self._attr_icon = "mdi:expand-all"
        self._attr_native_unit_of_measurement = "bytes"
        self.esp3d.event_emitter.on(Event.TOTAL_BYTES, self.set_attr_native_value)


class PrintProgress(Base):
    def __init__(self, esp3d: Esp3d):
        super().__init__(esp3d)
        self._attr_name = "Print progress"
        self._attr_icon = "mdi:progress-check"
        self._attr_native_unit_of_measurement = "%"
        self._attr_suggested_display_precision = 2
        self.esp3d.event_emitter.on(Event.CURRENT_BYTE, self.set_current_byte)
        self.esp3d.event_emitter.on(Event.TOTAL_BYTES, self.set_total_bytes)
        self.current_byte = None
        self.total_byte = None

    def set_current_byte(self, value):
        self.current_byte = value

    def set_total_bytes(self, value):
        self.total_bytes = value
        self.schedule_update_ha_state()

    @property
    def state(self):
        if self.current_byte is not None and self.total_bytes is not None:
            return float(self.current_byte) / float(self.total_bytes) * 100


class NotificationEntity(Base):
    def __init__(self, esp3d: Esp3d):
        super().__init__(esp3d)
        self._attr_name = "Notification"
        self._attr_icon = "mdi:monitor"
        self.esp3d.event_emitter.on(Event.NOTIFICATION, self.set_state)
        self._state = ""

    def set_state(self, value):
        self._state = value
        self.schedule_update_ha_state()

    @property
    def state(self):
        return self._state

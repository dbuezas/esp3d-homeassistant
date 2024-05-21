from .esp3d import Esp3d
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
from .const import DOMAIN
import logging
from .event_emitter import Event

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add sensors for passed config_entry in HA."""
    esp3d: Esp3d = hass.data[DOMAIN][config_entry.entry_id]
    new_devices = [
        BusyEntity(esp3d),
        MeshEntity(esp3d),
        IsPrintingEntity(esp3d),
    ]
    async_add_entities(new_devices)


class Base(BinarySensorEntity):
    def __init__(self, esp3d: Esp3d):
        self.esp3d = esp3d
        self._attr_has_entity_name = True
        self.esp3d.event_emitter.on(Event.CONNECTION_STATUS, self.set_attr_available)

    def set_attr_available(self, is_connected: bool):
        if self._attr_available != is_connected:
            self._attr_available = is_connected
            self.schedule_update_ha_state()

    @property
    def unique_id(self) -> str:
        assert self.name
        return self.esp3d._host + "_" + self.name

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.esp3d._host)},
        )


class BusyEntity(Base):
    def __init__(self, esp3d: Esp3d):
        super().__init__(esp3d)

        self._attr_name = "Busy"
        self._attr_icon = "mdi:timer-sand"

        self.firmware_name = None
        self.source_code_url = None
        self.protocol_version = None
        self.machine_type = None
        self.extruder_count = None
        self.uuid = None
        self.esp3d.event_emitter.on(Event.IS_BUSY, self.set_attr_is_on)
        self.esp3d.event_emitter.on(Event.FIRMWARE_NAME, self.set_firmware_name)
        self.esp3d.event_emitter.on(Event.SOURCE_CODE_URL, self.set_source_code_url)
        self.esp3d.event_emitter.on(Event.PROTOCOL_VERSION, self.set_protocol_version)
        self.esp3d.event_emitter.on(Event.MACHINE_TYPE, self.set_machine_type)
        self.esp3d.event_emitter.on(Event.EXTRUDER_COUNT, self.set_extruder_count)
        self.esp3d.event_emitter.on(Event.UUID, self.set_uuid)

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.esp3d._host)},
            name=self.esp3d.name,
            manufacturer=self.machine_type,
            # model=self.firmware_name,
            sw_version=self.firmware_name,
            configuration_url=self.source_code_url,
        )

    def set_attr_is_on(self, is_on: bool):
        if self._attr_is_on != is_on:
            self._attr_is_on = is_on
            self.schedule_update_ha_state()

    def set_firmware_name(self, value):
        self.firmware_name = value

    def set_source_code_url(self, value):
        self.source_code_url = value

    def set_protocol_version(self, value):
        self.protocol_version = value

    def set_machine_type(self, value):
        self.machine_type = value

    def set_extruder_count(self, value):
        self.extruder_count = value

    def set_uuid(self, value):
        self.uuid = value


class IsPrintingEntity(Base):
    def __init__(self, esp3d: Esp3d):
        super().__init__(esp3d)

        self._attr_device_class = BinarySensorDeviceClass.RUNNING
        self._attr_name = "Is printing"
        self._attr_icon = "mdi:printer-3d"

        self._attr_is_on = False
        self.esp3d.event_emitter.on(Event.IS_PRINTING, self.set_is_on)

    def set_is_on(self, is_on: bool):
        if self._attr_is_on != is_on:
            self._attr_is_on = is_on
            self.schedule_update_ha_state()


class MeshEntity(Base):
    def __init__(self, esp3d: Esp3d):
        super().__init__(esp3d)

        self._attr_name = "Mesh"
        self._attr_icon = "mdi:matrix"

        self._attr_is_on = False
        self.mesh = None
        self.esp3d.event_emitter.on(Event.MESH, self.set_mesh)

    def set_mesh(self, mesh: dict[str, list[float]]):
        self._attr_is_on = True
        self.mesh = mesh
        _LOGGER.debug(f"mesh:{mesh}")
        self.schedule_update_ha_state()

    @property
    def extra_state_attributes(self):
        """Return the device specific state attributes."""
        return self.mesh

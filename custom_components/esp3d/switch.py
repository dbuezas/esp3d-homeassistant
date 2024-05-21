import asyncio
from homeassistant.helpers.restore_state import RestoreEntity
from datetime import datetime, timedelta

from homeassistant.components.switch import SwitchEntity

from .esp3d import Esp3d
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
        FetchTempsSwitch(esp3d, config_entry),
        FetchPosSwitch(esp3d, config_entry),
        FetchPrintStatus(esp3d, config_entry),
    ]
    async_add_entities(new_devices)


# class Base(RestoreSwitchEntity):
class Base(SwitchEntity, RestoreEntity):
    def __init__(self, esp3d: Esp3d, config_entry: ConfigEntry):
        self.config_entry = config_entry
        self.esp3d = esp3d
        self._attr_has_entity_name = True
        self._task = None
        self.is_on = False
        self._attr_available = False

        # always available, otherwise there is no way to start receiving data
        self.esp3d.event_emitter.on(Event.CONNECTION_STATUS, self.set_attr_available)

    async def async_added_to_hass(self):
        """Run when this Entity has been added to Home Assistant."""
        await super().async_added_to_hass()

        # Try to restore previous state
        if state := await self.async_get_last_state():
            self.is_on = state.state == "on"

    def set_attr_available(self, is_connected: bool):
        if self._attr_available != is_connected:
            self._attr_available = is_connected
            self.schedule_update_ha_state()
            if is_connected:
                if self.is_on:
                    self.config_entry.async_create_task(
                        self.hass,
                        self.async_turn_on(),
                        f"reset {self.name} on reconnect",
                    )
                else:
                    self.config_entry.async_create_task(
                        self.hass,
                        self.async_turn_off(),
                        f"reset {self.name} on reconnect",
                    )

    @property
    def unique_id(self) -> str:
        assert self.name
        return self.esp3d._host + "_" + self.name

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.esp3d._host)},
        )


class FetchTempsSwitch(Base):
    def __init__(self, esp3d: Esp3d, config_entry: ConfigEntry):
        # requires AUTO_REPORT_TEMPERATURES
        super().__init__(esp3d, config_entry)
        self._attr_name = "Fetch temperatures"
        self._attr_icon = "mdi:thermometer-check"

    async def async_turn_on(self) -> None:
        self.is_on = True
        await self.esp3d.async_send("M155 S2")

    async def async_turn_off(self) -> None:
        self.is_on = False
        await self.esp3d.async_send("M155 S0")


class FetchPosSwitch(Base):
    # requires AUTO_REPORT_POSITION
    def __init__(self, esp3d: Esp3d, config_entry):
        super().__init__(esp3d, config_entry)
        self._attr_name = "Fetch positions"
        self._attr_icon = "mdi:axis-arrow"

    async def async_turn_on(self) -> None:
        await self.esp3d.async_send("M154 S2")
        self.is_on = True

    async def async_turn_off(self) -> None:
        await self.esp3d.async_send("M154 S0")
        self.is_on = False


class FetchPrintStatus(Base):
    # requires AUTO_REPORT_SD_STATUS
    def __init__(self, esp3d: Esp3d, config_entry: ConfigEntry):
        super().__init__(esp3d, config_entry)
        self._attr_name = "Fetch print status"
        self._attr_icon = "mdi:printer-3d"

    async def async_turn_on(self) -> None:
        await self.esp3d.async_send("M27 S2")
        self.is_on = True

    async def async_turn_off(self) -> None:
        await self.esp3d.async_send("M27 S0")
        self.is_on = False

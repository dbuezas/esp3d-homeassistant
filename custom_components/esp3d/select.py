from homeassistant.components.select import SelectEntity
from .esp3d import Esp3d
from .const import DOMAIN
from .file_list_parser import FileDetail
import logging
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .event_emitter import Event

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the select entity for the passed config_entry in HA."""
    esp3d: Esp3d = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([FileSelectEntity(esp3d, config_entry)])


class FileSelectEntity(SelectEntity):
    def __init__(self, esp3d: Esp3d, config_entry: ConfigEntry):
        self.esp3d = esp3d
        self.config_entry = config_entry
        self._attr_has_entity_name = True
        self._current: str | None = None
        self._files = []
        self.esp3d.event_emitter.on(Event.FILE_LIST, self.update_file_list)
        self.esp3d.event_emitter.on(Event.FILE_OPENED, self.file_opened)
        # self.esp3d.event_emitter.on(Event.SDCARD_INSERTED, self.on_sdcard_event)
        # self.esp3d.event_emitter.on(Event.SDCARD_REMOVED, self.on_sdcard_event)

    @property
    def name(self) -> str:
        """Return the name of the select entity."""
        return "File Selector"

    @property
    def options(self) -> list[str]:
        """Return a list of available options."""
        options = [file.long_name or file.short_name for file in self._files]
        return options

    @property
    def current_option(self) -> str | None:
        for file in self._files:
            if file.short_name == self._current:
                return file.long_name or file.short_name
        return None

    def on_sdcard_event(self) -> None:
        self.config_entry.async_create_task(
            self.hass,
            self.esp3d.async_send("M20 L"),
            f"request file list",
        )

    def file_opened(self, option: str, size: int) -> None:
        self._current = option
        found = False
        for file in self._files:
            if file.short_name == option or file.long_name == option:
                found = True
                break
        if not found:
            self._files = [
                FileDetail(
                    short_name=option,
                    size=size,
                    long_name=None,
                )
            ]
        self.schedule_update_ha_state()
        _LOGGER.info(f"Selected file changed to: {option}")

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        for file in self._files:
            # Check if either the short name or long name matches the input_name.
            # Assuming file['long_name'] could be None, use the or operator to default to an empty string.
            if file.short_name == option or file.long_name == option:
                await self.esp3d.async_send("M23 " + file.short_name)
                # await self.esp3d.async_send("M24")
                return
        raise FileNotFoundError("file not found")

    def update_file_list(self, file_list: list[FileDetail]):
        """Update the list of files from an event."""
        self._files = list(reversed(file_list))
        # Optionally reset the current selection if the new list does not include it.
        self.schedule_update_ha_state()
        _LOGGER.info(f"Updated files to: {self._files}")

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self.esp3d._host}_file_selector"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.esp3d._host)},
            name=self.esp3d.name,
        )

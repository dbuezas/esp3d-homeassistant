"""Support for ESP3D."""

from __future__ import annotations
import voluptuous as vol

from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import device_registry as dr

from .esp3d import Esp3d

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse


from .const import (
    DOMAIN,
)

import logging

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [
    Platform.SENSOR,
    Platform.NUMBER,
    Platform.SWITCH,
    Platform.BINARY_SENSOR,
    Platform.SELECT,
]

# based on https://github.com/home-assistant/example-custom-config/tree/master/custom_components/detailed_hello_world_push


def setup_hass_services(hass: HomeAssistant):
    """Set up is called when Home Assistant is loading our component."""

    async def send_gcode(call: ServiceCall):
        """Handle the service call."""
        _LOGGER.debug(f"DATA: {call.data}")

        dev_registry = dr.async_get(hass)
        device_ids = call.data.get("device_id")
        for device_id in device_ids:
            device = dev_registry.async_get(device_id)
            for config_entry_id in device.config_entries:
                # Now you can access the data associated with this config entry
                esp3d = hass.data[DOMAIN].get(config_entry_id)
                if esp3d:
                    response = await esp3d.async_send(call.data.get("gcode"))
                    if call.return_response:
                        return {"response": response}
                    return None

    hass.services.register(
        DOMAIN,
        "send_gcode",
        send_gcode,
        schema=vol.Schema(
            {
                vol.Required("device_id"): vol.All(cv.ensure_list, [cv.string]),
                vol.Required("gcode"): cv.string,
            }
        ),
        supports_response=SupportsResponse.OPTIONAL,
    )

    # Return boolean to indicate that initialization was successful.
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Hello World from a config entry."""

    esp3d = Esp3d(
        name=entry.data["name"],
        host=entry.data["host"],
        port=entry.data["port"],
        hass=hass,
    )

    entry.async_create_background_task(
        hass=hass,
        target=esp3d.async_monitor_connection(),
        name="monitor esp3d connection",
    )
    entry.async_create_background_task(
        hass=hass,
        target=esp3d.async_keep_alive(),
        name="keep_alive esp3d connection",
    )

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = esp3d
    _LOGGER.debug(f"entry.unique_id: {entry.unique_id}")

    # This creates each HA object for each platform your device requires.
    # It's done by calling the `async_setup_entry` function in each platform module.
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    await hass.async_add_executor_job(setup_hass_services, hass)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # This is called when an entry/configured device is to be removed. The class
    # needs to unload itself, and remove callbacks. See the classes for further
    # details
    hass.services.async_remove(DOMAIN, "send_gcode")

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        esp3d: Esp3d = hass.data[DOMAIN].pop(entry.entry_id)
        await esp3d.async_kill()
    return unload_ok

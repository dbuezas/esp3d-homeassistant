import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN,
)
import logging

_LOGGER = logging.getLogger(__name__)


class Esp3dConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow"""

    VERSION = 1

    def __init__(self):
        """Initialize flow."""
        self.discovery_info = None

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        _LOGGER.debug("async_step_user: %s", user_input)

        errors = {}
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_NAME): str,
                        vol.Required(CONF_HOST): str,
                        vol.Required(CONF_PORT, default=23): cv.port,
                    }
                ),
                errors=errors,
            )

        await self.async_set_unique_id(user_input[CONF_HOST])
        self._abort_if_unique_id_configured(updates=user_input)
        return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)

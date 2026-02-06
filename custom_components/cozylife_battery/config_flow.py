"""Config flow for CozyLife Battery integration."""
import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .api import CozyLifeAPI
from .const import DOMAIN, CONF_HOST, DEFAULT_NAME

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
    }
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for CozyLife Battery."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST]

            # Prevent duplicate entries for the same host
            self._async_abort_entries_match({CONF_HOST: host})

            # Validate the connection by attempting to reach the device
            api = CozyLifeAPI(host)
            try:
                await api.update()
            except Exception:
                _LOGGER.exception("Failed to connect to device at %s", host)
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title=DEFAULT_NAME, data=user_input
                )

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

"""Config flow for Lykyn integration."""

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult

from .api import LykynApiClient, LykynAuthError
from .const import CONF_EMAIL, CONF_PASSWORD, DOMAIN

_LOGGER = logging.getLogger(__name__)


class LykynConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Lykyn."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Check for duplicate
            for entry in self._async_current_entries():
                if user_input[CONF_EMAIL] == entry.data.get(CONF_EMAIL):
                    return self.async_abort(reason="already_configured")

            client = LykynApiClient(
                email=user_input[CONF_EMAIL],
                password=user_input[CONF_PASSWORD],
            )

            try:
                await client.authenticate()
                devices = await client.get_devices()
                await client.close()

                return self.async_create_entry(
                    title=f"Lykyn ({user_input[CONF_EMAIL]})",
                    data=user_input,
                )
            except LykynAuthError:
                errors["base"] = "invalid_auth"
            except Exception:
                _LOGGER.exception("Unexpected error during config flow")
                errors["base"] = "cannot_connect"
            finally:
                await client.close()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_EMAIL): str,
                    vol.Required(CONF_PASSWORD): str,
                }
            ),
            errors=errors,
        )

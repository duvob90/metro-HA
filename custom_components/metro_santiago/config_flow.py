from __future__ import annotations

from homeassistant import config_entries
from homeassistant.core import callback
import voluptuous as vol

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL

class MetroConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(
                title="Metro de Santiago", data={}, options=user_input
            )
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {vol.Optional("scan_interval", default=DEFAULT_SCAN_INTERVAL): vol.Coerce(int)}
            ),
        )

    async def async_step_import(self, user_input=None):
        return await self.async_step_user(user_input)

    @callback
    def async_get_options_flow(self, config_entry):
        return MetroOptionsFlow()

class MetroOptionsFlow(config_entries.OptionsFlow):
    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {vol.Optional("scan_interval", default=DEFAULT_SCAN_INTERVAL): vol.Coerce(int)}
            ),
        )

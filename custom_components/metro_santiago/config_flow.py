from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from .const import DOMAIN, DEFAULT_SCAN_INTERVAL

class MetroConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="Metro de Santiago", data={}, options=user_input)
        return self.async_show_form(
            step_id="user",
            data_schema=self.hass.helpers.config_validation.vol.Schema(
                { self.hass.helpers.config_validation.vol.Optional("scan_interval", default=DEFAULT_SCAN_INTERVAL): int }
            ),
        )

    async def async_step_import(self, user_input=None):
        return await self.async_step_user(user_input)

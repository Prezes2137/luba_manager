import voluptuous as vol
from homeassistant import config_entries

DOMAIN = "luba_manager"

class LubaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    VERSION = 1

    async def async_step_user(self, user_input=None):

        if user_input is not None:
            return self.async_create_entry(
                title="Luba Manager",
                data=user_input
            )

        schema = vol.Schema({
            vol.Optional("temp_min", default=10): int,
            vol.Optional("temp_max", default=28): int,
            vol.Optional("rain_block", default=70): int,
            vol.Optional("max_daily_runs", default=2): int,
        })

        return self.async_show_form(step_id="user", data_schema=schema)
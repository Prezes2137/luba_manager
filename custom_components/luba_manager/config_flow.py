from homeassistant import config_entries
from homeassistant.core import callback

from .const import DOMAIN, CONF_ZONES
from .flow_utils import build_schema, build_zones, validate_zone_names

class LubaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        from .options_flow import LubaOptionsFlow

        return LubaOptionsFlow(config_entry)

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            zones = build_zones(user_input)

            if not validate_zone_names(zones):
                errors["base"] = "duplicate_zone_names"
            else:
                data = {
                    key: value
                    for key, value in user_input.items()
                    if not key.startswith("zone_")
                }
                data[CONF_ZONES] = zones

                return self.async_create_entry(title="Luba Manager", data=data)

        return self.async_show_form(
            step_id="user",
            data_schema=build_schema(user_input or {}),
            errors=errors,
        )
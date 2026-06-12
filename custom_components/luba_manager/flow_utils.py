import voluptuous as vol
from homeassistant.helpers import selector

from .const import (
    CONF_MAX_DAILY_RUNS,
    CONF_MOWER_ENTITY_ID,
    CONF_RAIN_BLOCK,
    CONF_TEMP_MAX,
    CONF_TEMP_MIN,
    CONF_ZONE_AREA,
    CONF_ZONE_DRYING_SPEED,
    CONF_ZONE_ID,
    CONF_ZONE_NAME,
    CONF_ZONES,
    DEFAULT_MAX_DAILY_RUNS,
    DEFAULT_RAIN_BLOCK,
    DEFAULT_TEMP_MAX,
    DEFAULT_TEMP_MIN,
    DEFAULT_ZONE_AREA,
    DEFAULT_ZONE_DRYING_SPEED,
    DEFAULT_ZONE_NAMES,
    ZONE_COUNT,
)


def build_schema(defaults):
    schema = {
        vol.Required(
            CONF_MOWER_ENTITY_ID,
            default=defaults.get(CONF_MOWER_ENTITY_ID),
        ): selector.EntitySelector(
            selector.EntitySelectorConfig(domain=["lawn_mower", "vacuum"])
        ),
        vol.Required(
            CONF_TEMP_MIN,
            default=defaults.get(CONF_TEMP_MIN, DEFAULT_TEMP_MIN),
        ): vol.Coerce(int),
        vol.Required(
            CONF_TEMP_MAX,
            default=defaults.get(CONF_TEMP_MAX, DEFAULT_TEMP_MAX),
        ): vol.Coerce(int),
        vol.Required(
            CONF_RAIN_BLOCK,
            default=defaults.get(CONF_RAIN_BLOCK, DEFAULT_RAIN_BLOCK),
        ): vol.Coerce(int),
        vol.Required(
            CONF_MAX_DAILY_RUNS,
            default=defaults.get(CONF_MAX_DAILY_RUNS, DEFAULT_MAX_DAILY_RUNS),
        ): vol.Coerce(int),
    }

    zone_defaults = defaults.get(CONF_ZONES, [])

    for index in range(ZONE_COUNT):
        zone_default = zone_defaults[index] if index < len(zone_defaults) else {}
        zone_number = index + 1
        schema[vol.Required(
            f"zone_{zone_number}_name",
            default=zone_default.get(CONF_ZONE_NAME, DEFAULT_ZONE_NAMES[index]),
        )] = vol.All(str, vol.Length(min=1))
        schema[vol.Required(
            f"zone_{zone_number}_area",
            default=zone_default.get(CONF_ZONE_AREA, DEFAULT_ZONE_AREA),
        )] = vol.All(vol.Coerce(float), vol.Range(min=0.1))
        schema[vol.Required(
            f"zone_{zone_number}_drying_speed",
            default=zone_default.get(CONF_ZONE_DRYING_SPEED, DEFAULT_ZONE_DRYING_SPEED),
        )] = vol.All(vol.Coerce(float), vol.Range(min=0.0))

    return vol.Schema(schema)


def build_zones(user_input):
    zones = []

    for index in range(ZONE_COUNT):
        zone_number = index + 1
        zones.append(
            {
                CONF_ZONE_ID: f"zone_{zone_number}",
                CONF_ZONE_NAME: user_input[f"zone_{zone_number}_name"].strip(),
                CONF_ZONE_AREA: float(user_input[f"zone_{zone_number}_area"]),
                CONF_ZONE_DRYING_SPEED: float(user_input[f"zone_{zone_number}_drying_speed"]),
            }
        )

    return zones


def validate_zone_names(zones):
    names = [zone[CONF_ZONE_NAME].casefold() for zone in zones]
    return len(names) == len(set(names))
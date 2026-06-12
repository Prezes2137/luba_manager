import voluptuous as vol
from homeassistant.helpers import selector

from .const import (
    CONF_MAX_DAILY_RUNS,
    CONF_MOWER_ENTITY_ID,
    CONF_OUTDOOR_TEMP_ENTITY_ID,
    CONF_RAIN_BLOCK,
    CONF_TEMP_MAX,
    CONF_TEMP_MIN,
    CONF_USE_OUTDOOR_TEMP_ENTITY,
    CONF_USE_WEATHER_ENTITY,
    CONF_WEATHER_ENTITY_ID,
    CONF_ZONE_AREA,
    CONF_ZONE_COUNT,
    CONF_ZONE_DRYING_SPEED,
    CONF_ZONE_ID,
    CONF_ZONE_NAME,
    CONF_ZONES,
    DEFAULT_OUTDOOR_TEMP_ENTITY_ID,
    DEFAULT_MAX_DAILY_RUNS,
    DEFAULT_RAIN_BLOCK,
    DEFAULT_TEMP_MAX,
    DEFAULT_TEMP_MIN,
    DEFAULT_USE_OUTDOOR_TEMP_ENTITY,
    DEFAULT_USE_WEATHER_ENTITY,
    DEFAULT_WEATHER_ENTITY_ID,
    DEFAULT_ZONE_AREA,
    DEFAULT_ZONE_COUNT,
    DEFAULT_ZONE_DRYING_SPEED,
    DEFAULT_ZONE_NAMES,
    MAX_ZONE_COUNT,
    MIN_ZONE_COUNT,
)


DRYING_OPTIONS = [
    selector.SelectOptionDict(value="powolna", label="powolna"),
    selector.SelectOptionDict(value="normalna", label="normalna"),
]


def _default_zone_name(index):
    if index < len(DEFAULT_ZONE_NAMES):
        return DEFAULT_ZONE_NAMES[index]
    return f"zone_{index + 1}"


def _clamp_zone_count(value):
    return max(MIN_ZONE_COUNT, min(MAX_ZONE_COUNT, value))


def _normalize_drying_level(value):
    text = str(value or "").strip().casefold()
    if text in {"powolna", "slow", "0", "0.0"}:
        return "powolna"
    return "normalna"


def build_general_schema(defaults):
    zones = defaults.get(CONF_ZONES, [])
    zone_count_default = defaults.get(CONF_ZONE_COUNT, len(zones) or DEFAULT_ZONE_COUNT)
    zone_count_default = _clamp_zone_count(int(zone_count_default))

    schema = {
        vol.Required(
            CONF_MOWER_ENTITY_ID,
            default=defaults.get(CONF_MOWER_ENTITY_ID),
        ): selector.EntitySelector(
            selector.EntitySelectorConfig(domain=["lawn_mower", "vacuum"])
        ),
        vol.Required(
            CONF_WEATHER_ENTITY_ID,
            default=defaults.get(CONF_WEATHER_ENTITY_ID, DEFAULT_WEATHER_ENTITY_ID),
        ): selector.EntitySelector(
            selector.EntitySelectorConfig(domain=["weather", "sensor"])
        ),
        vol.Required(
            CONF_OUTDOOR_TEMP_ENTITY_ID,
            default=defaults.get(CONF_OUTDOOR_TEMP_ENTITY_ID, DEFAULT_OUTDOOR_TEMP_ENTITY_ID),
        ): selector.EntitySelector(
            selector.EntitySelectorConfig(domain=["sensor"])
        ),
        vol.Required(
            CONF_USE_WEATHER_ENTITY,
            default=defaults.get(CONF_USE_WEATHER_ENTITY, DEFAULT_USE_WEATHER_ENTITY),
        ): bool,
        vol.Required(
            CONF_USE_OUTDOOR_TEMP_ENTITY,
            default=defaults.get(CONF_USE_OUTDOOR_TEMP_ENTITY, DEFAULT_USE_OUTDOOR_TEMP_ENTITY),
        ): bool,
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
        vol.Required(
            CONF_ZONE_COUNT,
            default=zone_count_default,
        ): vol.All(vol.Coerce(int), vol.Range(min=MIN_ZONE_COUNT, max=MAX_ZONE_COUNT)),
    }

    return vol.Schema(schema)


def build_zone_schema(zone_count, zone_defaults=None):
    zone_defaults = zone_defaults or []
    zone_count = _clamp_zone_count(int(zone_count))

    schema = {}

    for index in range(zone_count):
        zone_default = zone_defaults[index] if index < len(zone_defaults) else {}
        zone_number = index + 1
        schema[vol.Required(
            f"zone_{zone_number}_name",
            default=zone_default.get(CONF_ZONE_NAME, _default_zone_name(index)),
        )] = vol.All(str, vol.Length(min=1))
        schema[vol.Required(
            f"zone_{zone_number}_area",
            default=zone_default.get(CONF_ZONE_AREA, DEFAULT_ZONE_AREA),
        )] = selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=0.1,
                mode=selector.NumberSelectorMode.BOX,
                unit_of_measurement="m²",
            )
        )
        schema[vol.Required(
            f"zone_{zone_number}_drying_speed",
            default=_normalize_drying_level(
                zone_default.get(CONF_ZONE_DRYING_SPEED, DEFAULT_ZONE_DRYING_SPEED)
            ),
        )] = selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=DRYING_OPTIONS,
                mode=selector.SelectSelectorMode.DROPDOWN,
            )
        )

    return vol.Schema(schema)


def build_zones(user_input, zone_count):
    zones = []

    for index in range(_clamp_zone_count(int(zone_count))):
        zone_number = index + 1
        zones.append(
            {
                CONF_ZONE_ID: f"zone_{zone_number}",
                CONF_ZONE_NAME: user_input[f"zone_{zone_number}_name"].strip(),
                CONF_ZONE_AREA: float(user_input[f"zone_{zone_number}_area"]),
                CONF_ZONE_DRYING_SPEED: _normalize_drying_level(
                    user_input[f"zone_{zone_number}_drying_speed"]
                ),
            }
        )

    return zones


def validate_zone_names(zones):
    names = [zone[CONF_ZONE_NAME].casefold() for zone in zones]
    return len(names) == len(set(names))
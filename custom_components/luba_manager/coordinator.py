import logging

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from datetime import timedelta
from .utils import base_score
from .const import (
    CONF_MOWER_ENTITY_ID,
    CONF_OUTDOOR_TEMP_ENTITY_ID,
    CONF_USE_OUTDOOR_TEMP_ENTITY,
    CONF_USE_WEATHER_ENTITY,
    CONF_WEATHER_ENTITY_ID,
    CONF_ZONE_AREA,
    CONF_ZONE_DRYING_SPEED,
    CONF_ZONE_ID,
    CONF_ZONE_NAME,
    CONF_ZONES,
)


_LOGGER = logging.getLogger(__name__)


def _normalize_key(value):
    return str(value or "").strip().casefold().replace(" ", "_")


def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _drying_bonus(value):
    text = str(value or "").strip().casefold()
    if text in {"powolna", "slow", "0", "0.0"}:
        return 1.5
    if text in {"normalna", "normal", "1", "1.0"}:
        return 3.0
    return max(0.0, _safe_float(value, 0.0) * 3.0)


def _state_or_none(hass, entity_id):
    if not entity_id:
        return None
    return hass.states.get(entity_id)


def _extract_rain(weather_state):
    if not weather_state:
        return 0.0

    attrs = weather_state.attributes
    if "precipitation_probability" in attrs:
        return _safe_float(attrs.get("precipitation_probability"), 0.0)

    forecast = attrs.get("forecast")
    if isinstance(forecast, list) and forecast:
        first = forecast[0] or {}
        if "precipitation_probability" in first:
            return _safe_float(first.get("precipitation_probability"), 0.0)

    return _safe_float(weather_state.state, 0.0)

class LubaCoordinator(DataUpdateCoordinator):

    def __init__(self, hass, config, options):
        super().__init__(
            hass,
            _LOGGER,
            name="luba_manager",
            update_interval=timedelta(minutes=15),
        )

        self.config = config
        self.options = options

    def _value(self, key, default=None):
        if key in self.options:
            return self.options[key]
        return self.config.get(key, default)

    async def _async_update_data(self):

        use_temp_entity = bool(self._value(CONF_USE_OUTDOOR_TEMP_ENTITY, True))
        temp_entity_id = self._value(CONF_OUTDOOR_TEMP_ENTITY_ID)
        temperature_state = _state_or_none(self.hass, temp_entity_id) if use_temp_entity else None
        temp = _safe_float(temperature_state.state if temperature_state else None, 20.0)

        use_weather_entity = bool(self._value(CONF_USE_WEATHER_ENTITY, True))
        weather_entity_id = self._value(CONF_WEATHER_ENTITY_ID)
        weather_state = _state_or_none(self.hass, weather_entity_id) if use_weather_entity else None
        rain = _extract_rain(weather_state) if use_weather_entity else 0.0

        last_zone_state = self.hass.states.get("input_text.luba_last_zone")
        last_zone = _normalize_key(last_zone_state.state if last_zone_state else "")

        base = base_score(temp, rain)

        zones = self._value(CONF_ZONES, [])
        scores = {}
        zone_names = {}

        for zone in zones:
            zone_id = zone.get(CONF_ZONE_ID) or _normalize_key(zone.get(CONF_ZONE_NAME))
            zone_name = zone.get(CONF_ZONE_NAME) or zone_id
            area = _safe_float(zone.get(CONF_ZONE_AREA, 0))
            drying_bonus = _drying_bonus(zone.get(CONF_ZONE_DRYING_SPEED, "normalna"))

            score = base
            score += min(area / 50.0, 20)
            score += drying_bonus

            if last_zone and last_zone in {zone_id, _normalize_key(zone_name)}:
                score -= 20
            else:
                score += 10

            scores[zone_id] = score
            zone_names[zone_id] = zone_name

        best_zone_id = max(scores, key=scores.get) if scores else None
        queue_ids = sorted(scores, key=scores.get, reverse=True)[:2] if scores else []

        return {
            "best": zone_names.get(best_zone_id, best_zone_id),
            "best_zone_id": best_zone_id,
            "mower_entity_id": self._value(CONF_MOWER_ENTITY_ID),
            "weather_entity_id": weather_entity_id,
            "outdoor_temp_entity_id": temp_entity_id,
            "use_weather_entity": use_weather_entity,
            "use_outdoor_temp_entity": use_temp_entity,
            "queue": [zone_names.get(zone_id, zone_id) for zone_id in queue_ids],
            "scores": scores,
            "zones": zones,
        }
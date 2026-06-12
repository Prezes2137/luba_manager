DOMAIN = "luba_manager"

CONF_MOWER_ENTITY_ID = "mower_entity_id"
CONF_WEATHER_ENTITY_ID = "weather_entity_id"
CONF_OUTDOOR_TEMP_ENTITY_ID = "outdoor_temp_entity_id"
CONF_USE_WEATHER_ENTITY = "use_weather_entity"
CONF_USE_OUTDOOR_TEMP_ENTITY = "use_outdoor_temp_entity"
CONF_TEMP_MIN = "temp_min"
CONF_TEMP_MAX = "temp_max"
CONF_RAIN_BLOCK = "rain_block"
CONF_MAX_DAILY_RUNS = "max_daily_runs"
CONF_ZONE_COUNT = "zone_count"
CONF_ZONES = "zones"
CONF_ZONE_ID = "id"
CONF_ZONE_NAME = "name"
CONF_ZONE_AREA = "area"
CONF_ZONE_DRYING_SPEED = "drying_speed"

MIN_ZONE_COUNT = 1
MAX_ZONE_COUNT = 20

DEFAULT_TEMP_MIN = 10
DEFAULT_TEMP_MAX = 28
DEFAULT_RAIN_BLOCK = 70
DEFAULT_MAX_DAILY_RUNS = 2
DEFAULT_WEATHER_ENTITY_ID = "weather.forecast_home"
DEFAULT_OUTDOOR_TEMP_ENTITY_ID = "sensor.czujnik_ogrod_temperature"
DEFAULT_USE_WEATHER_ENTITY = True
DEFAULT_USE_OUTDOOR_TEMP_ENTITY = True
DEFAULT_ZONE_COUNT = 4

DEFAULT_ZONE_NAMES = ["front", "tyl", "lacznik", "bagno"]
DEFAULT_ZONE_AREA = 500.0
DEFAULT_ZONE_DRYING_SPEED = "normalna"
import voluptuous as vol
from homeassistant.exceptions import HomeAssistantError
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform

from .coordinator import LubaCoordinator
from .const import DOMAIN, CONF_ZONE_ACTION, CONF_ZONE_ID, CONF_ZONE_NAME
from .services import execute_action

PLATFORMS = [Platform.SENSOR]
SERVICE_TRIGGER_ZONE_ACTION = "trigger_zone_action"
SERVICE_TRIGGER_BEST_ZONE_ACTION = "trigger_best_zone_action"

async def async_setup(hass, config):
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass, entry: ConfigEntry):
    coordinator = LubaCoordinator(hass, entry.data, entry.options)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    if not hass.services.has_service(DOMAIN, SERVICE_TRIGGER_ZONE_ACTION):
        async def _trigger_zone_action(call):
            entry_id = call.data.get("entry_id")
            coordinator_obj = _resolve_coordinator(hass, entry_id)

            zone_id = call.data.get("zone_id")
            zone_name = call.data.get("zone_name")
            if not zone_id and not zone_name:
                raise HomeAssistantError("Provide zone_id or zone_name")
            zone = _resolve_zone(coordinator_obj.data.get("zones", []), zone_id, zone_name)

            action = zone.get(CONF_ZONE_ACTION)
            zone_label = zone.get(CONF_ZONE_NAME) or zone.get(CONF_ZONE_ID)

            await execute_action(hass, action, zone_label)
            hass.bus.async_fire("luba_zone_executed", {"zone": zone_label, "action": action})

        hass.services.async_register(
            DOMAIN,
            SERVICE_TRIGGER_ZONE_ACTION,
            _trigger_zone_action,
            schema=vol.Schema(
                {
                    vol.Optional("entry_id"): str,
                    vol.Optional("zone_id"): str,
                    vol.Optional("zone_name"): str,
                }
            ),
        )

    if not hass.services.has_service(DOMAIN, SERVICE_TRIGGER_BEST_ZONE_ACTION):
        async def _trigger_best_zone_action(call):
            entry_id = call.data.get("entry_id")
            coordinator_obj = _resolve_coordinator(hass, entry_id)
            best_zone_id = coordinator_obj.data.get("best_zone_id")
            if not best_zone_id:
                raise HomeAssistantError("No best zone available")

            zone = _resolve_zone(coordinator_obj.data.get("zones", []), best_zone_id, None)
            action = zone.get(CONF_ZONE_ACTION)
            zone_label = zone.get(CONF_ZONE_NAME) or zone.get(CONF_ZONE_ID)

            await execute_action(hass, action, zone_label)
            hass.bus.async_fire("luba_zone_executed", {"zone": zone_label, "action": action})

        hass.services.async_register(
            DOMAIN,
            SERVICE_TRIGGER_BEST_ZONE_ACTION,
            _trigger_best_zone_action,
            schema=vol.Schema({vol.Optional("entry_id"): str}),
        )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass, entry: ConfigEntry):
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)

        if not hass.data[DOMAIN]:
            if hass.services.has_service(DOMAIN, SERVICE_TRIGGER_ZONE_ACTION):
                hass.services.async_remove(DOMAIN, SERVICE_TRIGGER_ZONE_ACTION)
            if hass.services.has_service(DOMAIN, SERVICE_TRIGGER_BEST_ZONE_ACTION):
                hass.services.async_remove(DOMAIN, SERVICE_TRIGGER_BEST_ZONE_ACTION)

    return unload_ok


def _resolve_coordinator(hass, entry_id=None):
    coordinators = hass.data.get(DOMAIN, {})
    if not coordinators:
        raise HomeAssistantError("No active Luba Manager entries")

    if entry_id:
        coordinator = coordinators.get(entry_id)
        if not coordinator:
            raise HomeAssistantError(f"Entry not found: {entry_id}")
        return coordinator

    return next(iter(coordinators.values()))


def _resolve_zone(zones, zone_id=None, zone_name=None):
    if zone_id:
        for zone in zones:
            if zone.get(CONF_ZONE_ID) == zone_id:
                return zone

    if zone_name:
        normalized = zone_name.strip().casefold()
        for zone in zones:
            if str(zone.get(CONF_ZONE_NAME, "")).strip().casefold() == normalized:
                return zone

    raise HomeAssistantError("Zone not found")
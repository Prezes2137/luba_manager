from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform

from .coordinator import LubaCoordinator
from .const import DOMAIN

PLATFORMS = [Platform.SENSOR]

async def async_setup(hass, config):
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass, entry: ConfigEntry):
    coordinator = LubaCoordinator(hass, entry.data, entry.options)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass, entry: ConfigEntry):
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)

    return unload_ok
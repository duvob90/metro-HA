from datetime import timedelta
import aiohttp, async_timeout
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.const import Platform
from .const import DOMAIN, API_URL, DEFAULT_SCAN_INTERVAL

PLATFORMS = [Platform.SENSOR]

async def async_setup_entry(hass, entry):
    session = aiohttp.ClientSession()
    async def _async_update():
        async with async_timeout.timeout(15):
            async with session.get(API_URL) as resp:
                resp.raise_for_status()
                return await resp.json()

    coordinator = DataUpdateCoordinator(
        hass,
        hass.helpers.event.async_track_time_interval,
        name=DOMAIN,
        update_method=_async_update,
        update_interval=timedelta(seconds=entry.options.get("scan_interval", DEFAULT_SCAN_INTERVAL)),
    )
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "session": session,
        "coordinator": coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass, entry):
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    session = hass.data[DOMAIN][entry.entry_id]["session"]
    await session.close()
    hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok

"""Lykyn Mushroom Grow Kit integration for Home Assistant."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_HOMEASSISTANT_STOP
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady

from .api import LykynApiClient, LykynAuthError, LykynApiError
from .const import CONF_EMAIL, CONF_PASSWORD, DOMAIN, PLATFORMS
from .coordinator import LykynCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Lykyn from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    client = LykynApiClient(
        email=entry.data[CONF_EMAIL],
        password=entry.data[CONF_PASSWORD],
    )

    try:
        await client.authenticate()
    except LykynAuthError as err:
        await client.close()
        raise ConfigEntryAuthFailed(str(err)) from err
    except Exception as err:
        await client.close()
        raise ConfigEntryNotReady(str(err)) from err

    coordinator = LykynCoordinator(hass, client)

    try:
        await coordinator.async_setup()
    except LykynApiError as err:
        await client.close()
        raise ConfigEntryNotReady(str(err)) from err

    hass.data[DOMAIN][entry.entry_id] = coordinator

    entry.async_on_unload(
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, client.close)
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        coordinator: LykynCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.async_shutdown()
    return unload_ok

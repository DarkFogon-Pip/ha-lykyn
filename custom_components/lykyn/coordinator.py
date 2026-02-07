"""DataUpdateCoordinator for Lykyn."""

import asyncio
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .api import LykynApiClient, LykynApiError
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class LykynCoordinator(DataUpdateCoordinator):
    """Coordinator for Lykyn devices."""

    def __init__(self, hass: HomeAssistant, client: LykynApiClient) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            # No polling interval - we use Socket.io push updates
        )
        self.client = client
        self.client.register_update_callback(self._on_device_update)

    async def _on_device_update(self, device_id: str | None) -> None:
        """Handle real-time device update from Socket.io."""
        self.async_set_updated_data(self.client.devices)

    async def _async_update_data(self) -> dict[str, dict]:
        """Fetch data from API (fallback, mainly for initial load)."""
        try:
            await self.client.get_devices()
            await self.client.get_online_devices()
            return self.client.devices
        except LykynApiError as err:
            _LOGGER.error("Error fetching Lykyn data: %s", err)
            raise

    async def async_setup(self) -> None:
        """Set up the coordinator: fetch devices and connect socket."""
        await self.client.get_devices()
        await self.client.get_online_devices()
        self.data = self.client.devices

        try:
            await self.client.connect_socket()
        except LykynApiError:
            _LOGGER.warning("Socket.io connection failed, will use polling")

    async def async_shutdown(self) -> None:
        """Shut down the coordinator."""
        self.client.unregister_update_callback(self._on_device_update)
        await self.client.close()

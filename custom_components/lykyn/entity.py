"""Base entity for Lykyn."""

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import LykynCoordinator


class LykynEntity(CoordinatorEntity[LykynCoordinator]):
    """Base entity for Lykyn devices."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: LykynCoordinator, device_id: str) -> None:
        super().__init__(coordinator)
        self._device_id = device_id

    @property
    def _device_data(self) -> dict:
        """Get the device data from coordinator."""
        return self.coordinator.client.devices.get(self._device_id, {})

    @property
    def _device_info_data(self) -> dict:
        """Get the info dict from device data."""
        return self._device_data.get("info", {})

    @property
    def _is_online(self) -> bool:
        """Check if device is online."""
        return self._device_id in self.coordinator.client.online_devices

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._is_online and super().available

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        device = self._device_data
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=device.get("name", f"Lykyn {self._device_id[:8]}"),
            manufacturer="Lykyn (Swayfish)",
            model="Mushroom Grow Kit",
            sw_version=device.get("info", {}).get("specs", {}).get("version"),
        )

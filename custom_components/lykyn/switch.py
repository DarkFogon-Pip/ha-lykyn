"""Switch platform for Lykyn."""

import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN
from .coordinator import LykynCoordinator
from .entity import LykynEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Lykyn switches."""
    coordinator: LykynCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []

    for device_id in coordinator.client.devices:
        entities.extend([
            LykynHumidifierSwitch(coordinator, device_id),
            LykynLightSwitch(coordinator, device_id),
        ])

    async_add_entities(entities)


class LykynHumidifierSwitch(LykynEntity, SwitchEntity):
    """Humidifier on/off switch."""

    _attr_translation_key = "humidifier"
    _attr_icon = "mdi:air-humidifier"

    def __init__(self, coordinator: LykynCoordinator, device_id: str) -> None:
        super().__init__(coordinator, device_id)
        self._attr_unique_id = f"{device_id}_humidifier"

    @property
    def is_on(self) -> bool | None:
        return self._device_info_data.get("humidifier")

    async def async_turn_on(self, **kwargs) -> None:
        await self.coordinator.client.update_device_info(
            self._device_id, {"humidifier": True}
        )

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.client.update_device_info(
            self._device_id, {"humidifier": False}
        )


class LykynLightSwitch(LykynEntity, SwitchEntity):
    """Light on/off switch."""

    _attr_translation_key = "light_switch"
    _attr_icon = "mdi:led-strip-variant"

    def __init__(self, coordinator: LykynCoordinator, device_id: str) -> None:
        super().__init__(coordinator, device_id)
        self._attr_unique_id = f"{device_id}_light_switch"

    @property
    def is_on(self) -> bool | None:
        return self._device_info_data.get("light")

    async def async_turn_on(self, **kwargs) -> None:
        await self.coordinator.client.update_device_info(
            self._device_id, {"light": True}
        )

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.client.update_device_info(
            self._device_id, {"light": False}
        )

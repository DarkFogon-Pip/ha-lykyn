"""Light platform for Lykyn."""

import logging

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_EFFECT,
    ATTR_RGB_COLOR,
    ColorMode,
    LightEntity,
    LightEntityFeature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from homeassistant.config_entries import ConfigEntry

from .const import DEFAULT_LIGHT_SETTINGS, DOMAIN, LIGHT_ANIMATIONS
from .coordinator import LykynCoordinator
from .entity import LykynEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Lykyn light entities."""
    coordinator: LykynCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []

    for device_id in coordinator.client.devices:
        entities.append(LykynLight(coordinator, device_id))

    async_add_entities(entities)


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert hex color string to RGB tuple."""
    hex_color = hex_color.lstrip("#")
    if len(hex_color) != 6:
        return (255, 255, 255)
    return (
        int(hex_color[0:2], 16),
        int(hex_color[2:4], 16),
        int(hex_color[4:6], 16),
    )


def _rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    """Convert RGB tuple to hex color string."""
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"


class LykynLight(LykynEntity, LightEntity):
    """Light entity for the Lykyn LED strip."""

    _attr_translation_key = "led_strip"
    _attr_supported_color_modes = {ColorMode.RGB}
    _attr_color_mode = ColorMode.RGB
    _attr_supported_features = LightEntityFeature.EFFECT

    def __init__(self, coordinator: LykynCoordinator, device_id: str) -> None:
        super().__init__(coordinator, device_id)
        self._attr_unique_id = f"{device_id}_light"
        self._attr_effect_list = LIGHT_ANIMATIONS

    @property
    def is_on(self) -> bool | None:
        info = self._device_info_data
        return info.get("light", False) and info.get("lightMode") != "OFF"

    @property
    def brightness(self) -> int | None:
        val = self._device_info_data.get("lightBrightness", 50)
        # Lykyn uses 0-100, HA uses 0-255
        return int(val * 255 / 100) if val is not None else None

    @property
    def rgb_color(self) -> tuple[int, int, int] | None:
        hex_color = self._device_info_data.get("lightColor", "#FFFFFF")
        return _hex_to_rgb(hex_color)

    @property
    def effect(self) -> str | None:
        info = self._device_info_data
        if info.get("lightMode") == "ANIMATION":
            return info.get("lightAnimation", "RAINBOW")
        return None

    async def async_turn_on(self, **kwargs) -> None:
        update = {"light": True}

        if ATTR_BRIGHTNESS in kwargs:
            # HA 0-255 → Lykyn 0-100
            update["lightBrightness"] = int(kwargs[ATTR_BRIGHTNESS] * 100 / 255)

        if ATTR_RGB_COLOR in kwargs:
            update["lightMode"] = "SOLID"
            update["lightColor"] = _rgb_to_hex(kwargs[ATTR_RGB_COLOR])

        if ATTR_EFFECT in kwargs:
            update["lightMode"] = "ANIMATION"
            update["lightAnimation"] = kwargs[ATTR_EFFECT]

        # If no mode specified and currently off, default to animation
        if "lightMode" not in update:
            current_mode = self._device_info_data.get("lightMode", "OFF")
            if current_mode == "OFF":
                update["lightMode"] = DEFAULT_LIGHT_SETTINGS["lightMode"]
                update["lightAnimation"] = DEFAULT_LIGHT_SETTINGS["lightAnimation"]

        await self.coordinator.client.update_device_info(self._device_id, update)

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.client.update_device_info(
            self._device_id, {"light": False, "lightMode": "OFF"}
        )

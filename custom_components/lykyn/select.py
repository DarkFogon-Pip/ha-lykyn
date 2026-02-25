"""Select platform for Lykyn."""

import logging

from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN, LIGHT_ANIMATIONS, LIGHT_MODES, MUSHROOM_PRESETS
from .coordinator import LykynCoordinator
from .entity import LykynEntity

_LOGGER = logging.getLogger(__name__)

CONTROL_TYPES = ["SMART", "MANUAL"]

MUSHROOM_LABELS = {
    "OysterPearlGrey": "Oyster - Pearl / Grey",
    "OysterBlue": "Oyster - Blue",
    "OysterGolden": "Oyster - Golden",
    "OysterPink": "Oyster - Pink",
    "OysterPhoenix": "Oyster - Phoenix",
    "OysterBlackPearl": "Oyster - Black Pearl",
    "KingOyster": "King Oyster / Trumpet",
    "LionsMane": "Lion's Mane",
    "BearsHead": "Bear's Head / Coral Tooth",
    "Shiitake": "Shiitake",
    "Beech": "Beech / Shimeji",
    "Pioppino": "Pioppino / Black Poplar",
    "Chestnut": "Chestnut",
    "Enoki": "Enoki / Velvet Shank",
    "WoodEar": "Wood Ear / Jelly Ear",
    "Button": "Button / Cremini / Portobello",
    "Nameko": "Nameko",
    "Maitake": "Maitake / Hen Of The Woods",
    "AlmondAgaricus": "Almond Agaricus",
    "Reishi": "Reishi",
    "TurkeyTail": "Turkey Tail",
    "Cordyceps": "Cordyceps Militaris",
    "Milky": "Milky",
    "PaddyStraw": "Paddy Straw",
    "SnowFungus": "Snow Fungus / Silver Ear",
    "Blewit": "Blewit / Wood Blewit",
    "ShaggyMane": "Shaggy Mane",
    "DungLoving": "Dung Loving",
    "CustomGrowthMode": "Custom Growth Mode",
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Lykyn select entities."""
    coordinator: LykynCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []

    for device_id in coordinator.client.devices:
        entities.extend([
            LykynControlTypeSelect(coordinator, device_id),
            LykynMushroomSelect(coordinator, device_id),
            LykynLightModeSelect(coordinator, device_id),
            LykynLightAnimationSelect(coordinator, device_id),
        ])

    async_add_entities(entities)


class LykynControlTypeSelect(LykynEntity, SelectEntity):
    """Control type selector (SMART/MANUAL)."""

    _attr_translation_key = "control_type"
    _attr_icon = "mdi:cog"
    _attr_options = CONTROL_TYPES

    def __init__(self, coordinator: LykynCoordinator, device_id: str) -> None:
        super().__init__(coordinator, device_id)
        self._attr_unique_id = f"{device_id}_control_type"

    @property
    def current_option(self) -> str | None:
        return self._device_info_data.get("controlType", "MANUAL")

    async def async_select_option(self, option: str) -> None:
        await self.coordinator.client.update_device_info(
            self._device_id, {"controlType": option}
        )


class LykynMushroomSelect(LykynEntity, SelectEntity):
    """Mushroom type selector."""

    _attr_translation_key = "mushroom_type"
    _attr_icon = "mdi:mushroom"
    _attr_options = list(MUSHROOM_LABELS.keys())

    def __init__(self, coordinator: LykynCoordinator, device_id: str) -> None:
        super().__init__(coordinator, device_id)
        self._attr_unique_id = f"{device_id}_mushroom_type"

    @property
    def current_option(self) -> str | None:
        return self._device_info_data.get("selectedMushroom")

    async def async_select_option(self, option: str) -> None:
        """Select a mushroom type and apply its presets."""
        preset = MUSHROOM_PRESETS.get(option, MUSHROOM_PRESETS["CustomGrowthMode"])
        update = {
            "selectedMushroom": option,
            "minTemp": preset["minTemp"],
            "maxTemp": preset["maxTemp"],
            "minHum": preset["minHum"],
            "maxHum": preset["maxHum"],
        }
        await self.coordinator.client.update_device_info(self._device_id, update)


class LykynLightModeSelect(LykynEntity, SelectEntity):
    """Light mode selector (ANIMATION/MANUAL/EMOTIONAL)."""

    _attr_translation_key = "light_mode"
    _attr_icon = "mdi:lightbulb-cog"
    _attr_options = LIGHT_MODES

    def __init__(self, coordinator: LykynCoordinator, device_id: str) -> None:
        super().__init__(coordinator, device_id)
        self._attr_unique_id = f"{device_id}_light_mode"

    @property
    def current_option(self) -> str | None:
        return self._device_info_data.get("lightMode")

    async def async_select_option(self, option: str) -> None:
        await self.coordinator.client.update_device_info(
            self._device_id, {"lightMode": option}
        )


class LykynLightAnimationSelect(LykynEntity, SelectEntity):
    """Light animation selector (29 animations)."""

    _attr_translation_key = "light_animation"
    _attr_icon = "mdi:animation"
    _attr_options = LIGHT_ANIMATIONS

    def __init__(self, coordinator: LykynCoordinator, device_id: str) -> None:
        super().__init__(coordinator, device_id)
        self._attr_unique_id = f"{device_id}_light_animation"

    @property
    def current_option(self) -> str | None:
        return self._device_info_data.get("lightAnimation")

    async def async_select_option(self, option: str) -> None:
        await self.coordinator.client.update_device_info(
            self._device_id, {"lightMode": "ANIMATION", "lightAnimation": option}
        )

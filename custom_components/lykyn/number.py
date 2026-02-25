"""Number platform for Lykyn."""

import logging

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.const import PERCENTAGE, UnitOfTemperature, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN
from .coordinator import LykynCoordinator
from .entity import LykynEntity

_LOGGER = logging.getLogger(__name__)

# Timer keys that live under info.smart
SMART_KEYS = {
    "airinOn", "airinOff", "airoutOn", "airoutOff",
    "humidifierOnDuration", "humidifierBelowMinDuration",
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Lykyn number entities."""
    coordinator: LykynCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []

    for device_id in coordinator.client.devices:
        entities.extend([
            LykynFanSpeedEntity(
                coordinator, device_id,
                key="airin", name_key="fan_in_speed",
                icon="mdi:fan",
            ),
            LykynFanSpeedEntity(
                coordinator, device_id,
                key="airout", name_key="fan_out_speed",
                icon="mdi:fan",
            ),
            LykynNumberEntity(
                coordinator, device_id,
                key="minTemp", name_key="min_temperature",
                min_val=0, max_val=40, step=1,
                unit=UnitOfTemperature.CELSIUS, icon="mdi:thermometer-low",
            ),
            LykynNumberEntity(
                coordinator, device_id,
                key="maxTemp", name_key="max_temperature",
                min_val=0, max_val=40, step=1,
                unit=UnitOfTemperature.CELSIUS, icon="mdi:thermometer-high",
            ),
            LykynNumberEntity(
                coordinator, device_id,
                key="minHum", name_key="min_humidity",
                min_val=0, max_val=100, step=1,
                unit=PERCENTAGE, icon="mdi:water-percent",
            ),
            LykynNumberEntity(
                coordinator, device_id,
                key="maxHum", name_key="max_humidity",
                min_val=0, max_val=100, step=1,
                unit=PERCENTAGE, icon="mdi:water-percent",
            ),
            LykynSmartNumberEntity(
                coordinator, device_id,
                key="airinOn", name_key="intake_fan_on",
                min_val=0, max_val=60, step=1,
                unit=UnitOfTime.MINUTES, icon="mdi:fan",
            ),
            LykynSmartNumberEntity(
                coordinator, device_id,
                key="airinOff", name_key="intake_fan_off",
                min_val=0, max_val=60, step=1,
                unit=UnitOfTime.MINUTES, icon="mdi:fan-off",
            ),
            LykynSmartNumberEntity(
                coordinator, device_id,
                key="airoutOn", name_key="exhaust_fan_on",
                min_val=0, max_val=60, step=1,
                unit=UnitOfTime.MINUTES, icon="mdi:fan",
            ),
            LykynSmartNumberEntity(
                coordinator, device_id,
                key="airoutOff", name_key="exhaust_fan_off",
                min_val=0, max_val=60, step=1,
                unit=UnitOfTime.MINUTES, icon="mdi:fan-off",
            ),
            LykynSmartNumberEntity(
                coordinator, device_id,
                key="humidifierOnDuration", name_key="humidifier_on_duration",
                min_val=0, max_val=60, step=1,
                unit=UnitOfTime.MINUTES, icon="mdi:air-humidifier",
            ),
            LykynSmartNumberEntity(
                coordinator, device_id,
                key="humidifierBelowMinDuration",
                name_key="humidifier_below_min_duration",
                min_val=0, max_val=60, step=1,
                unit=UnitOfTime.MINUTES, icon="mdi:air-humidifier",
            ),
            LykynNumberEntity(
                coordinator, device_id,
                key="lightBrightness", name_key="light_brightness",
                min_val=0, max_val=100, step=1,
                unit=PERCENTAGE, icon="mdi:brightness-6",
            ),
            LykynCalibrationNumber(
                coordinator, device_id,
                key="tempPercent", name_key="temp_calibration_offset",
                icon="mdi:thermometer-alert",
            ),
            LykynCalibrationNumber(
                coordinator, device_id,
                key="humPercent", name_key="humidity_calibration_offset",
                icon="mdi:water-percent-alert",
            ),
        ])

    async_add_entities(entities)


class LykynNumberEntity(LykynEntity, NumberEntity):
    """A numeric setting for a Lykyn device (reads from info.<key>)."""

    _attr_mode = NumberMode.BOX

    def __init__(
        self,
        coordinator: LykynCoordinator,
        device_id: str,
        key: str,
        name_key: str,
        min_val: float,
        max_val: float,
        step: float,
        unit: str,
        icon: str,
    ) -> None:
        super().__init__(coordinator, device_id)
        self._key = key
        self._attr_unique_id = f"{device_id}_{key}"
        self._attr_translation_key = name_key
        self._attr_native_min_value = min_val
        self._attr_native_max_value = max_val
        self._attr_native_step = step
        self._attr_native_unit_of_measurement = unit
        self._attr_icon = icon

    @property
    def native_value(self) -> float | None:
        return self._device_info_data.get(self._key)

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.client.update_device_info(
            self._device_id, {self._key: value}
        )


class LykynSmartNumberEntity(LykynEntity, NumberEntity):
    """A numeric setting nested under info.smart.<key>."""

    _attr_mode = NumberMode.BOX

    def __init__(
        self,
        coordinator: LykynCoordinator,
        device_id: str,
        key: str,
        name_key: str,
        min_val: float,
        max_val: float,
        step: float,
        unit: str,
        icon: str,
    ) -> None:
        super().__init__(coordinator, device_id)
        self._key = key
        self._attr_unique_id = f"{device_id}_{key}"
        self._attr_translation_key = name_key
        self._attr_native_min_value = min_val
        self._attr_native_max_value = max_val
        self._attr_native_step = step
        self._attr_native_unit_of_measurement = unit
        self._attr_icon = icon

    @property
    def native_value(self) -> float | None:
        smart = self._device_info_data.get("smart", {})
        return smart.get(self._key)

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.client.update_device_info(
            self._device_id, {"smart": {self._key: value}}
        )


class LykynCalibrationNumber(LykynEntity, NumberEntity):
    """Calibration offset under info.calibrate.<key>."""

    _attr_mode = NumberMode.BOX
    _attr_native_min_value = -10
    _attr_native_max_value = 10
    _attr_native_step = 0.1

    def __init__(
        self,
        coordinator: LykynCoordinator,
        device_id: str,
        key: str,
        name_key: str,
        icon: str,
    ) -> None:
        super().__init__(coordinator, device_id)
        self._key = key
        self._attr_unique_id = f"{device_id}_calibrate_{key}"
        self._attr_translation_key = name_key
        self._attr_icon = icon

    @property
    def native_value(self) -> float | None:
        calibrate = self._device_info_data.get("calibrate", {})
        return calibrate.get(self._key)

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.client.update_device_info(
            self._device_id, {"calibrate": {self._key: value}}
        )


class LykynFanSpeedEntity(LykynEntity, NumberEntity):
    """Fan speed control (0-3) for a Lykyn device."""

    _attr_mode = NumberMode.SLIDER
    _attr_native_min_value = 0
    _attr_native_max_value = 3
    _attr_native_step = 1

    def __init__(
        self,
        coordinator: LykynCoordinator,
        device_id: str,
        key: str,
        name_key: str,
        icon: str,
    ) -> None:
        super().__init__(coordinator, device_id)
        self._key = key
        self._attr_unique_id = f"{device_id}_{key}_speed"
        self._attr_translation_key = name_key
        self._attr_icon = icon

    @property
    def native_value(self) -> float | None:
        return self._device_info_data.get(self._key)

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.client.update_device_info(
            self._device_id, {self._key: int(value)}
        )

"""Sensor platform for Lykyn."""

import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE, UnitOfTemperature
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
    """Set up Lykyn sensors."""
    coordinator: LykynCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []

    for device_id in coordinator.client.devices:
        entities.extend([
            LykynTemperatureSensor(coordinator, device_id),
            LykynHumiditySensor(coordinator, device_id),
            LykynRawTemperatureSensor(coordinator, device_id),
            LykynRawHumiditySensor(coordinator, device_id),
            LykynTargetTempMinSensor(coordinator, device_id),
            LykynTargetTempMaxSensor(coordinator, device_id),
            LykynTargetHumMinSensor(coordinator, device_id),
            LykynTargetHumMaxSensor(coordinator, device_id),
        ])

    async_add_entities(entities)


class LykynTemperatureSensor(LykynEntity, SensorEntity):
    """Calibrated temperature sensor."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_translation_key = "temperature"

    def __init__(self, coordinator: LykynCoordinator, device_id: str) -> None:
        super().__init__(coordinator, device_id)
        self._attr_unique_id = f"{device_id}_temperature"

    @property
    def native_value(self) -> float | None:
        calibrate = self._device_info_data.get("calibrate", {})
        return calibrate.get("calibratedTemp") or calibrate.get("temp")


class LykynHumiditySensor(LykynEntity, SensorEntity):
    """Calibrated humidity sensor."""

    _attr_device_class = SensorDeviceClass.HUMIDITY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_translation_key = "humidity"

    def __init__(self, coordinator: LykynCoordinator, device_id: str) -> None:
        super().__init__(coordinator, device_id)
        self._attr_unique_id = f"{device_id}_humidity"

    @property
    def native_value(self) -> float | None:
        calibrate = self._device_info_data.get("calibrate", {})
        val = calibrate.get("calibratedHum") or calibrate.get("hum")
        if val is not None:
            return min(val, 100.0)
        return None


class LykynRawTemperatureSensor(LykynEntity, SensorEntity):
    """Raw (uncalibrated) temperature sensor."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_translation_key = "raw_temperature"
    _attr_entity_registry_enabled_default = False

    def __init__(self, coordinator: LykynCoordinator, device_id: str) -> None:
        super().__init__(coordinator, device_id)
        self._attr_unique_id = f"{device_id}_raw_temperature"

    @property
    def native_value(self) -> float | None:
        calibrate = self._device_info_data.get("calibrate", {})
        return calibrate.get("temp")


class LykynRawHumiditySensor(LykynEntity, SensorEntity):
    """Raw (uncalibrated) humidity sensor."""

    _attr_device_class = SensorDeviceClass.HUMIDITY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_translation_key = "raw_humidity"
    _attr_entity_registry_enabled_default = False

    def __init__(self, coordinator: LykynCoordinator, device_id: str) -> None:
        super().__init__(coordinator, device_id)
        self._attr_unique_id = f"{device_id}_raw_humidity"

    @property
    def native_value(self) -> float | None:
        calibrate = self._device_info_data.get("calibrate", {})
        val = calibrate.get("hum")
        if val is not None:
            return min(val, 100.0)
        return None


class LykynTargetTempMinSensor(LykynEntity, SensorEntity):
    """Target minimum temperature sensor."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_translation_key = "target_temp_min"
    _attr_entity_registry_enabled_default = False

    def __init__(self, coordinator: LykynCoordinator, device_id: str) -> None:
        super().__init__(coordinator, device_id)
        self._attr_unique_id = f"{device_id}_target_temp_min"

    @property
    def native_value(self) -> float | None:
        return self._device_info_data.get("minTemp")


class LykynTargetTempMaxSensor(LykynEntity, SensorEntity):
    """Target maximum temperature sensor."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_translation_key = "target_temp_max"
    _attr_entity_registry_enabled_default = False

    def __init__(self, coordinator: LykynCoordinator, device_id: str) -> None:
        super().__init__(coordinator, device_id)
        self._attr_unique_id = f"{device_id}_target_temp_max"

    @property
    def native_value(self) -> float | None:
        return self._device_info_data.get("maxTemp")


class LykynTargetHumMinSensor(LykynEntity, SensorEntity):
    """Target minimum humidity sensor."""

    _attr_device_class = SensorDeviceClass.HUMIDITY
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_translation_key = "target_hum_min"
    _attr_entity_registry_enabled_default = False

    def __init__(self, coordinator: LykynCoordinator, device_id: str) -> None:
        super().__init__(coordinator, device_id)
        self._attr_unique_id = f"{device_id}_target_hum_min"

    @property
    def native_value(self) -> float | None:
        return self._device_info_data.get("minHum")


class LykynTargetHumMaxSensor(LykynEntity, SensorEntity):
    """Target maximum humidity sensor."""

    _attr_device_class = SensorDeviceClass.HUMIDITY
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_translation_key = "target_hum_max"
    _attr_entity_registry_enabled_default = False

    def __init__(self, coordinator: LykynCoordinator, device_id: str) -> None:
        super().__init__(coordinator, device_id)
        self._attr_unique_id = f"{device_id}_target_hum_max"

    @property
    def native_value(self) -> float | None:
        return self._device_info_data.get("maxHum")

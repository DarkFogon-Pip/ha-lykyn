# Changelog

## [0.2.0] - 2026-02-25

### Fixed
- Timer duration entities (intake/exhaust fan on/off, humidifier durations) now read from `info.smart.*` instead of flat `info.*` — previously showed "unknown"
- Light modes corrected to match actual API: `ANIMATION`, `MANUAL`, `EMOTIONAL` (was `ANIMATION`, `SOLID`, `OFF`)
- Calibrated temperature/humidity sensors now read from nested `info.calibrate.calibratedTemp`/`calibratedHum` (was flat `info.calibratedTemp`)
- Light turn_off no longer sets non-existent `lightMode: "OFF"` — just sets `light: false`
- Light turn_on with RGB color now sets `lightMode: "MANUAL"` (was `"SOLID"`)
- `update_device_info` now deep-merges nested sub-objects (`smart`, `calibrate`) instead of overwriting them

### Added
- **29 light animations** (was 6): RAINBOW, AURORA, BEATCHASE, BPM, BREATH, COLORWAVES, CONFETTI, CYANMAGENTAFADE, FIRE, FIREFLYDANCE, FROZENPULSE, ICECOMET, NOISE, OCEANWAVE, PASTELWAVES, PIXELMETEOR, POLICELIGHTS, POPCORN, PRIDE, PULSERAINBOW, RAINBOWGLITTER, RAINBOWMARCH, RAINBOWPOP, RANDOMCHASE, RGBFADEALL, RGB_WAVE, SINELON, SOFTWHITETWINKLE, SUNSETFADE
- **Emotional mode** available as a light effect in the LED strip entity
- **`realtimeDeviceUpdates`** socket event listener for live sensor data stream
- **Smart Light Enable** switch (`info.smart.light`) — toggle light subsystem in SMART mode
- **Smart Humidifier Enable** switch (`info.smart.humidifier`) — toggle humidifier subsystem in SMART mode
- **Light Mode** select entity (`ANIMATION` / `MANUAL` / `EMOTIONAL`)
- **Light Animation** select entity (all 29 animations)
- **Temperature Calibration Offset** number entity (`info.calibrate.tempPercent`, range -10 to 10)
- **Humidity Calibration Offset** number entity (`info.calibrate.humPercent`, range -10 to 10)
- **Raw Temperature** sensor (`info.calibrate.temp`, disabled by default)
- **Raw Humidity** sensor (`info.calibrate.hum`, disabled by default)
- Translation keys for all new entities in `strings.json` and `translations/en.json`

### Changed
- Entity count increased from 24 to **32 per device**
- Timer number entities now use `LykynSmartNumberEntity` class that reads/writes to `info.smart.*`

## [0.1.1] - 2026-02-23

### Fixed
- Initial release bug fixes

## [0.1.0] - 2026-02-23

### Added
- Initial release
- Full reverse-engineered Lykyn cloud protocol integration
- Real-time sensor data via Socket.io push
- 24 entities per device (6 sensors, 2 switches, 13 numbers, 1 light, 2 selects)
- 29 mushroom species presets
- Fan speed control (0-3)
- LED strip with RGB color and 6 animation effects

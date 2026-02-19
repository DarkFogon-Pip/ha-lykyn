# Lykyn Mushroom Grow Kit - Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

A custom Home Assistant integration for the **Lykyn Smart Mushroom Grow Kit** (by [Swayfish](https://lykyn.app/)). This integration was built by **reverse-engineering the Lykyn cloud protocol** since no official API or integration exists.

## Features

- **Real-time sensor data** via Socket.io push (temperature, humidity)
- **Full device control**: fans, humidifier, LED light strip
- **Fan speed control**: intake and exhaust fans independently set 0–3 (off → low → medium → high)
- **29 mushroom species presets** with auto-configured temperature/humidity ranges
- **LED effects**: Aurora, Breath, RGB Wave, Rainbow, Confetti, Sunset Fade
- **Smart/Manual control modes**
- **Multi-device support**

## Entities (per device)

| Type | Entities | Description |
|------|----------|-------------|
| Sensor | 6 | Temperature, humidity, target min/max setpoints |
| Switch | 2 | Humidifier on/off, light on/off |
| Number | 13 | **Fan in/out speed (0–3)**, temp/humidity setpoints, fan cycle timers, humidifier durations, brightness |
| Light | 1 | LED strip with RGB color, brightness, and 6 animation effects |
| Select | 2 | Control mode (Smart/Manual), mushroom type (29 species) |

**Total: 24 entities per device**

### Fan Speed Control

The two fan speed sliders (`Fan in speed`, `Fan out speed`) match what the official Lykyn app exposes:

| Value | Meaning |
|-------|---------|
| 0 | Fan off |
| 1 | Low speed |
| 2 | Medium speed |
| 3 | High speed |

## Supported Mushroom Types

Oyster (Pearl/Grey, Blue, Golden, Pink, Phoenix, Black Pearl), King Oyster, Lion's Mane, Bear's Head, Shiitake, Beech/Shimeji, Pioppino, Chestnut, Enoki, Wood Ear, Button/Cremini/Portobello, Nameko, Maitake, Almond Agaricus, Reishi, Turkey Tail, Cordyceps, Milky, Paddy Straw, Snow Fungus, Blewit, Shaggy Mane, Dung Loving, and Custom Growth Mode.

## Installation

### HACS (Recommended)

1. Open HACS in your Home Assistant instance
2. Click the three dots menu (top right) and select **Custom repositories**
3. Add this repository URL and select **Integration** as the category
4. Click **Add**
5. Search for "Lykyn" in HACS and install it
6. Restart Home Assistant

### Manual

1. Copy the `custom_components/lykyn` folder to your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant

## Configuration

1. Go to **Settings** > **Devices & Services** > **Add Integration**
2. Search for **Lykyn**
3. Enter your Lykyn account email and password (the same credentials you use at [lykyn.app](https://lykyn.app/))
4. All your devices will be automatically discovered

## How It Works

This integration communicates with the Lykyn cloud service (lykyn.app) using:

- **Socket.io** (WebSocket) for real-time push updates - your sensors update instantly when the device reports new data
- **REST API** for initial device discovery and authentication
- **NextAuth** credentials flow for authentication

The Lykyn grow kit uses an ESP32-C3 microcontroller that connects to WiFi and communicates with the cloud. This integration mirrors exactly what the official Lykyn app does, but brings it into Home Assistant.

### Architecture

```
Home Assistant
    |
    v
Lykyn Integration (this)
    |
    ├── REST API (HTTPS) ── Initial auth + device fetch
    |
    └── Socket.io (WSS) ── Real-time sensor data + control commands
         |
         v
    lykyn.app (Cloud)
         |
         v
    ESP32-C3 (Your Grow Kit)
```

## Protocol Documentation

The full reverse-engineered protocol is documented in [`custom_components/lykyn/PROTOCOL.md`](custom_components/lykyn/PROTOCOL.md), including:

- All REST API endpoints
- Socket.io events and payloads
- Device data model
- BLE setup protocol
- Authentication flow

## Reverse Engineering Story

This integration was built entirely through reverse engineering:

1. **Network reconnaissance** - Found the ESP32-C3 device on the local network
2. **APK decompilation** - Decompiled the Android app (com.swayfish.Lykyn) using jadx
3. **Discovered architecture** - The app is a thin WebView wrapper around a Nuxt.js SPA at lykyn.app
4. **JS bundle analysis** - Downloaded and analyzed 33 minified JavaScript bundles to extract the full Socket.io protocol, REST API endpoints, and device data model
5. **Built the integration** - Created a full HA custom component with real-time push updates

The entire reverse engineering and integration development was done by Claude Code (Anthropic's AI coding agent) in approximately 2-3 hours.

## Disclaimer

This is an unofficial, community-built integration. It is not affiliated with, endorsed by, or connected to Swayfish or Lykyn in any way. Use at your own risk. The integration relies on the Lykyn cloud service - if Lykyn changes their API, this integration may break.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! If you have a Lykyn device and find issues or want to add features, please open an issue or pull request.

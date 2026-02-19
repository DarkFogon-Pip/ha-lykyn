# Lykyn Mushroom Grow Kit - Protocol Documentation

Reverse-engineered from the Lykyn Android APK (com.swayfish.Lykyn) and
Nuxt.js SPA bundles at https://lykyn.app/

**Developer:** Swayfish Teknoloji Anonim Sirketi (Turkey)
**Contact:** ibrahim.b@swayfish.com

## Architecture Overview

```
Mobile App (WebView)
    |
    v
lykyn.app (Nuxt.js SPA)
    |
    ├── REST API (HTTPS)
    |   ├── GET  /api/user/devices          — list user's devices
    |   ├── GET  /api/admin/devices         — list all devices (admin)
    |   ├── GET  /api/device/online         — list online device IDs
    |   ├── GET  /api/device/{id}           — get single device info
    |   ├── GET  /api/device/{id}/data      — get sensor history
    |   ├── POST /api/auth/google-sign-in   — authenticate with Google
    |   ├── POST /api/user/subscription/add — add push subscription
    |   └── GET  /api/user/subscription/all — list push subscriptions
    |
    └── Socket.io (WSS, path: /socket.io)
        ├── Auth: extraHeaders.auth = JSON({type: "user", token: userId})
        |
        ├── Client → Server (emit)
        |   ├── "getOnlineDevices"  — request online device list
        |   ├── "updateDevice"      — update device settings
        |   └── "deleteDevice"      — delete a device
        |
        └── Server → Client (on)
            ├── "onlineDevices"     — array of online device IDs
            ├── "updateDevice"      — device was updated (by device or user)
            └── "deleteDevice"      — device was deleted
```

## Authentication

1. **Google Sign-In** → POST /api/auth/google-sign-in with `{idToken, source, clientId, name, email, picture}`
2. Server returns `{success: true, user: {email}, token}`
3. NextAuth credentials sign-in with `{email, token}`
4. Session provides `user.id` (used as Socket.io auth token)

### Socket.io Connection

```javascript
socket = io({
  extraHeaders: {
    auth: JSON.stringify({ type: "user", token: userId })
  }
});
// Default path: /socket.io
// Server: wss://lykyn.app
```

## Device Data Model

### Device Object (from /api/user/devices)

```json
{
  "id": "device-uuid",
  "name": "My Mushroom Kit",
  "user_id": "user-uuid",
  "type": "MUSHROOM",
  "info": { ... },
  "created_at": "2025-01-01T00:00:00Z"
}
```

### DeviceInfo Object (the `info` field)

```json
{
  "temp": 22.5,
  "hum": 87.3,
  "calibratedTemp": 22.8,
  "calibratedHum": 88.0,
  "calibrate": {},

  "controlType": "SMART",
  "selectedMushroom": "LionsMane",
  "selectedMicrogreens": "Arugula",

  "minTemp": 16,
  "maxTemp": 21,
  "minHum": 85,
  "maxHum": 90,

  "airin": 2,       // intake fan speed level (0=off, 1–3=low→high)
  "airout": 1,      // exhaust fan speed level (0=off, 1–3=low→high)

  "airinOn": 3,
  "airoutOn": 0,
  "airinOff": 1,
  "airoutOff": 1,

  "humidifier": true,
  "humidifierOnDuration": 5,
  "humidifierBelowMinDuration": 10,

  "light": true,
  "lightMode": "ANIMATION",
  "lightColor": "#FFFFFF",
  "lightBrightness": 50,
  "lightAnimation": "RAINBOW",

  "smart": {
    "humidifier": true,
    "light": true,
    "airinOn": 3,
    "airoutOn": 0,
    "airinOff": 1,
    "airoutOff": 1,
    "humidifierOnDuration": 5,
    "humidifierBelowMinDuration": 10
  }
}
```

### Light Animations
AURORA, BREATH, RGB_WAVE, RAINBOW, CONFETTI, SUNSETFADE

### Light Modes
ANIMATION (use lightAnimation), SOLID (use lightColor), OFF

## Socket.io Events

### emit "updateDevice"

```javascript
socket.emit("updateDevice", { info: { ... } }, { id: "device-uuid" });
socket.emit("updateDevice", { name: "New Name" }, { id: "device-uuid" });
```

### emit "deleteDevice"

```javascript
socket.emit("deleteDevice", { id: "device-uuid" });
```

### emit "getOnlineDevices"

```javascript
socket.emit("getOnlineDevices");
```

### on "onlineDevices"

```javascript
// deviceIds = ["uuid-1", "uuid-2", ...]
```

### on "updateDevice"

```javascript
// (device, source) — source truthy = from device itself
```

## REST API

### GET /api/device/{id}/data?limit=144&order=DESC

Sensor history records:
```json
{
  "data": [{
    "temp": 22.5, "hum": 87.3,
    "airin": 1, "airout": 0, "humidifier": 1, "light": 1,
    "minTemp": 16, "maxTemp": 21, "minHum": 85, "maxHum": 90,
    "created_at": "2025-01-15T14:30:00Z"
  }]
}
```

## BLE Protocol (WiFi Setup Only)

- Service: `4fafc201-1fb5-459e-8fcc-c5c9c331914b`
- Write: `beb5483e-36e1-4688-b7f5-ea07361b26a8`
- Notify: `6E400003-B5A3-F393-E0A9-E50E24DCCA9E`

## Hardware

ESP32-C3, 2.4 GHz WiFi, BLE, temp+humidity sensors, intake/exhaust fans, humidifier, LED strip.

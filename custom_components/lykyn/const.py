"""Constants for the Lykyn integration."""

DOMAIN = "lykyn"

CONF_EMAIL = "email"
CONF_PASSWORD = "password"

LYKYN_BASE_URL = "https://lykyn.app"
LYKYN_API_CSRF = "/api/auth/csrf"
LYKYN_API_CALLBACK = "/api/auth/callback/credentials"
LYKYN_API_SESSION = "/api/auth/session"
LYKYN_API_DEVICES = "/api/user/devices"
LYKYN_API_DEVICE = "/api/device/{device_id}"
LYKYN_API_DEVICE_DATA = "/api/device/{device_id}/data"
LYKYN_API_DEVICE_ONLINE = "/api/device/online"

PLATFORMS = ["sensor", "switch", "number", "light", "select"]

MUSHROOM_PRESETS = {
    "OysterPearlGrey": {"minTemp": 12, "maxTemp": 20, "minHum": 85, "maxHum": 89},
    "OysterBlue": {"minTemp": 10, "maxTemp": 18, "minHum": 85, "maxHum": 88},
    "OysterGolden": {"minTemp": 20, "maxTemp": 28, "minHum": 84, "maxHum": 88},
    "OysterPink": {"minTemp": 24, "maxTemp": 30, "minHum": 85, "maxHum": 88},
    "OysterPhoenix": {"minTemp": 18, "maxTemp": 27, "minHum": 85, "maxHum": 88},
    "OysterBlackPearl": {"minTemp": 15, "maxTemp": 21, "minHum": 84, "maxHum": 88},
    "KingOyster": {"minTemp": 15, "maxTemp": 18, "minHum": 83, "maxHum": 87},
    "LionsMane": {"minTemp": 16, "maxTemp": 21, "minHum": 85, "maxHum": 90},
    "BearsHead": {"minTemp": 14, "maxTemp": 19, "minHum": 84, "maxHum": 88},
    "Shiitake": {"minTemp": 13, "maxTemp": 22, "minHum": 85, "maxHum": 90},
    "Beech": {"minTemp": 12, "maxTemp": 18, "minHum": 86, "maxHum": 89},
    "Pioppino": {"minTemp": 18, "maxTemp": 23, "minHum": 85, "maxHum": 89},
    "Chestnut": {"minTemp": 16, "maxTemp": 20, "minHum": 84, "maxHum": 88},
    "Enoki": {"minTemp": 8, "maxTemp": 15, "minHum": 84, "maxHum": 89},
    "WoodEar": {"minTemp": 20, "maxTemp": 28, "minHum": 85, "maxHum": 90},
    "Button": {"minTemp": 16, "maxTemp": 19, "minHum": 86, "maxHum": 90},
    "Nameko": {"minTemp": 10, "maxTemp": 15, "minHum": 86, "maxHum": 90},
    "Maitake": {"minTemp": 12, "maxTemp": 18, "minHum": 85, "maxHum": 88},
    "AlmondAgaricus": {"minTemp": 20, "maxTemp": 26, "minHum": 84, "maxHum": 88},
    "Reishi": {"minTemp": 24, "maxTemp": 30, "minHum": 84, "maxHum": 88},
    "TurkeyTail": {"minTemp": 16, "maxTemp": 24, "minHum": 84, "maxHum": 89},
    "Cordyceps": {"minTemp": 16, "maxTemp": 20, "minHum": 85, "maxHum": 90},
    "Milky": {"minTemp": 28, "maxTemp": 32, "minHum": 85, "maxHum": 90},
    "PaddyStraw": {"minTemp": 28, "maxTemp": 35, "minHum": 85, "maxHum": 90},
    "SnowFungus": {"minTemp": 24, "maxTemp": 28, "minHum": 84, "maxHum": 90},
    "Blewit": {"minTemp": 10, "maxTemp": 16, "minHum": 84, "maxHum": 88},
    "ShaggyMane": {"minTemp": 10, "maxTemp": 18, "minHum": 85, "maxHum": 89},
    "DungLoving": {"minTemp": 14, "maxTemp": 18, "minHum": 85, "maxHum": 88},
    "CustomGrowthMode": {"minTemp": 15, "maxTemp": 25, "minHum": 85, "maxHum": 90},
}

LIGHT_ANIMATIONS = [
    "AURORA",
    "BREATH",
    "RGB_WAVE",
    "RAINBOW",
    "CONFETTI",
    "SUNSETFADE",
]

LIGHT_MODES = ["ANIMATION", "SOLID", "OFF"]

DEFAULT_LIGHT_SETTINGS = {
    "lightMode": "ANIMATION",
    "lightColor": "#FFFFFF",
    "lightBrightness": 50,
    "lightAnimation": "RAINBOW",
}

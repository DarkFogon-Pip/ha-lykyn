"""API client for the Lykyn cloud service."""

import asyncio
import json
import logging
from http.cookies import SimpleCookie

import aiohttp
import socketio

from .const import (
    LYKYN_API_CALLBACK,
    LYKYN_API_CSRF,
    LYKYN_API_DEVICE,
    LYKYN_API_DEVICE_DATA,
    LYKYN_API_DEVICE_ONLINE,
    LYKYN_API_DEVICES,
    LYKYN_API_SESSION,
    LYKYN_BASE_URL,
)

_LOGGER = logging.getLogger(__name__)


class LykynApiError(Exception):
    """Raised when the API returns an error."""


class LykynAuthError(LykynApiError):
    """Raised when authentication fails."""


class LykynApiClient:
    """Client for the Lykyn cloud API."""

    def __init__(self, email: str, password: str) -> None:
        self._email = email
        self._password = password
        self._session: aiohttp.ClientSession | None = None
        self._cookies: dict[str, str] = {}
        self._user_id: str | None = None
        self._sio: socketio.AsyncClient | None = None
        self._connected = False
        self._devices: dict[str, dict] = {}
        self._online_devices: list[str] = []
        self._update_callbacks: list = []

    @property
    def user_id(self) -> str | None:
        return self._user_id

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def devices(self) -> dict[str, dict]:
        return self._devices

    @property
    def online_devices(self) -> list[str]:
        return self._online_devices

    def register_update_callback(self, callback) -> None:
        self._update_callbacks.append(callback)

    def unregister_update_callback(self, callback) -> None:
        self._update_callbacks.remove(callback)

    async def _notify_update(self, device_id: str | None = None) -> None:
        for callback in self._update_callbacks:
            try:
                await callback(device_id)
            except Exception:
                _LOGGER.exception("Error in update callback")

    async def _ensure_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            jar = aiohttp.CookieJar()
            self._session = aiohttp.ClientSession(
                cookie_jar=jar,
                headers={
                    "User-Agent": "HomeAssistant/Lykyn",
                    "Accept-Encoding": "gzip, deflate",
                },
            )
        return self._session

    async def authenticate(self) -> bool:
        """Authenticate with the Lykyn cloud using email/password."""
        session = await self._ensure_session()

        # Step 1: Get CSRF token
        async with session.get(f"{LYKYN_BASE_URL}{LYKYN_API_CSRF}") as resp:
            if resp.status != 200:
                raise LykynAuthError(f"Failed to get CSRF token: {resp.status}")
            data = await resp.json()
            csrf_token = data.get("csrfToken")
            if not csrf_token:
                raise LykynAuthError("No CSRF token in response")

        # Step 2: POST credentials to NextAuth callback
        async with session.post(
            f"{LYKYN_BASE_URL}{LYKYN_API_CALLBACK}",
            data={
                "csrfToken": csrf_token,
                "email": self._email,
                "password": self._password,
                "redirect": "false",
                "json": "true",
                "callbackUrl": LYKYN_BASE_URL,
            },
            allow_redirects=False,
        ) as resp:
            # NextAuth returns 200 with {url} on success, or error
            if resp.status == 200:
                result = await resp.json()
                if "url" in result and "error" not in result.get("url", ""):
                    _LOGGER.debug("Authentication successful")
                else:
                    raise LykynAuthError("Invalid credentials")
            elif resp.status in (301, 302):
                location = resp.headers.get("Location", "")
                if "error" in location:
                    raise LykynAuthError("Invalid credentials")
            else:
                raise LykynAuthError(f"Auth failed with status {resp.status}")

        # Step 3: Get session to retrieve user ID
        async with session.get(f"{LYKYN_BASE_URL}{LYKYN_API_SESSION}") as resp:
            if resp.status != 200:
                raise LykynAuthError("Failed to get session")
            session_data = await resp.json()
            user = session_data.get("user", {})
            self._user_id = user.get("id")
            if not self._user_id:
                raise LykynAuthError("No user ID in session")
            _LOGGER.debug("Got user ID: %s", self._user_id)

        return True

    async def get_devices(self) -> list[dict]:
        """Fetch the list of user's devices."""
        session = await self._ensure_session()
        async with session.get(f"{LYKYN_BASE_URL}{LYKYN_API_DEVICES}") as resp:
            if resp.status != 200:
                raise LykynApiError(f"Failed to get devices: {resp.status}")
            devices = await resp.json()
            for device in devices:
                self._devices[device["id"]] = device
            return devices

    async def get_device(self, device_id: str) -> dict:
        """Fetch a single device."""
        session = await self._ensure_session()
        url = f"{LYKYN_BASE_URL}{LYKYN_API_DEVICE.format(device_id=device_id)}"
        async with session.get(url) as resp:
            if resp.status != 200:
                raise LykynApiError(f"Failed to get device: {resp.status}")
            device = await resp.json()
            self._devices[device_id] = device
            return device

    async def get_device_data(
        self, device_id: str, limit: int = 144
    ) -> list[dict]:
        """Fetch sensor history for a device."""
        session = await self._ensure_session()
        url = f"{LYKYN_BASE_URL}{LYKYN_API_DEVICE_DATA.format(device_id=device_id)}"
        async with session.get(url, params={"limit": limit, "order": "DESC"}) as resp:
            if resp.status != 200:
                raise LykynApiError(f"Failed to get device data: {resp.status}")
            data = await resp.json()
            return data.get("data", [])

    async def get_online_devices(self) -> list[str]:
        """Fetch online device IDs via REST."""
        session = await self._ensure_session()
        url = f"{LYKYN_BASE_URL}{LYKYN_API_DEVICE_ONLINE}"
        async with session.get(url) as resp:
            if resp.status != 200:
                return self._online_devices
            data = await resp.json()
            self._online_devices = data.get("devices", [])
            return self._online_devices

    async def connect_socket(self) -> None:
        """Connect to the Socket.io server for real-time updates."""
        if self._sio is not None and self._connected:
            return

        if not self._user_id:
            raise LykynApiError("Must authenticate before connecting socket")

        # Extract cookies from aiohttp session for socketio
        cookie_str = ""
        if self._session:
            jar = self._session.cookie_jar
            cookies = jar.filter_cookies(LYKYN_BASE_URL)
            cookie_str = "; ".join(f"{k}={v.value}" for k, v in cookies.items())

        self._sio = socketio.AsyncClient(
            reconnection=True,
            reconnection_attempts=0,  # infinite
            reconnection_delay=5,
            reconnection_delay_max=60,
            logger=False,
            engineio_logger=False,
        )

        auth_header = json.dumps({"type": "user", "token": self._user_id})

        @self._sio.event
        async def connect():
            _LOGGER.info("Socket.io connected to Lykyn")
            self._connected = True
            await self._sio.emit("getOnlineDevices")

        @self._sio.event
        async def disconnect():
            _LOGGER.warning("Socket.io disconnected from Lykyn")
            self._connected = False

        @self._sio.on("onlineDevices")
        async def on_online_devices(data):
            self._online_devices = data if data else []
            _LOGGER.debug("Online devices: %s", self._online_devices)
            await self._notify_update(None)

        @self._sio.on("updateDevice")
        async def on_update_device(device, *args):
            device_id = device.get("id")
            if device_id:
                self._devices[device_id] = device
                _LOGGER.debug("Device updated: %s (%s)", device.get("name"), device_id)
                await self._notify_update(device_id)

        @self._sio.on("realtimeDeviceUpdates")
        async def on_realtime_device_updates(data, *args):
            device_id = data.get("id") if isinstance(data, dict) else None
            if device_id and device_id in self._devices:
                device = self._devices[device_id]
                info = device.get("info", {})
                calibrate = info.get("calibrate", {})
                if "temp" in data:
                    calibrate["temp"] = data["temp"]
                if "hum" in data:
                    calibrate["hum"] = data["hum"]
                if "calibratedTemp" in data:
                    calibrate["calibratedTemp"] = data["calibratedTemp"]
                if "calibratedHum" in data:
                    calibrate["calibratedHum"] = data["calibratedHum"]
                info["calibrate"] = calibrate
                device["info"] = info
                _LOGGER.debug("Realtime update for %s: temp=%s hum=%s", device_id, data.get("temp"), data.get("hum"))
                await self._notify_update(device_id)

        @self._sio.on("deleteDevice")
        async def on_delete_device(device_id):
            self._devices.pop(device_id, None)
            _LOGGER.info("Device deleted: %s", device_id)
            await self._notify_update(device_id)

        headers = {"auth": auth_header}
        if cookie_str:
            headers["Cookie"] = cookie_str

        try:
            await self._sio.connect(
                LYKYN_BASE_URL,
                headers=headers,
                transports=["websocket", "polling"],
            )
        except Exception as err:
            _LOGGER.error("Failed to connect Socket.io: %s", err)
            raise LykynApiError(f"Socket.io connection failed: {err}") from err

    async def update_device(self, device_id: str, update: dict) -> None:
        """Send device update via Socket.io."""
        if not self._sio or not self._connected:
            raise LykynApiError("Not connected to Socket.io")

        await self._sio.emit("updateDevice", (update, {"id": device_id}))
        _LOGGER.debug("Sent updateDevice for %s: %s", device_id, update)

    async def update_device_info(self, device_id: str, info_update: dict) -> None:
        """Update the info field of a device.

        Handles nested sub-objects (smart, calibrate) by merging them
        rather than replacing.
        """
        device = self._devices.get(device_id, {})
        current_info = dict(device.get("info", {}))
        for key, value in info_update.items():
            if isinstance(value, dict) and isinstance(current_info.get(key), dict):
                merged = dict(current_info[key])
                merged.update(value)
                current_info[key] = merged
            else:
                current_info[key] = value
        await self.update_device(device_id, {"info": current_info})

    async def disconnect_socket(self) -> None:
        """Disconnect Socket.io."""
        if self._sio:
            try:
                await self._sio.disconnect()
            except Exception:
                pass
            self._sio = None
            self._connected = False

    async def close(self, *args) -> None:
        """Close all connections."""
        await self.disconnect_socket()
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

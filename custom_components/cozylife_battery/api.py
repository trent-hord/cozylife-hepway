"""API for communicating with the CozyLife Battery."""
import logging
import asyncio
import socket
import json
import time

from .const import PORT

_LOGGER = logging.getLogger(__name__)

TIMEOUT = 10
BUFFER_SIZE = 4096


class CozyLifeAPI:
    """API to communicate with the CozyLife device."""

    def __init__(self, host: str):
        """Initialize the API."""
        self.host = host
        self._state = {
            "1": 0,      # AC Power (0=off, 1=on)
            "2": 0,      # Battery Level (percentage) - Deprecated?
            "3": 0,      # Battery Level (percentage / 10)
            "4": 0,      # Output Watts
            "21": 0,     # Incoming Watts
            "30": 60,    # Minutes Remaining
            "47": 0      # AC Charging Power
        }
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None

    async def _ensure_connection(self):
        """Ensure we have an active TCP connection, reconnecting if needed."""
        if self._writer is not None and not self._writer.is_closing():
            return

        # Clean up any stale connection
        await self._close_connection()

        _LOGGER.debug("Opening connection to %s:%s", self.host, PORT)
        self._reader, self._writer = await asyncio.wait_for(
            asyncio.open_connection(self.host, PORT), timeout=TIMEOUT
        )

    async def _close_connection(self):
        """Close the TCP connection."""
        if self._writer:
            try:
                self._writer.close()
                await self._writer.wait_closed()
            except Exception:
                pass
        self._reader = None
        self._writer = None

    async def _send_tcp_command(self, cmd: int, payload: dict) -> dict:
        """Send a command and return the response.

        Uses a persistent connection. If the send fails on an existing
        connection, tears it down, reconnects once, and retries before
        propagating the error.
        """
        sn = str(int(round(time.time() * 1000)))
        message = {
            'pv': 0,
            'cmd': cmd,
            'sn': sn,
            'msg': payload
        }

        if cmd == 3: # SET
            keys = [int(k) for k in payload.keys()]
            message['msg'] = {'attr': keys, 'data': payload}

        json_str = json.dumps(message)
        packet = (json_str + "\r\n").encode('utf-8')

        # Try twice: once on the existing connection, once after reconnecting
        for attempt in range(2):
            try:
                await self._ensure_connection()

                _LOGGER.debug("Sending to %s: %s", self.host, packet)
                self._writer.write(packet)
                await self._writer.drain()

                data = await asyncio.wait_for(self._reader.readline(), timeout=TIMEOUT)

                if not data:
                    raise ConnectionError("Device closed connection (empty response)")

                response_str = data.decode('utf-8').strip()
                _LOGGER.debug("Received from %s: %s", self.host, response_str)

                return json.loads(response_str)

            except (asyncio.TimeoutError, OSError, json.JSONDecodeError) as err:
                await self._close_connection()
                if attempt == 0:
                    _LOGGER.debug(
                        "Connection to %s failed (%s), reconnecting...",
                        self.host, err,
                    )
                    continue
                _LOGGER.error("Connection error to %s: %s", self.host, err)
                raise

    async def update(self):
        """Fetch the latest data from the device."""
        try:
            # Query specific attributes we track
            attr_list = [int(k) for k in self._state.keys()]
            response = await self._send_tcp_command(2, {'attr': attr_list})
            if 'msg' in response and 'data' in response['msg']:
                # The data comes as a dictionary of attributes
                self._state.update(response['msg']['data'])
            elif 'error' in response:
                _LOGGER.error("Device reported error: %s", response['error'])
        except Exception as e:
            _LOGGER.error("Error updating status: %s", e)
            raise

        return self._state

    async def set_state(self, attribute_id: str, value):
        """Set a specific attribute on the device."""
        try:
            # attribute_id is expected to be a string key for the payload
            payload = {attribute_id: int(value)}
            await self._send_tcp_command(3, payload)

            # Optimistic update (store as int to match what the device expects)
            self._state[attribute_id] = int(value)
            return True
        except Exception as e:
             _LOGGER.error("Error setting state for %s: %s", attribute_id, e)
             return False

    async def async_close(self):
        """Close the persistent connection (called on integration unload)."""
        await self._close_connection()

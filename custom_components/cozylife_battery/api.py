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
            "4": 0,      # Output Watts
            "21": 0,     # Incoming Watts
            "30": 60     # Minutes Remaining
        }

    async def _send_tcp_command(self, cmd: int, payload: dict) -> dict:
        """Send a command and return the response."""
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

        reader = writer = None
        try:
            _LOGGER.debug("Connecting to %s:%s", self.host, PORT)
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, PORT), timeout=TIMEOUT
            )

            _LOGGER.debug("Sending to %s: %s", self.host, packet)
            writer.write(packet)
            await writer.drain()

            data = await asyncio.wait_for(reader.read(BUFFER_SIZE), timeout=TIMEOUT)
            response_str = data.decode('utf-8').strip()
            _LOGGER.debug("Received from %s: %s", self.host, response_str)

            return json.loads(response_str)

        except (asyncio.TimeoutError, ConnectionError, socket.gaierror) as err:
            _LOGGER.error("Connection error to %s: %s", self.host, err)
            raise
        except json.JSONDecodeError as err:
            _LOGGER.error("JSON decode error from %s: %s", self.host, err)
            raise
        finally:
            if writer:
                writer.close()
                try:
                    await writer.wait_closed()
                except Exception:
                    pass

    async def update(self):
        """Fetch the latest data from the device."""
        try:
            # Query all attributes using [0] based on reference implementation
            response = await self._send_tcp_command(2, {'attr': [0]})
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

            # Optimistic update
            self._state[attribute_id] = value
            return True
        except Exception as e:
             _LOGGER.error("Error setting state for %s: %s", attribute_id, e)
             return False

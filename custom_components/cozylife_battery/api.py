"""API for communicating with the CozyLife Battery."""
import logging
import asyncio
import socket

_LOGGER = logging.getLogger(__name__)

# TODO: Update these constants with the correct protocol details
PORT = 5555
TIMEOUT = 10
BUFFER_SIZE = 1024

class CozyLifeAPI:
    """API to communicate with the CozyLife device."""

    def __init__(self, host: str):
        """Initialize the API."""
        self.host = host
        self._state = {
            "1": 0,      # AC Power (0=off, 1=on)
            "4": 0,      # Output Watts
            "30": 60     # Minutes Remaining
        }

    async def _send_command(self, command: bytes) -> bytes:
        """Send a command and return the response."""
        reader = writer = None
        try:
            _LOGGER.debug("Connecting to %s:%s", self.host, PORT)
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, PORT), timeout=TIMEOUT
            )

            _LOGGER.debug("Sending to %s: %s", self.host, command)
            writer.write(command)
            await writer.drain()

            data = await asyncio.wait_for(reader.read(BUFFER_SIZE), timeout=TIMEOUT)
            _LOGGER.debug("Received from %s: %s", self.host, data)

            return data

        except (asyncio.TimeoutError, ConnectionError, socket.gaierror) as err:
            _LOGGER.error("Connection error to %s: %s", self.host, err)
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
        # TODO: Implement actual protocol.
        # Example:
        # try:
        #     response = await self._send_command(b'{"cmd": "query"}')
        #     # Parse response
        #     # self._state = parse(response)
        # except Exception:
        #     # Keep old state or raise
        #     pass

        # MOCK DATA (Remove when protocol is implemented)
        await asyncio.sleep(0.1)
        _LOGGER.info("Mock update: %s", self._state)
        return self._state

    async def set_state(self, attribute_id: str, value):
        """Set a specific attribute on the device."""
        # TODO: Implement actual protocol.
        # Example:
        # payload = json.dumps({"attr": attribute_id, "val": value}).encode()
        # await self._send_command(payload)

        # MOCK DATA (Remove when protocol is implemented)
        _LOGGER.info("Mock set_state: %s = %s", attribute_id, value)
        if attribute_id == "1":
             self._state[attribute_id] = 1 if value else 0
        elif attribute_id in self._state:
            self._state[attribute_id] = value

        return True

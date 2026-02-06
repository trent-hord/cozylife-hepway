import sys
from unittest.mock import MagicMock, AsyncMock

# Helper to mock modules
def mock_modules():
    modules = [
        "homeassistant",
        "homeassistant.components",
        "homeassistant.components.sensor",
        "homeassistant.components.switch",
        "homeassistant.config_entries",
        "homeassistant.const",
        "homeassistant.core",
        "homeassistant.helpers",
        "homeassistant.helpers.entity_platform",
        "homeassistant.helpers.update_coordinator",
        "homeassistant.helpers.entity",
        "homeassistant.data_entry_flow",
    ]
    for module in modules:
        sys.modules[module] = MagicMock()

mock_modules()

# specific constants
sys.modules["homeassistant.const"].CONF_HOST = "host"
sys.modules["homeassistant.const"].UnitOfPower = MagicMock()
sys.modules["homeassistant.const"].UnitOfTime = MagicMock()
sys.modules["homeassistant.const"].Platform = MagicMock()

# Mocking ConfigFlow
class MockConfigFlow:
    def __init__(self):
        self.async_show_form = MagicMock(return_value={"type": "form"})
        self.async_create_entry = MagicMock(return_value={"type": "create_entry"})

sys.modules["homeassistant.config_entries"].ConfigFlow = MockConfigFlow

import pytest
from unittest.mock import patch

@pytest.fixture
def mock_api():
    """Mock the CozyLifeAPI."""
    with patch("custom_components.cozylife_battery.config_flow.CozyLifeAPI") as mock:
        instance = mock.return_value
        instance.test_connection = AsyncMock(return_value=True)
        instance.update = AsyncMock(return_value={})
        instance.set_state = AsyncMock(return_value=True)
        yield instance

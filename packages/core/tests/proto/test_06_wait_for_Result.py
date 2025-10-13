import asyncio
import pytest
from unittest.mock import patch
from interfaces.__mocks__.connection import MockDeviceConnection
from core import SDK
from tests.proto.__fixtures__.wait_For_result import fixtures, constant_date
from tests.__fixtures__.config import config as test_config


class TestSDKWaitForResult:
    """Test sdk.wait_for_result"""

    @pytest.fixture
    async def setup(self):
        """Setup fixture for each test"""
        # Mock the constant date - use UTC timestamp to match TypeScript Date.now()
        import calendar

        utc_timestamp = (
            calendar.timegm(constant_date.timetuple())
            + constant_date.microsecond / 1000000
        )
        with (
            patch("time.time", return_value=utc_timestamp),
            patch("core.encoders.packet.packet.time.time", return_value=utc_timestamp),
            patch(
                "os.times", return_value=type("MockTimes", (), {"elapsed": 16778725})()
            ),
        ):
            connection = await MockDeviceConnection.create()
            applet_id = 0

            async def on_data():
                # Send ACK packet first
                await connection.mock_device_send(
                    bytes([170, 1, 7, 0, 1, 0, 1, 0, 69, 133])
                )
                # Then send SDK Version: 3.0.1, Packet Version: v3
                await connection.mock_device_send(
                    bytes([170, 88, 12, 0, 1, 0, 1, 0, 3, 0, 0, 0, 1, 173, 177])
                )

            connection.configure_listeners(on_data)

            sdk = await SDK.create(connection, applet_id)
            await sdk.before_operation()
            connection.remove_listeners()

            yield connection, sdk

            await connection.destroy()

    @pytest.mark.parametrize("test_case", fixtures["invalid_args"])
    def test_should_throw_error_with_invalid_arguments(self, setup, test_case):
        """Test error with invalid arguments"""

        async def _test():
            connection, sdk = await setup.__anext__()

            with pytest.raises(Exception):
                await sdk.wait_for_result(
                    {
                        "sequence_number": test_case["sequence_number"],
                        "options": {
                            "interval": 20,
                            "timeout": test_config.defaultTimeout,
                            "max_tries": 1,
                        },
                    }
                )

        asyncio.run(_test())

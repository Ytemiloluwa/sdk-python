import asyncio
import pytest
from unittest.mock import patch

from interfaces.__mocks__.connection import MockDeviceConnection
from interfaces.errors.connection_error import DeviceConnectionError
from core import SDK
from tests.proto.__fixtures__.get_status import fixtures, constant_date
from tests.__fixtures__.config import config as test_config


class TestSDKGetStatus:
    """Test sdk.get_status"""

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
            applet_id = 12

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

    @pytest.mark.parametrize("test_case", fixtures["valid"])
    def test_should_throw_error_when_device_is_disconnected(self, setup, test_case):
        """Test error when device is disconnected"""

        async def _test():
            connection, sdk = await setup.__anext__()

            from unittest.mock import Mock

            on_data = Mock()

            connection.configure_listeners(on_data)
            await connection.destroy()

            with pytest.raises(DeviceConnectionError):
                await sdk.get_status(1, test_config.defaultTimeout)

            assert on_data.call_count == 0

        asyncio.run(_test())

    @pytest.mark.parametrize("test_case", fixtures["valid"])
    def test_should_throw_error_when_device_is_disconnected_in_between(
        self, setup, test_case
    ):
        """Test error when device is disconnected during operation"""

        async def _test():
            connection, sdk = await setup.__anext__()

            async def on_data(data: bytes):
                assert test_case["status_request"] == data
                i = 0
                for ack_packet in test_case["ack_packets"]:
                    if i >= len(test_case["ack_packets"]) - 1:
                        await connection.destroy()
                    else:
                        await connection.mock_device_send(ack_packet)
                    i += 1

            connection.configure_listeners(on_data)

            with pytest.raises(DeviceConnectionError):
                await sdk.get_status(1, test_config.defaultTimeout)

        asyncio.run(_test())

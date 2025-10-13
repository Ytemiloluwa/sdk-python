import asyncio
import pytest
from interfaces.errors.connection_error import DeviceConnectionError
from interfaces.__mocks__.connection import MockDeviceConnection
from core import SDK
from tests.__fixtures__.config import config
from tests.legacy.__fixtures__.receiveLegacyCommand import (
    legacy_receive_command_test_cases,
)


class TestReceiveLegacyCommand:
    @pytest.fixture
    async def setup(self):
        """Setup fixture for each test"""
        connection = await MockDeviceConnection.create()

        async def on_data():
            # SDK Version: 0.1.16, PacketVersion: v1
            await connection.mock_device_send(
                bytes(
                    [
                        170,
                        1,
                        7,
                        0,
                        1,
                        0,
                        1,
                        0,
                        69,
                        133,
                        170,
                        88,
                        12,
                        0,
                        1,
                        0,
                        1,
                        0,
                        0,
                        0,
                        1,
                        0,
                        16,
                        118,
                        67,
                    ]
                )
            )

        connection.configure_listeners(on_data)

        sdk = await SDK.create(connection, 0)  # appletId = 0
        await sdk.before_operation()
        connection.remove_listeners()

        yield connection, sdk

        await sdk.destroy()

    @pytest.mark.parametrize("test_case", legacy_receive_command_test_cases["valid"])
    def test_should_be_able_to_receive_data(self, setup, test_case):
        """Test receiving legacy command data for valid cases"""

        async def _test():
            connection, sdk = await setup.__anext__()

            async def send_data_from_device(packets_from_device):
                for data in packets_from_device:
                    await connection.mock_device_send(data)

            # Determine timeout based on data length
            timeout = (
                1200
                if len(test_case["output"]["data"]) > 200
                else config.defaultTimeout
            )

            # Execute both operations concurrently
            response, _ = await asyncio.gather(
                sdk.deprecated.receive_legacy_command(
                    test_case["params"]["allAcceptableCommands"],
                    timeout,
                ),
                send_data_from_device(test_case["packetsFromDevice"]),
            )

            assert response["data"] == test_case["output"]["data"]
            assert response["commandType"] == test_case["output"]["commandType"]

        asyncio.run(_test())

    @pytest.mark.parametrize("test_case", legacy_receive_command_test_cases["valid"])
    def test_should_throw_error_when_device_is_disconnected(self, setup, test_case):
        """Test error when device is disconnected"""

        async def _test():
            connection, sdk = await setup.__anext__()

            await connection.destroy()

            with pytest.raises(DeviceConnectionError):
                await sdk.deprecated.receive_legacy_command(
                    test_case["params"]["allAcceptableCommands"],
                    config.defaultTimeout,
                )

        asyncio.run(_test())

    @pytest.mark.parametrize("test_case", legacy_receive_command_test_cases["valid"])
    def test_should_throw_error_when_device_is_disconnected_in_between(
        self, setup, test_case
    ):
        """Test error when device is disconnected during operation"""

        async def _test():
            connection, sdk = await setup.__anext__()

            async def send_data_from_device(packets_from_device):
                for i, data in enumerate(packets_from_device):
                    if i >= len(packets_from_device) - 1:
                        await connection.destroy()
                    else:
                        await connection.mock_device_send(data)

            # Execute both operations concurrently and check for rejection
            results = await asyncio.gather(
                sdk.deprecated.receive_legacy_command(
                    test_case["params"]["allAcceptableCommands"],
                    config.defaultTimeout,
                ),
                send_data_from_device(test_case["packetsFromDevice"]),
                return_exceptions=True,
            )

            # Check that the first operation (receive_legacy_command) failed
            assert isinstance(results[0], DeviceConnectionError)

        asyncio.run(_test())

    @pytest.mark.parametrize(
        "test_case", legacy_receive_command_test_cases["invalidArgs"]
    )
    def test_should_throw_error_with_invalid_arguments(self, setup, test_case):
        """Test error handling for invalid arguments"""

        async def _test():
            connection, sdk = await setup.__anext__()

            with pytest.raises(Exception):
                await sdk.deprecated.receive_legacy_command(
                    test_case["allAcceptableCommands"],
                    config.defaultTimeout,
                )

        asyncio.run(_test())

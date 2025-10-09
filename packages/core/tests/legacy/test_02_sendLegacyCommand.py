import asyncio
import pytest
import random
from unittest.mock import Mock

from interfaces.errors.connection_error import DeviceConnectionError
from interfaces.errors.communication_error import DeviceCommunicationError
from interfaces.__mocks__.connection import MockDeviceConnection

from core import SDK
from tests.__fixtures__.config import config
from tests.legacy.__fixtures__.sendLegacyCommand import legacy_send_command_test_cases


class TestSendLegacyCommand:
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

    @pytest.mark.parametrize("test_case", legacy_send_command_test_cases["valid"])
    def test_should_be_able_to_send_data(self, setup, test_case):
        """Test sending legacy command data for valid cases"""

        async def _test():
            connection, sdk = await setup.__anext__()

            async def on_data(data: bytes):
                packet_index = next(
                    (i for i, elem in enumerate(test_case["packets"]) if elem == data),
                    -1,
                )
                assert data in test_case["packets"]
                assert packet_index >= 0
                await connection.mock_device_send(test_case["ackPackets"][packet_index])

            connection.configure_listeners(on_data)
            await sdk.deprecated.send_legacy_command(
                test_case["params"]["command"],
                test_case["params"]["data"],
                1,
                config.defaultTimeout,
            )

        asyncio.run(_test())

    @pytest.mark.parametrize("test_case", legacy_send_command_test_cases["valid"])
    def test_should_be_able_to_handle_multiple_retries(self, setup, test_case):
        """Test retry functionality for valid cases"""

        async def _test():
            connection, sdk = await setup.__anext__()

            max_timeout_triggers = 3
            total_timeout_triggers = 0
            max_tries = 3
            retries = {}

            async def on_data(data: bytes):
                nonlocal total_timeout_triggers
                packet_index = next(
                    (i for i, elem in enumerate(test_case["packets"]) if elem == data),
                    -1,
                )
                assert data in test_case["packets"]
                assert packet_index >= 0

                current_retry = retries.get(packet_index, 0) + 1

                do_trigger_error = (
                    random.random() > 0.5
                    and current_retry < max_tries
                    and total_timeout_triggers < max_timeout_triggers
                )

                if not do_trigger_error:
                    await connection.mock_device_send(
                        test_case["ackPackets"][packet_index]
                    )
                else:
                    total_timeout_triggers += 1
                    retries[packet_index] = current_retry

            connection.configure_listeners(on_data)
            await sdk.deprecated.send_legacy_command(
                test_case["params"]["command"],
                test_case["params"]["data"],
                max_tries,
                config.defaultTimeout,
            )

        asyncio.run(_test())

    @pytest.mark.parametrize("test_case", legacy_send_command_test_cases["valid"])
    def test_should_throw_error_when_device_is_disconnected(self, setup, test_case):
        """Test error when device is disconnected"""

        async def _test():
            connection, sdk = await setup.__anext__()

            on_data = Mock()
            connection.configure_listeners(on_data)

            await connection.destroy()

            with pytest.raises((DeviceConnectionError, DeviceCommunicationError)):
                await sdk.deprecated.send_legacy_command(
                    test_case["params"]["command"],
                    test_case["params"]["data"],
                    1,
                    config.defaultTimeout,
                )

            assert on_data.call_count == 0

        asyncio.run(_test())

    @pytest.mark.parametrize("test_case", legacy_send_command_test_cases["valid"])
    def test_should_throw_error_when_device_is_disconnected_in_between(
        self, setup, test_case
    ):
        async def _test():
            connection, sdk = await setup.__anext__()

            async def on_data(data: bytes):
                packet_index = next(
                    (i for i, elem in enumerate(test_case["packets"]) if elem == data),
                    -1,
                )
                if len(test_case["packets"]) == 1:
                    await connection.destroy()
                    return

                await connection.mock_device_send(test_case["ackPackets"][packet_index])
                if packet_index == 0:
                    await connection.destroy()

            connection.configure_listeners(on_data)

            if len(test_case["packets"]) == 1:
                try:
                    await sdk.deprecated.send_legacy_command(
                        test_case["params"]["command"],
                        test_case["params"]["data"],
                        1,
                        config.defaultTimeout,
                    )
                    assert (
                        False
                    ), "Expected DeviceCommunicationError but no error was raised"
                except DeviceCommunicationError:

                    pass
                except Exception as e:
                    pass
            else:
                with pytest.raises((DeviceConnectionError, DeviceCommunicationError)):
                    await sdk.deprecated.send_legacy_command(
                        test_case["params"]["command"],
                        test_case["params"]["data"],
                        1,
                        config.defaultTimeout,
                    )

        asyncio.run(_test())

    @pytest.mark.parametrize("test_case", legacy_send_command_test_cases["invalidArgs"])
    def test_should_throw_error_with_invalid_arguments(self, setup, test_case):
        """Test error handling for invalid arguments"""

        async def _test():
            connection, sdk = await setup.__anext__()

            with pytest.raises(Exception):
                await sdk.deprecated.send_legacy_command(
                    test_case["command"],
                    test_case["data"],
                    test_case["maxTries"],
                    config.defaultTimeout,
                )

        asyncio.run(_test())

import asyncio
import pytest
import random
from unittest.mock import Mock

from interfaces.errors.bootloader_error import DeviceBootloaderError
from interfaces.errors.connection_error import DeviceConnectionError
from interfaces import DeviceState
from interfaces.__mocks__.connection import MockDeviceConnection

from core import SDK
from tests.__fixtures__.config import config
from tests.bootloader.__fixtures__.sendBootloaderData import (
    send_bootloader_data_test_cases,
)


class TestSendBootloaderData:
    @pytest.fixture
    async def setup(self):
        """Setup fixture for each test"""
        connection = await MockDeviceConnection.create()
        connection.configure_device(DeviceState.BOOTLOADER, "MOCK")

        sdk = await SDK.create(connection, 0)  # appletId = 0
        await connection.before_operation()
        connection.remove_listeners()

        yield connection, sdk

        await sdk.destroy()

    @pytest.mark.parametrize("test_case", send_bootloader_data_test_cases["valid"])
    def test_should_be_able_to_send_data(self, setup, test_case):
        """Test sending bootloader data for valid cases"""

        async def _test():
            connection, sdk = await setup.__anext__()

            async def on_data(data: bytes):
                packet_index = next(
                    (i for i, elem in enumerate(test_case["packets"]) if elem == data),
                    -1,
                )
                assert data in test_case["packets"]
                assert packet_index >= 0
                await connection.mock_device_send(bytes([6]))  # ACK response

            connection.configure_listeners(on_data)

            # Queue the receiving mode packet
            await connection.mock_device_send(bytes([67]))  # RECEIVING_MODE_PACKET

            await sdk.send_bootloader_data(
                test_case["data"],
                None,
                {
                    "maxTries": 1,
                    "firstTimeout": config.defaultTimeout,
                    "timeout": config.defaultTimeout,
                },
            )

        asyncio.run(_test())

    @pytest.mark.parametrize("test_case", send_bootloader_data_test_cases["valid"])
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
                    random.random() < 0.5
                    and current_retry < max_tries
                    and total_timeout_triggers < max_timeout_triggers
                )

                if not do_trigger_error:
                    await connection.mock_device_send(bytes([6]))  # ACK response
                else:
                    total_timeout_triggers += 1
                    retries[packet_index] = current_retry

            connection.configure_listeners(on_data)

            # Queue the receiving mode packet
            await connection.mock_device_send(bytes([67]))  # RECEIVING_MODE_PACKET

            await sdk.send_bootloader_data(
                test_case["data"],
                None,
                {
                    "timeout": config.defaultTimeout,
                    "firstTimeout": config.defaultTimeout,
                    "maxTries": max_tries,
                },
            )

        asyncio.run(_test())

    @pytest.mark.parametrize("test_case", send_bootloader_data_test_cases["valid"])
    def test_should_return_valid_errors_when_device_is_not_in_receiving_mode(
        self, setup, test_case
    ):
        """Test error when device is not in receiving mode"""

        async def _test():
            connection, sdk = await setup.__anext__()

            on_data = Mock()
            connection.configure_listeners(on_data)

            # Don't queue receiving mode packet - should cause error
            with pytest.raises(DeviceBootloaderError):
                await sdk.send_bootloader_data(
                    test_case["data"],
                    None,
                    {
                        "timeout": config.defaultTimeout,
                        "firstTimeout": config.defaultTimeout,
                        "maxTries": 1,
                    },
                )

            assert on_data.call_count == 0

        asyncio.run(_test())

    @pytest.mark.parametrize("test_case", send_bootloader_data_test_cases["valid"])
    def test_should_return_valid_errors_when_device_is_disconnected(
        self, setup, test_case
    ):
        """Test error when device is disconnected"""

        async def _test():
            connection, sdk = await setup.__anext__()

            on_data = Mock()
            connection.configure_listeners(on_data)

            # Queue receiving mode packet
            await connection.mock_device_send(bytes([67]))
            await connection.destroy()

            with pytest.raises(DeviceConnectionError):
                await sdk.send_bootloader_data(
                    test_case["data"],
                    None,
                    {
                        "timeout": config.defaultTimeout,
                        "firstTimeout": config.defaultTimeout,
                        "maxTries": 1,
                    },
                )

            assert on_data.call_count == 0

        asyncio.run(_test())

    @pytest.mark.parametrize("test_case", send_bootloader_data_test_cases["valid"])
    def test_should_return_valid_errors_when_device_is_disconnected_in_between(
        self, setup, test_case
    ):
        """Test error when device is disconnected during operation"""

        async def _test():
            connection, sdk = await setup.__anext__()

            async def on_data(data: bytes):
                packet_index = next(
                    (i for i, elem in enumerate(test_case["packets"]) if elem == data),
                    -1,
                )
                assert data in test_case["packets"]
                assert packet_index >= 0
                if packet_index >= len(test_case["packets"]) - 1:
                    await connection.destroy()
                else:
                    await connection.mock_device_send(bytes([6]))

            connection.configure_listeners(on_data)

            # Queue receiving mode packet
            await connection.mock_device_send(bytes([67]))

            with pytest.raises(DeviceConnectionError):
                await sdk.send_bootloader_data(
                    test_case["data"],
                    None,
                    {
                        "timeout": config.defaultTimeout,
                        "firstTimeout": config.defaultTimeout,
                        "maxTries": 1,
                    },
                )

        asyncio.run(_test())

    @pytest.mark.parametrize(
        "test_case", send_bootloader_data_test_cases["invalidArgs"]
    )
    def test_should_throw_error_with_invalid_arguments(self, setup, test_case):
        """Test error handling for invalid arguments"""

        async def _test():
            connection, sdk = await setup.__anext__()

            with pytest.raises(Exception):
                await sdk.send_bootloader_data(test_case["data"])

        asyncio.run(_test())

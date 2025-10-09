import asyncio
import pytest

from interfaces.errors.connection_error import DeviceConnectionError
from interfaces import DeviceState
from interfaces.__mocks__.connection import MockDeviceConnection

from core import SDK
from tests.__fixtures__.config import config


class TestSendBootloaderAbort:
    @pytest.fixture
    async def setup(self):
        """Setup fixture for each test"""
        connection = await MockDeviceConnection.create()
        connection.configure_device(DeviceState.BOOTLOADER, "MOCK")

        sdk = await SDK.create(connection, 0)  # appletId = 0
        await connection.before_operation()
        connection.remove_listeners()

        yield connection, sdk

        await connection.destroy()

    def test_should_be_able_to_send_abort(self, setup):
        """Test basic abort functionality"""
        async def _test():
            connection, sdk = await setup.__anext__()

            call_count = 0

            async def on_data(data: bytes):
                nonlocal call_count
                call_count += 1
                assert data == bytes([65])
                await connection.mock_device_send(bytes([24]))

            connection.configure_listeners(on_data)
            await sdk.send_bootloader_abort({"maxTries": 1})

            assert call_count == 1

        asyncio.run(_test())

    def test_should_be_able_to_handle_multiple_retries(self, setup):
        """Test retry functionality"""
        async def _test():
            connection, sdk = await setup.__anext__()

            max_tries = 3
            current_retry = 0
            call_count = 0

            async def on_data(data: bytes):
                nonlocal current_retry, call_count
                call_count += 1
                assert data == bytes([65])
                current_retry += 1
                if current_retry >= max_tries:
                    await connection.mock_device_send(bytes([24]))

            connection.configure_listeners(on_data)
            await sdk.send_bootloader_abort({
                "firstTimeout": config.defaultTimeout,
                "timeout": config.defaultTimeout,
                "maxTries": max_tries,
            })

            assert call_count == max_tries

        asyncio.run(_test())

    def test_should_return_valid_errors_when_device_is_disconnected(self, setup):
        """Test error handling when device is disconnected"""
        async def _test():
            connection, sdk = await setup.__anext__()

            call_count = 0

            async def on_data(data: bytes):
                nonlocal call_count
                call_count += 1
                assert data == bytes([65])
                await connection.mock_device_send(bytes([24]))

            connection.configure_listeners(on_data)
            await connection.destroy()

            with pytest.raises(DeviceConnectionError):
                await sdk.send_bootloader_abort({"maxTries": 1})

            assert call_count == 0

        asyncio.run(_test())

    def test_should_return_valid_errors_when_device_is_disconnected_in_between(self, setup):
        """Test error handling when device is disconnected during operation"""
        async def _test():
            connection, sdk = await setup.__anext__()

            call_count = 0

            async def on_data(data: bytes):
                nonlocal call_count
                call_count += 1
                assert data == bytes([65])
                await connection.destroy()

            connection.configure_listeners(on_data)

            with pytest.raises(DeviceConnectionError):
                await sdk.send_bootloader_abort({"maxTries": 1})

            assert call_count == 1

        asyncio.run(_test())
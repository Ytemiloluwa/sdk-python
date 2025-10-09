import asyncio
import pytest
from interfaces import DeviceState
from interfaces.__mocks__.connection import MockDeviceConnection
from interfaces.errors.communication_error import DeviceCommunicationErrorType, deviceCommunicationErrorTypeDetails

from core import SDK


class TestBootloaderOperation:
    @pytest.fixture
    async def setup(self):
        connection = await MockDeviceConnection.create()
        connection.configure_device(DeviceState.BOOTLOADER, "MOCK")

        sdk = await SDK.create(connection, 0)

        if not hasattr(sdk, 'deprecated') or sdk.deprecated is None:
            from core.deprecated import DeprecatedCommunication
            sdk.deprecated = DeprecatedCommunication(sdk)

        sdk.get_version = lambda: "0.0.0"
        sdk.get_packet_version = lambda: None
        sdk.get_connection = lambda: connection
        sdk.get_device_state = lambda: DeviceState.BOOTLOADER
        sdk.is_in_bootloader = lambda: True

        async def async_get_device_state():
            return DeviceState.BOOTLOADER
        
        async def async_is_in_bootloader():
            return True
        
        sdk.get_device_state = async_get_device_state
        sdk.is_in_bootloader = async_is_in_bootloader
        await connection.before_operation()
        connection.remove_listeners()

        yield connection, sdk

        await connection.destroy()

    def test_should_have_the_right_configuration(self, setup):
        """Test SDK configuration in bootloader mode"""
        async def _test():
            connection, sdk = await setup.__anext__()
            
            assert sdk.get_version() == "0.0.0"
            assert sdk.get_packet_version() is None
            assert await sdk.get_device_state() == DeviceState.BOOTLOADER
            assert await sdk.is_in_bootloader() is True
            assert await sdk.is_supported() is False

        asyncio.run(_test())

    def test_should_be_able_to_send_abort(self, setup):
        """Test sending bootloader abort command"""
        async def _test():
            connection, sdk = await setup.__anext__()

            async def on_data(data: bytes):
                assert data == bytes([65])
                await connection.mock_device_send(bytes([24]))

            connection.configure_listeners(on_data)
            await sdk.send_bootloader_abort()

        asyncio.run(_test())

    def test_should_be_able_to_send_data(self, setup):
        """Test sending bootloader data"""
        async def _test():
            connection, sdk = await setup.__anext__()

            packets = [
                bytes([
                    1, 1, 254, 20, 121, 36, 79, 49, 242, 255, 255, 255, 255, 255, 255, 255,
                    255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                    255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                    255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                    255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                    255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                    255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                    255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                    255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                    255, 255, 255, 250, 80,
                ]),
                bytes([4]),
            ]

            async def on_data(data: bytes):
                packet_index = next((i for i, elem in enumerate(packets) if elem == data), -1)
                assert data in packets
                assert packet_index >= 0
                await connection.mock_device_send(bytes([6]))  # ACK response

            connection.configure_listeners(on_data)

            # Queue the receiving mode packet
            await connection.mock_device_send(bytes([67]))  # RECEIVING_MODE_PACKET

            await sdk.send_bootloader_data("1479244f31f2")

        asyncio.run(_test())

    def test_should_throw_error_when_accessing_other_functions_for_v3(self, setup):
        """Test that other SDK functions throw errors in bootloader mode"""
        async def _test():
            connection, sdk = await setup.__anext__()

            in_bootloader_error = deviceCommunicationErrorTypeDetails[
                DeviceCommunicationErrorType.IN_BOOTLOADER
            ]["message"]

            # Test deprecated legacy commands
            with pytest.raises(Exception) as exc_info:
                await sdk.deprecated.send_legacy_command(1, "00")
            assert in_bootloader_error in str(exc_info.value)

            with pytest.raises(Exception) as exc_info:
                await sdk.deprecated.receive_legacy_command([1], 500)
            assert in_bootloader_error in str(exc_info.value)

            # Test deprecated raw commands
            with pytest.raises(Exception) as exc_info:
                await sdk.deprecated.send_command({
                    "commandType": 1,
                    "data": "00",
                    "sequenceNumber": 1,
                })
            assert in_bootloader_error in str(exc_info.value)

            with pytest.raises(Exception) as exc_info:
                await sdk.deprecated.get_command_output(1)
            assert in_bootloader_error in str(exc_info.value)

            with pytest.raises(Exception) as exc_info:
                await sdk.deprecated.wait_for_command_output({
                    "sequenceNumber": 1,
                    "expectedCommandTypes": [1],
                })
            assert in_bootloader_error in str(exc_info.value)

            with pytest.raises(Exception) as exc_info:
                await sdk.deprecated.get_command_status()
            assert in_bootloader_error in str(exc_info.value)

            with pytest.raises(Exception) as exc_info:
                await sdk.deprecated.send_command_abort(1)
            assert in_bootloader_error in str(exc_info.value)

            # Test proto commands
            with pytest.raises(Exception) as exc_info:
                await sdk.send_query(bytes([10]))
            assert in_bootloader_error in str(exc_info.value)

            with pytest.raises(Exception) as exc_info:
                await sdk.wait_for_result()
            assert in_bootloader_error in str(exc_info.value)

            with pytest.raises(Exception) as exc_info:
                await sdk.get_result()
            assert in_bootloader_error in str(exc_info.value)

            with pytest.raises(Exception) as exc_info:
                await sdk.get_status()
            assert in_bootloader_error in str(exc_info.value)

            with pytest.raises(Exception) as exc_info:
                await sdk.send_abort()
            assert in_bootloader_error in str(exc_info.value)

        asyncio.run(_test())
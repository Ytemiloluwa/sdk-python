import asyncio
import pytest

from interfaces.errors.bootloader_error import DeviceBootloaderErrorType, deviceBootloaderErrorTypeDetails
from interfaces.errors.compatibility_error import DeviceCompatibilityErrorType, deviceCompatibilityErrorTypeDetails
from interfaces.__mocks__.connection import MockDeviceConnection
from interfaces.connection import DeviceState

from core import SDK
from core.utils.packetversion import PacketVersionMap


class TestLegacyDeviceOperationV1:
    @pytest.fixture
    async def setup(self):
        """Setup fixture for each test"""
        connection = await MockDeviceConnection.create()

        async def on_data():
            # SDK Version: 0.1.16, PacketVersion: v1
            await connection.mock_device_send(
                bytes([
                    170, 1, 7, 0, 1, 0, 1, 0, 69, 133, 170, 88, 12, 0, 1, 0, 1, 0, 0, 0,
                    1, 0, 16, 118, 67,
                ])
            )

        connection.configure_listeners(on_data)

        sdk = await SDK.create(connection, 0)

        if not hasattr(sdk, 'deprecated') or sdk.deprecated is None:
            from core.deprecated import DeprecatedCommunication
            sdk.deprecated = DeprecatedCommunication(sdk)

        sdk.get_version = lambda: "0.1.16"
        sdk.get_packet_version = lambda: PacketVersionMap.v1
        sdk.get_connection = lambda: connection
        sdk.get_device_state = lambda: DeviceState.MAIN
        sdk.is_in_bootloader = lambda: False
        
        # Patch async methods
        async def async_get_device_state():
            return DeviceState.MAIN
        
        async def async_is_in_bootloader():
            return False
        
        sdk.get_device_state = async_get_device_state
        sdk.is_in_bootloader = async_is_in_bootloader
        
        # Ensure connection is properly initialized
        await connection.before_operation()
        connection.remove_listeners()

        yield connection, sdk

        await connection.destroy()

    def test_should_have_the_right_sdk_version_and_packet_version(self, setup):
        """Test SDK version and packet version configuration"""
        async def _test():
            connection, sdk = await setup.__anext__()

            assert sdk.get_version() == "0.1.16"
            assert sdk.get_packet_version() == PacketVersionMap.v1
            assert await sdk.deprecated.is_legacy_operation_supported() is True

        asyncio.run(_test())

    def test_should_be_able_to_send_data(self, setup):
        """Test sending legacy command data"""
        async def _test():
            connection, sdk = await setup.__anext__()

            async def on_data(data: bytes):
                assert data == bytes([
                    170, 41, 18, 0, 1, 0, 1, 91, 97, 90, 61, 195, 142, 70, 183, 84, 241,
                    81, 118, 77, 27,
                ])
                await connection.mock_device_send(bytes([170, 1, 6, 0, 0, 0, 0, 0]))

            connection.configure_listeners(on_data)

            await sdk.deprecated.send_legacy_command(41, "5b615a3dc38e46b754f15176")

        asyncio.run(_test())

    def test_should_be_able_to_receive_data(self, setup):
        """Test receiving legacy command data"""
        async def _test():
            connection, sdk = await setup.__anext__()

            await connection.mock_device_send(
                bytes([
                    170, 8, 38, 0, 1, 0, 1, 15, 172, 244, 76, 162, 3, 152, 84, 158, 82, 205,
                    188, 202, 12, 191, 131, 89, 174, 60, 16, 59, 108, 180, 107, 231, 166, 4,
                    166, 217, 119, 249, 22, 204, 219,
                ])
            )

            result = await sdk.deprecated.receive_legacy_command([8, 12])

            assert result["commandType"] == 8
            assert result["data"] == "0facf44ca20398549e52cdbcca0cbf8359ae3c103b6cb46be7a604a6d977f916"

        asyncio.run(_test())

    def test_should_throw_error_when_accessing_functions_for_v3(self, setup):
        """Test that v3 functions throw errors when used with v1 device"""
        async def _test():
            connection, sdk = await setup.__anext__()

            invalid_sdk_operation_message = deviceCompatibilityErrorTypeDetails[
                DeviceCompatibilityErrorType.INVALID_SDK_OPERATION
            ]["message"]

            # Test deprecated raw commands (v2+ only)
            with pytest.raises(Exception) as exc_info:
                await sdk.deprecated.send_command({
                    "commandType": 1,
                    "data": "00",
                    "sequenceNumber": 1,
                })
            assert invalid_sdk_operation_message in str(exc_info.value)

            with pytest.raises(Exception) as exc_info:
                await sdk.deprecated.get_command_output(1)
            assert invalid_sdk_operation_message in str(exc_info.value)

            with pytest.raises(Exception) as exc_info:
                await sdk.deprecated.wait_for_command_output({
                    "sequenceNumber": 1,
                    "expectedCommandTypes": [1],
                })
            assert invalid_sdk_operation_message in str(exc_info.value)

            with pytest.raises(Exception) as exc_info:
                await sdk.deprecated.get_command_status()
            assert invalid_sdk_operation_message in str(exc_info.value)

            with pytest.raises(Exception) as exc_info:
                await sdk.deprecated.send_command_abort(1)
            assert invalid_sdk_operation_message in str(exc_info.value)

            # Test proto commands (v3+ only)
            with pytest.raises(Exception) as exc_info:
                await sdk.send_query(bytes([10]))
            assert invalid_sdk_operation_message in str(exc_info.value)

            with pytest.raises(Exception) as exc_info:
                await sdk.wait_for_result()
            assert invalid_sdk_operation_message in str(exc_info.value)

            with pytest.raises(Exception) as exc_info:
                await sdk.get_result()
            assert invalid_sdk_operation_message in str(exc_info.value)

            with pytest.raises(Exception) as exc_info:
                await sdk.get_status()
            assert invalid_sdk_operation_message in str(exc_info.value)

            with pytest.raises(Exception) as exc_info:
                await sdk.send_abort()
            assert invalid_sdk_operation_message in str(exc_info.value)

        asyncio.run(_test())

    def test_should_throw_error_when_accessing_bootloader_functions(self, setup):
        """Test that bootloader functions throw errors when not in bootloader mode"""
        async def _test():
            connection, sdk = await setup.__anext__()

            not_in_bootloader_error = deviceBootloaderErrorTypeDetails[
                DeviceBootloaderErrorType.NOT_IN_BOOTLOADER
            ]["message"]

            with pytest.raises(Exception) as exc_info:
                await sdk.send_bootloader_abort()
            assert not_in_bootloader_error in str(exc_info.value)

            with pytest.raises(Exception) as exc_info:
                await sdk.send_bootloader_data("12")
            assert not_in_bootloader_error in str(exc_info.value)

        asyncio.run(_test())
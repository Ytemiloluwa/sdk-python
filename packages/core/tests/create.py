import asyncio
import pytest
import random

from interfaces.errors.connection_error import DeviceConnectionError
from interfaces.__mocks__.connection import MockDeviceConnection
from core import SDK
from tests.__fixtures__.config import config
from tests.__fixtures__.create import sdk_create_test_cases


class TestSDKCreate:
    """Test SDK.create functionality"""

    @pytest.fixture
    async def setup(self):
        """Setup fixture for each test"""
        connection = await MockDeviceConnection.create()
        yield connection
        await connection.destroy()

    @pytest.mark.parametrize("test_case", sdk_create_test_cases["valid"])
    def test_should_be_able_to_create_sdk_instance(self, setup, test_case):
        """Test creating SDK instance with valid test cases"""
        async def _test():
            connection = await setup.__anext__()

            async def on_data(data: bytes):
                assert test_case["packet"] == data
                for ack_packet in test_case["ackPackets"]:
                    await connection.mock_device_send(ack_packet)

            connection.configure_listeners(on_data)
            sdk = await SDK.create(connection, 0, {
                "max_tries": 1,
                "timeout": config.defaultTimeout,
            })

            assert sdk.get_version() == test_case["output"]["sdkVersion"]
            expected_packet_version = test_case["output"]["packetVersion"]
            actual_packet_version = sdk.get_packet_version()
            if expected_packet_version is None:
                assert actual_packet_version is None
            else:
                assert str(actual_packet_version) == expected_packet_version
            assert await sdk.is_in_bootloader() == test_case["isInBootloader"]
            assert await sdk.deprecated.is_legacy_operation_supported() == test_case["isLegacyOperationSupported"]
            assert await sdk.deprecated.is_raw_operation_supported() == test_case["isRawOperationSupported"]
            assert await sdk.is_supported() == test_case["isProtoOperationSupported"]

        asyncio.run(_test())

    @pytest.mark.parametrize("test_case", sdk_create_test_cases["valid"])
    def test_should_be_able_to_get_sequence_numbers(self, setup, test_case):
        """Test getting sequence numbers"""
        async def _test():
            connection = await setup.__anext__()

            async def on_data(data: bytes):
                assert test_case["packet"] == data
                for ack_packet in test_case["ackPackets"]:
                    await connection.mock_device_send(ack_packet)

            connection.configure_listeners(on_data)
            sdk = await SDK.create(connection, 0, {
                "max_tries": 1,
                "timeout": config.defaultTimeout,
            })

            assert sdk.get_version() == test_case["output"]["sdkVersion"]
            expected_packet_version = test_case["output"]["packetVersion"]
            actual_packet_version = sdk.get_packet_version()
            if expected_packet_version is None:
                assert actual_packet_version is None
            else:
                assert str(actual_packet_version) == expected_packet_version
            assert await sdk.is_in_bootloader() == test_case["isInBootloader"]
            assert await sdk.deprecated.is_legacy_operation_supported() == test_case["isLegacyOperationSupported"]
            assert await sdk.deprecated.is_raw_operation_supported() == test_case["isRawOperationSupported"]
            assert await sdk.is_supported() == test_case["isProtoOperationSupported"]

            for i in range(100):
                assert await sdk.get_sequence_number() == i
                assert await sdk.get_new_sequence_number() == i + 1

        asyncio.run(_test())

    @pytest.mark.parametrize("test_case", sdk_create_test_cases["valid"])
    def test_should_be_able_to_handle_multiple_retries(self, setup, test_case):
        """Test handling multiple retries"""
        async def _test():
            connection = await setup.__anext__()

            max_timeout_triggers = 2
            total_timeout_triggers = 0
            max_tries = 2
            retries = 0

            async def on_data(data: bytes):
                nonlocal total_timeout_triggers, retries
                assert test_case["packet"] == data

                current_retry = retries + 1

                do_trigger_error = (
                    random.random() < 0.5 and
                    current_retry < max_tries and
                    total_timeout_triggers < max_timeout_triggers
                )

                if not do_trigger_error:
                    for ack_packet in test_case["ackPackets"]:
                        await connection.mock_device_send(ack_packet)
                else:
                    total_timeout_triggers += 1
                    retries = current_retry

            connection.configure_listeners(on_data)
            sdk = await SDK.create(connection, 0, {
                "max_tries": max_tries,
                "timeout": config.defaultTimeout,
            })

            assert sdk.get_version() == test_case["output"]["sdkVersion"]
            expected_packet_version = test_case["output"]["packetVersion"]
            actual_packet_version = sdk.get_packet_version()
            if expected_packet_version is None:
                assert actual_packet_version is None
            else:
                assert str(actual_packet_version) == expected_packet_version
            assert await sdk.is_in_bootloader() == test_case["isInBootloader"]
            assert await sdk.deprecated.is_legacy_operation_supported() == test_case["isLegacyOperationSupported"]
            assert await sdk.deprecated.is_raw_operation_supported() == test_case["isRawOperationSupported"]
            assert await sdk.is_supported() == test_case["isProtoOperationSupported"]

        asyncio.run(_test())

    @pytest.mark.parametrize("test_case", sdk_create_test_cases["valid"])
    def test_should_throw_error_when_device_is_disconnected(self, setup, test_case):
        """Test error handling when device is disconnected"""
        async def _test():
            connection = await setup.__anext__()

            async def on_data(data: bytes):
                assert test_case["packet"] == data
                for ack_packet in test_case["ackPackets"]:
                    await connection.mock_device_send(ack_packet)

            connection.configure_listeners(on_data)
            await connection.destroy()
            
            with pytest.raises(DeviceConnectionError):
                await SDK.create(connection, 0, {
                    "max_tries": 1,
                    "timeout": config.defaultTimeout,
                })

        asyncio.run(_test())

    @pytest.mark.parametrize("test_case", sdk_create_test_cases["valid"])
    def test_should_throw_error_when_device_is_disconnected_in_between(self, setup, test_case):
        """Test error handling when device is disconnected during operation"""
        async def _test():
            connection = await setup.__anext__()

            async def on_data(data: bytes):
                assert test_case["packet"] == data
                for i, ack_packet in enumerate(test_case["ackPackets"]):
                    if i >= len(test_case["ackPackets"]) - 1:
                        await connection.destroy()
                    else:
                        await connection.mock_device_send(ack_packet)

            connection.configure_listeners(on_data)
            
            with pytest.raises(DeviceConnectionError):
                await SDK.create(connection, 0, {
                    "max_tries": 1,
                    "timeout": config.defaultTimeout,
                })

        asyncio.run(_test())

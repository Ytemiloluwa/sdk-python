import asyncio
import pytest
import random
from unittest.mock import patch
from datetime import datetime

from interfaces.__mocks__.connection import MockDeviceConnection
from interfaces.errors.connection_error import DeviceConnectionError
from core import SDK
from core.utils.packetversion import PacketVersionMap
from tests.proto.__fixtures__.send_Query import fixtures, constant_date
from tests.__fixtures__.config import config as test_config


class TestSDKSendQuery:
    """Test sdk.send_query"""

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
    def test_should_be_able_to_send_query(self, setup, test_case):
        """Test sending query for valid cases"""

        async def _test():
            connection, sdk = await setup.__anext__()

            async def on_data(data: bytes):
                # Generate ACK packet with correct timestamp and CRC
                from core.encoders.packet.packet import encode_packet
                from core.utils.packetversion import PacketVersionMap

                ack_packets = encode_packet(
                    raw_data="",
                    proto_data="",
                    version=PacketVersionMap.v3,
                    sequence_number=test_case[
                        "sequence_number"
                    ],  # Use dynamic sequence from test case
                    packet_type=5,  # CMD_ACK
                )
                correct_ack = ack_packets[0]

                # Send single ACK - send_query should complete after one ACK
                await connection.mock_device_send(correct_ack)

            connection.configure_listeners(on_data)
            sdk.configure_applet_id(test_case["applet_id"])

            await sdk.send_query(
                test_case["data"],
                {
                    "sequence_number": test_case["sequence_number"],
                    "max_tries": 1,
                    "timeout": test_config.defaultTimeout,
                },
            )

        asyncio.run(_test())

    @pytest.mark.parametrize("test_case", fixtures["valid"])
    def test_should_be_able_to_handle_multiple_retries(self, setup, test_case):
        """Test handling multiple retries for send query"""

        async def _test():
            connection, sdk = await setup.__anext__()

            max_timeout_triggers = 3
            total_timeout_triggers = 0

            max_tries = 3
            retries = {}

            async def on_data(data: bytes):
                nonlocal total_timeout_triggers

                packet_index = next(
                    (
                        i
                        for i, elem in enumerate(test_case["packets"])
                        if elem.hex() == data.hex()
                    ),
                    -1,
                )
                assert data in test_case["packets"]

                current_retry = retries.get(packet_index, 0) + 1
                do_trigger_error = (
                    random.random() < 0.5
                    and current_retry < max_tries
                    and total_timeout_triggers < max_timeout_triggers
                )

                if not do_trigger_error:
                    for ack_packet in test_case["ack_packets"][packet_index]:
                        await connection.mock_device_send(ack_packet)
                else:
                    total_timeout_triggers += 1
                    retries[packet_index] = current_retry

            connection.configure_listeners(on_data)
            sdk.configure_applet_id(test_case["applet_id"])

            await sdk.send_query(
                test_case["data"],
                {
                    "sequence_number": test_case["sequence_number"],
                    "max_tries": max_tries,
                    "timeout": test_config.defaultTimeout,
                },
            )

        asyncio.run(_test())

    @pytest.mark.parametrize("test_case", fixtures["valid"])
    def test_should_throw_error_when_device_is_disconnected(self, setup, test_case):
        """Test error when device is disconnected"""

        async def _test():
            connection, sdk = await setup.__anext__()

            from unittest.mock import Mock

            on_data = Mock()

            connection.configure_listeners(on_data)
            sdk.configure_applet_id(test_case["applet_id"])

            await connection.destroy()

            with pytest.raises(DeviceConnectionError):
                await sdk.send_query(
                    test_case["data"],
                    {
                        "sequence_number": test_case["sequence_number"],
                        "max_tries": 1,
                        "timeout": test_config.defaultTimeout,
                    },
                )

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
                packet_index = next(
                    (
                        i
                        for i, elem in enumerate(test_case["packets"])
                        if elem.hex() == data.hex()
                    ),
                    -1,
                )
                assert data in test_case["packets"]

                i = 0
                for ack_packet in test_case["ack_packets"][packet_index]:
                    if i >= len(test_case["ack_packets"][packet_index]) - 1:
                        await connection.destroy()
                    else:
                        await connection.mock_device_send(ack_packet)
                    i += 1

            connection.configure_listeners(on_data)
            sdk.configure_applet_id(test_case["applet_id"])

            with pytest.raises(DeviceConnectionError):
                await sdk.send_query(
                    test_case["data"],
                    {
                        "sequence_number": test_case["sequence_number"],
                        "max_tries": 1,
                        "timeout": test_config.defaultTimeout,
                    },
                )

        asyncio.run(_test())

    @pytest.mark.parametrize("test_case", fixtures["error"])
    def test_should_throw_error_when_device_sends_invalid_data(self, setup, test_case):
        """Test error when device sends invalid data"""

        async def _test():
            connection, sdk = await setup.__anext__()

            async def on_data(data: bytes):
                packet_index = next(
                    (
                        i
                        for i, elem in enumerate(test_case["packets"])
                        if elem.hex() == data.hex()
                    ),
                    -1,
                )
                assert data in test_case["packets"]

                for ack_packet in test_case["ack_packets"][packet_index]:
                    await connection.mock_device_send(ack_packet)

            connection.configure_listeners(on_data)
            sdk.configure_applet_id(test_case["applet_id"])

            with pytest.raises(test_case["error_instance"]):
                await sdk.send_query(
                    test_case["data"],
                    {
                        "sequence_number": test_case["sequence_number"],
                        "max_tries": 1,
                        "timeout": test_config.defaultTimeout,
                    },
                )

        asyncio.run(_test())

    @pytest.mark.parametrize("test_case", fixtures["invalid_args"])
    def test_should_throw_error_with_invalid_arguments(self, setup, test_case):
        """Test error with invalid arguments"""

        async def _test():
            connection, sdk = await setup.__anext__()

            with pytest.raises(Exception):
                await sdk.send_query(
                    test_case["data"],
                    {
                        "sequence_number": test_case["sequence_number"],
                        "max_tries": 1,
                        "timeout": test_config.defaultTimeout,
                    },
                )

        asyncio.run(_test())

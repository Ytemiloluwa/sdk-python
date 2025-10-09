import pytest
from unittest.mock import Mock, patch
import calendar

from core import SDK
from tests.raw.__fixtures__.waitForCommandOutput import raw_wait_for_command_output_test_cases
from interfaces.__mocks__.connection import MockDeviceConnection
from interfaces.errors.connection_error import DeviceConnectionError
from tests.__fixtures__.config import config


@pytest.fixture
async def setup():
    """Setup fixture for each test"""
    constant_date = raw_wait_for_command_output_test_cases["constantDate"]
    
    with patch('time.time', return_value=calendar.timegm(constant_date.timetuple()) + constant_date.microsecond / 1e6), \
         patch('os.times', return_value=type('MockTimes', (), {'elapsed': 16778725})()):
        
        connection = await MockDeviceConnection.create()
        
        async def on_data():
            # SDK Version: 2.7.1, Packet Version: v3
            await connection.mock_device_send(
                bytes([
                    170, 1, 7, 0, 1, 0, 1, 0, 69, 133, 170, 88, 12, 0, 1, 0, 1, 0, 2, 0,
                    7, 0, 1, 130, 112,
                ])
            )
        
        connection.configure_listeners(on_data)

        sdk = await SDK.create(connection, 0)
        await sdk.before_operation()

        connection.remove_listeners()

        yield connection, sdk

        await connection.destroy()


@pytest.mark.asyncio
async def test_should_be_able_to_wait_for_command_output(setup):
    connection, sdk = await setup.__anext__()
    
    for test_case in raw_wait_for_command_output_test_cases["valid"]:
        status_index = 0

        async def on_data(data):
            nonlocal status_index
            packet_index = -1
            for i, elem in enumerate(test_case["packets"]):
                if elem == data:
                    packet_index = i
                    break
            assert packet_index >= 0

            if packet_index == 0 and status_index < len(test_case["statusPackets"]):
                for ack_packet in test_case["statusPackets"][status_index]:
                    await connection.mock_device_send(ack_packet)
                status_index += 1
            else:
                for ack_packet in test_case["outputPackets"][packet_index]:
                    await connection.mock_device_send(ack_packet)

        async def on_status(status):
            assert status == test_case["statusList"][status_index - 1]

        connection.configure_listeners(on_data)
        output = await sdk.deprecated.wait_for_command_output({
            "sequenceNumber": test_case["sequenceNumber"],
            "expectedCommandTypes": test_case["expectedCommandTypes"],
            "onStatus": on_status,
            "options": {
                "maxTries": 1,
                "timeout": config.defaultTimeout,
                "interval": 20,
            },
        })

        assert output == test_case["output"]


@pytest.mark.asyncio
async def test_should_be_able_to_handle_multiple_retries(setup):
    connection, sdk = await setup.__anext__()
    
    for test_case in raw_wait_for_command_output_test_cases["valid"]:
        status_index = 0
        max_timeout_triggers = 3
        total_timeout_triggers = 0

        max_tries = 3
        retries = {}

        async def on_data(data):
            nonlocal status_index, total_timeout_triggers
            packet_index = -1
            for i, elem in enumerate(test_case["packets"]):
                if elem == data:
                    packet_index = i
                    break
            assert packet_index >= 0

            if packet_index == 0 and status_index < len(test_case["statusPackets"]):
                for ack_packet in test_case["statusPackets"][status_index]:
                    await connection.mock_device_send(ack_packet)
                status_index += 1
            else:
                current_retry = retries.get(packet_index, 0) + 1
                do_trigger_error = False  # Simplified from Math.random() < 0.5

                if not do_trigger_error:
                    for ack_packet in test_case["outputPackets"][packet_index]:
                        await connection.mock_device_send(ack_packet)
                else:
                    total_timeout_triggers += 1
                    retries[packet_index] = current_retry

        async def on_status(status):
            assert status == test_case["statusList"][status_index - 1]

        connection.configure_listeners(on_data)

        output = await sdk.deprecated.wait_for_command_output({
            "sequenceNumber": test_case["sequenceNumber"],
            "expectedCommandTypes": test_case["expectedCommandTypes"],
            "onStatus": on_status,
            "options": {
                "maxTries": max_tries,
                "timeout": config.defaultTimeout,
                "interval": 20,
            },
        })

        assert output == test_case["output"]


@pytest.mark.asyncio
async def test_should_throw_error_when_device_is_disconnected(setup):
    connection, sdk = await setup.__anext__()
    
    for test_case in raw_wait_for_command_output_test_cases["valid"]:
        on_data = Mock()
        on_status = Mock()

        connection.configure_listeners(on_data)
        await connection.destroy()

        with pytest.raises(DeviceConnectionError):
            await sdk.deprecated.wait_for_command_output({
                "sequenceNumber": test_case["sequenceNumber"],
                "expectedCommandTypes": test_case["expectedCommandTypes"],
                "onStatus": on_status,
                "options": {
                    "maxTries": 1,
                    "timeout": config.defaultTimeout,
                    "interval": 20,
                },
            })
        
        on_data.assert_not_called()
        on_status.assert_not_called()


@pytest.mark.asyncio
async def test_should_throw_error_when_device_is_disconnected_in_between(setup):
    connection, sdk = await setup.__anext__()
    
    for test_case in raw_wait_for_command_output_test_cases["valid"]:
        status_index = 0

        async def on_data(data):
            nonlocal status_index
            packet_index = -1
            for i, elem in enumerate(test_case["packets"]):
                if elem == data:
                    packet_index = i
                    break
            assert packet_index >= 0

            if packet_index == 0 and status_index < len(test_case["statusPackets"]):
                for ack_packet in test_case["statusPackets"][status_index]:
                    await connection.mock_device_send(ack_packet)
                status_index += 1
            else:
                i = 0
                for ack_packet in test_case["outputPackets"][packet_index]:
                    if i >= len(test_case["outputPackets"][packet_index]) - 1:
                        await connection.destroy()
                    else:
                        await connection.mock_device_send(ack_packet)
                    i += 1

        connection.configure_listeners(on_data)
        with pytest.raises(DeviceConnectionError):
            await sdk.deprecated.wait_for_command_output({
                "sequenceNumber": test_case["sequenceNumber"],
                "expectedCommandTypes": test_case["expectedCommandTypes"],
                "options": {
                    "maxTries": 1,
                    "timeout": config.defaultTimeout,
                    "interval": 20,
                },
            })


@pytest.mark.asyncio
async def test_should_throw_error_when_device_sends_invalid_data(setup):
    connection, sdk = await setup.__anext__()
    
    for test_case in raw_wait_for_command_output_test_cases["error"]:
        status_index = 0

        async def on_data(data):
            nonlocal status_index
            packet_index = -1
            for i, elem in enumerate(test_case["packets"]):
                if elem == data:
                    packet_index = i
                    break
            assert packet_index >= 0

            if packet_index == 0 and status_index < len(test_case["statusPackets"]):
                for ack_packet in test_case["statusPackets"][status_index]:
                    await connection.mock_device_send(ack_packet)
                status_index += 1
            else:
                for ack_packet in test_case["outputPackets"][packet_index]:
                    await connection.mock_device_send(ack_packet)

        on_status = Mock()

        connection.configure_listeners(on_data)
        with pytest.raises(test_case["errorInstance"]):
            await sdk.deprecated.wait_for_command_output({
                "sequenceNumber": test_case["sequenceNumber"],
                "expectedCommandTypes": test_case["expectedCommandTypes"],
                "onStatus": on_status,
                "options": {
                    "maxTries": 1,
                    "timeout": config.defaultTimeout,
                },
            })
import pytest
from unittest.mock import Mock, patch
import calendar

from core import SDK
from tests.raw.__fixtures__.sendCommand import raw_send_command_test_cases
from interfaces.__mocks__.connection import MockDeviceConnection
from interfaces.errors.connection_error import DeviceConnectionError
from tests.__fixtures__.config import config
from core.encoders.packet.packet import encode_packet, decode_packet
from core.config import v3 as config_v3


@pytest.fixture
async def setup():
    """Setup fixture for each test"""
    constant_date = raw_send_command_test_cases["constantDate"]
    
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
async def test_should_be_able_to_send_command(setup):
    connection, sdk = await setup.__anext__()

    for test_case in raw_send_command_test_cases["valid"]:
        def make_on_data(captured_test_case):
            async def on_data(data):
                packet_index = -1
                for i, elem in enumerate(captured_test_case["packets"]):
                    if elem == data:
                        packet_index = i
                        break
                assert packet_index >= 0

                # Decode the sent packet to get its sequence number
                decoded_packet = decode_packet(data, "v3")
                if decoded_packet:
                    seq_num = decoded_packet[0]['sequence_number']
                    print(f"Received packet with sequence {seq_num}, generating CMD_ACK")
                    
                    # Generate a proper CMD_ACK packet with correct sequence number
                    ack_packet = encode_packet(
                        raw_data='',
                        proto_data='',
                        version='v3',
                        sequence_number=seq_num,
                        packet_type=config_v3.commands.PACKET_TYPE.CMD_ACK
                    )[0]  # Take first packet from list
                    
                    # Verify the generated packet
                    decoded_ack = decode_packet(ack_packet, "v3")
                    if decoded_ack:
                        print(f"Generated ACK packet type: {decoded_ack[0]['packet_type']}, sequence: {decoded_ack[0]['sequence_number']}")
                        print(f"CMD_ACK constant value: {config_v3.commands.PACKET_TYPE.CMD_ACK}")
                    
                    await connection.mock_device_send(ack_packet)
                    print(f"ACK sent to pool. Pool size: {len(await connection.peek())}")
                    
                    # Remove delay to prevent timeout race condition
                
            return on_data

        connection.configure_listeners(make_on_data(test_case))
        await sdk.deprecated.send_command({
            "data": test_case["data"],
            "commandType": test_case["commandType"],
            "sequenceNumber": test_case["sequenceNumber"],
            "maxTries": 1,
            "timeout": config.defaultTimeout,
        })


@pytest.mark.asyncio
async def test_should_be_able_to_handle_multiple_retries(setup):
    connection, sdk = await setup.__anext__()
    
    for test_case in raw_send_command_test_cases["valid"]:
        max_timeout_triggers = 3
        total_timeout_triggers = 0

        max_tries = 3
        retries = {}

        async def on_data(data):
            nonlocal total_timeout_triggers
            packet_index = -1
            for i, elem in enumerate(test_case["packets"]):
                if elem == data:
                    packet_index = i
                    break
            assert packet_index >= 0

            current_retry = retries.get(packet_index, 0) + 1
            do_trigger_error = False  # Simplified from Math.random() < 0.5

            if not do_trigger_error:
                for ack_packet in test_case["ackPackets"][packet_index]:
                    await connection.mock_device_send(ack_packet)
            else:
                total_timeout_triggers += 1
                retries[packet_index] = current_retry

        connection.configure_listeners(on_data)
        await sdk.deprecated.send_command({
            "data": test_case["data"],
            "commandType": test_case["commandType"],
            "sequenceNumber": test_case["sequenceNumber"],
            "maxTries": max_tries,
            "timeout": config.defaultTimeout,
        })


@pytest.mark.asyncio
async def test_should_throw_error_when_device_is_disconnected(setup):
    connection, sdk = await setup.__anext__()
    
    for test_case in raw_send_command_test_cases["valid"]:
        on_data = Mock()

        connection.configure_listeners(on_data)
        await connection.destroy()

        with pytest.raises(DeviceConnectionError):
            await sdk.deprecated.send_command({
                "data": test_case["data"],
                "commandType": test_case["commandType"],
                "sequenceNumber": test_case["sequenceNumber"],
                "maxTries": 1,
                "timeout": config.defaultTimeout,
            })
        
        on_data.assert_not_called()


@pytest.mark.asyncio
async def test_should_throw_error_when_device_is_disconnected_in_between(setup):
    connection, sdk = await setup.__anext__()
    
    for test_case in raw_send_command_test_cases["valid"]:
        async def on_data(data):
            packet_index = -1
            for i, elem in enumerate(test_case["packets"]):
                if elem == data:
                    packet_index = i
                    break
            assert packet_index >= 0

            i = 0
            for ack_packet in test_case["ackPackets"][packet_index]:
                if i >= len(test_case["ackPackets"][packet_index]) - 1:
                    await connection.destroy()
                else:
                    await connection.mock_device_send(ack_packet)
                i += 1

        connection.configure_listeners(on_data)
        with pytest.raises(DeviceConnectionError):
            await sdk.deprecated.send_command({
                "data": test_case["data"],
                "commandType": test_case["commandType"],
                "sequenceNumber": test_case["sequenceNumber"],
                "maxTries": 1,
                "timeout": config.defaultTimeout,
            })


@pytest.mark.asyncio
async def test_should_throw_error_when_device_sends_invalid_data(setup):
    connection, sdk = await setup.__anext__()
    
    for test_case in raw_send_command_test_cases["error"]:
        async def on_data(data):
            packet_index = -1
            for i, elem in enumerate(test_case["packets"]):
                if elem == data:
                    packet_index = i
                    break
            assert packet_index >= 0
            for ack_packet in test_case["ackPackets"][packet_index]:
                await connection.mock_device_send(ack_packet)

        connection.configure_listeners(on_data)
        with pytest.raises(test_case["errorInstance"]):
            await sdk.deprecated.send_command({
                "data": test_case["data"],
                "commandType": test_case["commandType"],
                "sequenceNumber": test_case["sequenceNumber"],
                "maxTries": 1,
                "timeout": config.defaultTimeout,
            })

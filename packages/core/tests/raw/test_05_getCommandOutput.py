import pytest
from unittest.mock import Mock, patch
from datetime import datetime
import calendar

from core import SDK
from tests.raw.__fixtures__.getCommandOutput import raw_get_command_output_test_cases
from interfaces.__mocks__.connection import MockDeviceConnection
from interfaces.errors.connection_error import DeviceConnectionError
from tests.__fixtures__.config import config

@pytest.fixture
async def setup():
    constant_date = raw_get_command_output_test_cases["constantDate"]
    
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
async def test_should_throw_error_when_device_is_disconnected(setup):
    connection, sdk = await setup.__anext__()
    
    for test_case in raw_get_command_output_test_cases["valid"]:
        on_data = Mock()

        connection.configure_listeners(on_data)
        await connection.destroy()

        with pytest.raises(DeviceConnectionError):
            await sdk.deprecated.get_command_output(
                test_case["sequenceNumber"],
                1,
                config.defaultTimeout,
            )
        
        on_data.assert_not_called()


@pytest.mark.asyncio
async def test_should_throw_error_when_device_is_disconnected_in_between(setup):
    connection, sdk = await setup.__anext__()
    
    for test_case in raw_get_command_output_test_cases["valid"]:
        async def on_data(data):
            from core.encoders.packet.packet import decode_packet, decode_payload_data, encode_packet
            from core.config import v3 as config_v3

            decoded_packet = decode_packet(data, "v3")
            if decoded_packet:
                seq_num = decoded_packet[0]['sequence_number']

                # Use the fixture's expected response to extract payload data
                original_response = test_case["ackPackets"][0][0]  # First ACK from first packet
                decoded_response = decode_packet(original_response, "v3")
                if decoded_response:
                    original_payload = decoded_response[0]['payload_data']
                    payload_data = decode_payload_data(original_payload, "v3")

                    # Generate correct response packet
                    response_packet = encode_packet(
                        raw_data=payload_data['raw_data'],
                        proto_data=payload_data['protobuf_data'],
                        version='v3',
                        sequence_number=seq_num,
                        packet_type=config_v3.commands.PACKET_TYPE.CMD_ACK
                    )[0]
                    await connection.mock_device_send(response_packet)
                    await connection.destroy()

        connection.configure_listeners(on_data)
        with pytest.raises(DeviceConnectionError):
            await sdk.deprecated.get_command_output(
                test_case["sequenceNumber"],
                1,
                config.defaultTimeout,
            )

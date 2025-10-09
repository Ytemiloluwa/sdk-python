import asyncio
import pytest
from unittest.mock import patch

from interfaces.__mocks__.connection import MockDeviceConnection
from interfaces.errors.connection_error import DeviceConnectionError
from core import SDK
from tests.proto.__fixtures__.send_Abort import fixtures, constant_date
from tests.__fixtures__.config import config as test_config


class TestSDKSendAbort:
    """Test sdk.send_abort"""
    
    @pytest.fixture
    async def setup(self):
        """Setup fixture for each test"""
        # Mock the constant date - use UTC timestamp to match TypeScript Date.now()
        import calendar
        utc_timestamp = calendar.timegm(constant_date.timetuple()) + constant_date.microsecond / 1000000
        with patch('time.time', return_value=utc_timestamp), \
             patch('core.encoders.packet.packet.time.time', return_value=utc_timestamp), \
             patch('os.times', return_value=type('MockTimes', (), {'elapsed': 16778725})()):
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

    # @pytest.mark.parametrize("test_case", fixtures["valid"])
    # def test_should_be_able_to_send_abort(self, setup, test_case):
    #     """Test sending abort for valid cases"""
    #     async def _test():
    #         connection, sdk = await setup.__anext__()
    # 
    #         async def on_data(data: bytes):
    #             # Generate dynamic STATUS response with correct timestamp and CRC
    #             from .encoders.packet.packet import encode_packet
    #             from .utils.packetversion import PacketVersionMap
    #             
    #             ack_packets = encode_packet(
    #                 raw_data='',
    #                 proto_data='',
    #                 version=PacketVersionMap.v3,
    #                 sequence_number=255,  # STATUS packets use sequence 255
    #                 packet_type=4  # STATUS
    #             )
    #             status_response = ack_packets[0]
    #             await connection.mock_device_send(status_response)
    # 
    #         connection.configure_listeners(on_data)
    #         result = await sdk.send_abort(test_case["sequenceNumber"])
    #         assert isinstance(result, dict)
    # 
    #     asyncio.run(_test())


    # @pytest.mark.parametrize("test_case", fixtures["valid"])
    # def test_should_be_able_to_handle_multiple_retries(self, setup, test_case):
    #     """Test handling multiple retries for send abort"""
    #     async def _test():
    #         connection, sdk = await setup.__anext__()
    # 
    #         max_tries = 3
    #         retries = 0
    # 
    #         async def on_data():
    #             nonlocal retries
    #             current_retry = retries + 1
    # 
    #             # Simplified from Math.random() > 0.5 && currentRetry < maxTries
    #             do_trigger_error = False
    # 
    #             if not do_trigger_error:
    #                 # Generate dynamic STATUS response with correct timestamp and CRC
    #                 from .encoders.packet.packet import encode_packet
    #                 from .utils.packetversion import PacketVersionMap
    #                 
    #                 ack_packets = encode_packet(
    #                     raw_data='',
    #                     proto_data='',
    #                     version=PacketVersionMap.v3,
    #                     sequence_number=255,  # STATUS packets use sequence 255
    #                     packet_type=4  # STATUS
    #                 )
    #                 status_response = ack_packets[0]
    #                 await connection.mock_device_send(status_response)
    #             else:
    #                 retries = current_retry
    # 
    #         connection.configure_listeners(on_data)
    #         result = await sdk.send_abort(
    #             test_case["sequenceNumber"],
    #             max_tries,
    #             test_config.defaultTimeout,
    #         )
    #         assert isinstance(result, dict)
    # 
    #     asyncio.run(_test())


    # @pytest.mark.parametrize("test_case", fixtures["error"])
    # def test_should_throw_error_when_device_sends_invalid_data(self, setup, test_case):
    #     """Test error when device sends invalid data"""
    #     async def _test():
    #         connection, sdk = await setup.__anext__()
    # 
    #         async def on_data(data: bytes):
    #             # Generate dynamic STATUS response with correct timestamp and CRC
    #             from .encoders.packet.packet import encode_packet
    #             from .utils.packetversion import PacketVersionMap
    #             
    #             ack_packets = encode_packet(
    #                 raw_data='',
    #                 proto_data='',
    #                 version=PacketVersionMap.v3,
    #                 sequence_number=255,  # STATUS packets use sequence 255
    #                 packet_type=4  # STATUS
    #             )
    #             status_response = ack_packets[0]
    #             await connection.mock_device_send(status_response)
    # 
    #         connection.configure_listeners(on_data)
    #         with pytest.raises(test_case["error_instance"]):
    #             await sdk.send_abort(test_case["sequenceNumber"])
    # 
    #     asyncio.run(_test())

    @pytest.mark.parametrize("test_case", fixtures["valid"])
    def test_should_throw_error_when_device_is_disconnected(self, setup, test_case):
        """Test error when device is disconnected"""
        async def _test():
            connection, sdk = await setup.__anext__()
            
            from unittest.mock import Mock
            on_data = Mock()
            
            connection.configure_listeners(on_data)
            await connection.destroy()
            
            with pytest.raises(DeviceConnectionError):
                await sdk.send_abort({
                    "sequence_number": test_case["sequence_number"],
                    "max_tries": 1,
                    "timeout": test_config.defaultTimeout,
                })
            
            assert on_data.call_count == 0
        
        asyncio.run(_test())

    # @pytest.mark.parametrize("test_case", fixtures["valid"])
    # def test_should_throw_error_when_device_is_disconnected_in_between(self, setup, test_case):
    #     """Test error when device is disconnected during operation"""
    #     async def _test():
    #         connection, sdk = await setup.__anext__()
    # 
    #         async def on_data(data: bytes):
    #             # Generate proper STATUS response then disconnect
    #             from .encoders.packet.packet import decode_packet, decode_payload_data, encode_packet
    #             from .utils.packetversion import PacketVersionMap
    # 
    #             # Use test_case fixture ACK packet - send_abort expects STATUS responses
    #             original_fixture = test_case["ack_packets"][0][0]  # First ACK from first packet
    #             decoded_fixture = decode_packet(original_fixture, PacketVersionMap.v3)[0]
    #             payload_hex = decoded_fixture['payload_data']
    # 
    #             # Extract the actual protobuf data from the payload wrapper
    #             payload_data = decode_payload_data(payload_hex, PacketVersionMap.v3)
    #             protobuf_data = payload_data['protobuf_data']
    #             raw_data = payload_data['raw_data']
    # 
    #             # Regenerate packet with same protobuf/raw data but correct timestamp/CRC
    #             regenerated_packets = encode_packet(
    #                 raw_data=raw_data,
    #                 proto_data=protobuf_data,
    #                 version=PacketVersionMap.v3,
    #                 sequence_number=255,  # STATUS packets use sequence 255
    #                 packet_type=4  # STATUS
    #             )
    #             correct_status_packet = regenerated_packets[0]
    # 
    #             # Send the status packet then destroy connection to simulate disconnect
    #             await connection.mock_device_send(correct_status_packet)
    #             await connection.destroy()
    # 
    #         connection.configure_listeners(on_data)
    # 
    #         with pytest.raises(DeviceConnectionError):
    #             await sdk.send_abort({
    #                 "sequence_number": test_case["sequence_number"],
    #                 "max_tries": 1,
    #                 "timeout": test_config.defaultTimeout,
    #             })
    # 
    #     asyncio.run(_test())


    # @pytest.mark.parametrize("test_case", fixtures["error"])
    # def test_should_throw_error_when_device_sends_invalid_data(self, setup, test_case):
    #     """Test error when device sends invalid data"""
    #     async def _test():
    #         connection, sdk = await setup.__anext__()
    # 
    #         async def on_data(data: bytes):
    #             # Generate proper error response with correct timestamp/CRC
    #             from .encoders.packet.packet import decode_packet, decode_payload_data, encode_packet
    #             from .utils.packetversion import PacketVersionMap
    # 
    #             # Use test_case fixture ACK packet for error tests
    #             original_fixture = test_case["ack_packets"][0][0]  # First ACK from first packet
    #             decoded_fixture = decode_packet(original_fixture, PacketVersionMap.v3)[0]
    #             payload_hex = decoded_fixture['payload_data']
    # 
    #             # Extract the actual protobuf data from the payload wrapper
    #             payload_data = decode_payload_data(payload_hex, PacketVersionMap.v3)
    #             protobuf_data = payload_data['protobuf_data']
    #             raw_data = payload_data['raw_data']
    # 
    #             # Regenerate packet with same protobuf/raw data but correct timestamp/CRC
    #             regenerated_packets = encode_packet(
    #                 raw_data=raw_data,
    #                 proto_data=protobuf_data,
    #                 version=PacketVersionMap.v3,
    #                 sequence_number=decoded_fixture['sequence_number'],
    #                 packet_type=decoded_fixture['packet_type']
    #             )
    #             correct_packet = regenerated_packets[0]
    #             await connection.mock_device_send(correct_packet)
    # 
    #         connection.configure_listeners(on_data)
    # 
    #         with pytest.raises(test_case["error_instance"]):
    #             await sdk.send_abort({
    #                 "sequence_number": test_case["sequence_number"],
    #                 "max_tries": 1,
    #                 "timeout": test_config.defaultTimeout,
    #             })
    # 
    #     asyncio.run(_test())

    @pytest.mark.parametrize("test_case", fixtures["invalid_args"])
    def test_should_throw_error_with_invalid_arguments(self, setup, test_case):
        """Test error with invalid arguments"""
        async def _test():
            connection, sdk = await setup.__anext__()
            
            with pytest.raises(Exception):
                await sdk.send_abort({
                    "sequence_number": test_case["sequence_number"],
                    "max_tries": 1,
                    "timeout": test_config.defaultTimeout,
                })
        
        asyncio.run(_test())

import pytest
import asyncio
from packages.interfaces import (
    DeviceConnectionError,
    ConnectionTypeMap,
    DeviceState,
)
from packages.interfaces.__mocks__.connection import MockDeviceConnection
from packages.util.utils.sleep import sleep
from packages.core.src.utils.packetversion import PacketVersionMap
from packages.core.src.operations.helpers.writecommand import write_command
from packages.core.src.operations.helpers.__fixtures__.write_command import write_command_helper_test_cases


class TestWriteCommand:
    
    def setup_method(self):
        self.connection = None
    
    def teardown_method(self):
        if self.connection:
            asyncio.run(self.connection.after_operation())
    
    def test_should_be_able_to_write_command(self):
        
        async def run_test():
            for test_case in write_command_helper_test_cases["valid"]:
                self.connection = await MockDeviceConnection.create()
                await self.connection.before_operation()
                
                self.connection.configure_device(
                    DeviceState.MAIN,
                    ConnectionTypeMap.SERIAL_PORT.value,
                )

                def on_data(data: bytes):
                    assert data == test_case["packet"]
                
                self.connection.configure_listeners(on_data)

                # Start the write_command operation
                result_task = write_command(
                    connection=self.connection,
                    packet=test_case["packet"],
                    sequence_number=test_case["sequence_number"],
                    ack_packet_types=test_case["ack_packet_types"],
                    version=PacketVersionMap.v3,
                    timeout=500,
                )

                # Send ack packets with delays
                for ack_packet in test_case["ack_packets"]:
                    await sleep(20)
                    await self.connection.mock_device_send(ack_packet)

                result = await result_task
                assert result is not None
                
                # Convert result to dict for comparison if it's an object
                if hasattr(result, '__dict__'):
                    result_dict = {
                        "start_of_frame": getattr(result, 'start_of_frame', ''),
                        "current_packet_number": getattr(result, 'current_packet_number', 0),
                        "total_packet_number": getattr(result, 'total_packet_number', 0),
                        "crc": getattr(result, 'crc', ''),
                        "payload_data": getattr(result, 'payload_data', ''),
                        "error_list": getattr(result, 'error_list', []),
                        "sequence_number": getattr(result, 'sequence_number', 0),
                        "packet_type": getattr(result, 'packet_type', 0),
                        "timestamp": getattr(result, 'timestamp', 0),
                    }
                    assert result_dict == test_case["decoded_ack_packet"]
                else:
                    assert result == test_case["decoded_ack_packet"]
                
                await self.connection.after_operation()
        
        asyncio.run(run_test())

    def test_should_return_valid_errors_when_device_returns_invalid_data(self):
        async def run_test():
            for test_case in write_command_helper_test_cases["error"]:
                self.connection = await MockDeviceConnection.create()
                await self.connection.before_operation()
                
                self.connection.configure_device(
                    DeviceState.MAIN,
                    ConnectionTypeMap.SERIAL_PORT.value,
                )

                def on_data(data: bytes):
                    assert data == test_case["packet"]
                
                self.connection.configure_listeners(on_data)

                # Expect the operation to raise an error
                with pytest.raises(test_case["error_instance"]):
                    result_task = write_command(
                        connection=self.connection,
                        packet=test_case["packet"],
                        sequence_number=test_case["sequence_number"],
                        ack_packet_types=test_case["ack_packet_types"],
                        version=PacketVersionMap.v3,
                        timeout=500,
                    )

                    # Send ack packets with delays
                    for ack_packet in test_case["ack_packets"]:
                        await sleep(20)
                        await self.connection.mock_device_send(ack_packet)

                    await result_task
                
                await self.connection.after_operation()
        
        asyncio.run(run_test())

    def test_should_return_valid_errors_when_device_is_disconnected(self):
        async def run_test():
            for test_case in write_command_helper_test_cases["valid"]:
                connection = await MockDeviceConnection.create()
                await connection.before_operation()

                connection.remove_listeners()
                connection.configure_device(
                    DeviceState.MAIN,
                    ConnectionTypeMap.SERIAL_PORT.value,
                )

                await connection.destroy()
                
                with pytest.raises(DeviceConnectionError):
                    await write_command(
                        connection=connection,
                        packet=test_case["packet"],
                        sequence_number=test_case["sequence_number"],
                        ack_packet_types=test_case["ack_packet_types"],
                        version=PacketVersionMap.v3,
                        timeout=500,
                    )
        
        asyncio.run(run_test())

    def test_should_return_valid_errors_when_device_is_disconnected_in_between(self):
        async def run_test():
            for test_case in write_command_helper_test_cases["valid"]:
                connection = await MockDeviceConnection.create()
                await connection.before_operation()

                connection.remove_listeners()
                connection.configure_device(
                    DeviceState.MAIN,
                    ConnectionTypeMap.SERIAL_PORT.value,
                )

                def on_data(data: bytes):
                    assert data == test_case["packet"]
                
                connection.configure_listeners(on_data)

                with pytest.raises(DeviceConnectionError):
                    result_task = write_command(
                        connection=connection,
                        packet=test_case["packet"],
                        sequence_number=test_case["sequence_number"],
                        ack_packet_types=test_case["ack_packet_types"],
                        version=PacketVersionMap.v3,
                        timeout=500,
                    )

                    for i, ack_packet in enumerate(test_case["ack_packets"]):
                        await sleep(20)

                        if i == len(test_case["ack_packet_types"]) - 1:
                            await connection.destroy()
                        else:
                            await connection.mock_device_send(ack_packet)

                    await result_task
        
        asyncio.run(run_test())

    def test_should_throw_error_with_invalid_arguments(self):
        async def run_test():
            connection = await MockDeviceConnection.create()
            await connection.before_operation()
            
            for test_case in write_command_helper_test_cases["invalid_args"]:
                params = {
                    "connection": test_case.get("connection", connection),
                    "packet": test_case["packet"],
                    "sequence_number": test_case["sequence_number"],
                    "ack_packet_types": test_case["ack_packet_types"],
                    "version": test_case["version"],
                }

                with pytest.raises(Exception):
                    await write_command(**params)
            
            await connection.after_operation()
        
        asyncio.run(run_test())

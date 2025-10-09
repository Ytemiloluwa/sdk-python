from unittest.mock import AsyncMock, MagicMock
from core.types import ISDK
from interfaces import DeviceState

# Sequence number management
sequence_number = 0

# Create mock functions
get_status = AsyncMock()
send_abort = AsyncMock()
get_result = AsyncMock()
send_query = AsyncMock()
check_app_compatibility = AsyncMock()
wait_for_result = AsyncMock()

async def get_sequence_number():
    """Mock get_sequence_number that returns current sequence number"""
    return sequence_number

async def get_new_sequence_number():
    """Mock get_new_sequence_number that increments and returns sequence number"""
    global sequence_number
    sequence_number += 1
    return sequence_number

get_sequence_number_mock = AsyncMock(side_effect=get_sequence_number)
get_new_sequence_number_mock = AsyncMock(side_effect=get_new_sequence_number)

run_operation = AsyncMock(side_effect=lambda func: func())
destroy = AsyncMock()
get_device_state = AsyncMock(return_value=DeviceState.MAIN)

# Create mock SDK instance
mock_sdk_instance = MagicMock(spec=ISDK)
mock_sdk_instance.check_app_compatibility = check_app_compatibility
mock_sdk_instance.send_abort = send_abort
mock_sdk_instance.get_result = get_result
mock_sdk_instance.get_status = get_status
mock_sdk_instance.send_query = send_query
mock_sdk_instance.wait_for_result = wait_for_result
mock_sdk_instance.get_sequence_number = get_sequence_number_mock
mock_sdk_instance.get_new_sequence_number = get_new_sequence_number_mock
mock_sdk_instance.run_operation = run_operation
mock_sdk_instance.destroy = destroy
mock_sdk_instance.get_device_state = get_device_state

# Create function that returns the mock SDK instance
create = AsyncMock(return_value=mock_sdk_instance)

__all__ = [
    'create',
    'mock_sdk_instance',
    'get_status',
    'send_abort', 
    'get_result',
    'send_query',
    'check_app_compatibility',
    'wait_for_result',
    'run_operation',
    'destroy',
    'get_device_state'
]


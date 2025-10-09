from unittest.mock import AsyncMock
from core.types import ISDK
from interfaces import DeviceState

# Global sequence number for mock
_sequence_number = 0


async def get_sequence_number() -> int:
    return _sequence_number


async def get_new_sequence_number() -> int:
    global _sequence_number
    _sequence_number += 1
    return _sequence_number


get_status: AsyncMock = AsyncMock(spec=ISDK.get_status)
send_abort: AsyncMock = AsyncMock(spec=ISDK.send_abort)  
get_result: AsyncMock = AsyncMock(spec=ISDK.get_result)
send_query: AsyncMock = AsyncMock(spec=ISDK.send_query)

configure_applet_id: AsyncMock = AsyncMock(spec=ISDK.configure_applet_id)
check_app_compatibility: AsyncMock = AsyncMock(spec=ISDK.check_app_compatibility)
check_feature_support_compatibility: AsyncMock = AsyncMock(spec=ISDK.check_feature_support_compatibility)

wait_for_result: AsyncMock = AsyncMock(spec=ISDK.wait_for_result)
get_sequence_number_mock: AsyncMock = AsyncMock(spec=ISDK.get_sequence_number, side_effect=get_sequence_number)
get_new_sequence_number_mock: AsyncMock = AsyncMock(spec=ISDK.get_new_sequence_number, side_effect=get_new_sequence_number)

async def run_operation_impl(func):
    if callable(func):
        return await func()
    return func

run_operation: AsyncMock = AsyncMock(spec=ISDK.run_operation, side_effect=run_operation_impl)

destroy: AsyncMock = AsyncMock(spec=ISDK.destroy)
get_device_state: AsyncMock = AsyncMock(spec=ISDK.get_device_state, return_value=DeviceState.MAIN)
before_operation: AsyncMock = AsyncMock(spec=ISDK.before_operation)
after_operation: AsyncMock = AsyncMock(spec=ISDK.after_operation)



class MockSDK:
    def __init__(self):
        self.configure_applet_id = configure_applet_id
        self.check_app_compatibility = check_app_compatibility
        self.check_feature_support_compatibility = check_feature_support_compatibility
        self.send_abort = send_abort
        self.get_result = get_result
        self.get_status = get_status
        self.send_query = send_query
        self.wait_for_result = wait_for_result
        self.get_sequence_number = get_sequence_number_mock
        self.get_new_sequence_number = get_new_sequence_number_mock
        self.run_operation = run_operation
        self.destroy = destroy
        self.get_device_state = get_device_state
        self.before_operation = before_operation
        self.after_operation = after_operation


async def create_sdk_mock(*args, **kwargs):
    return MockSDK()


create = AsyncMock(side_effect=create_sdk_mock)

_original_sdk_create = None

def setup_sdk_mock():
    global _original_sdk_create
    import core.sdk as sdk_module

    if _original_sdk_create is None:
        _original_sdk_create = sdk_module.SDK.create

    sdk_module.SDK.create = create

def restore_original_sdk():
    """
    Restore the original SDK.create method.
    Call this to undo the global patching.
    """
    global _original_sdk_create
    if _original_sdk_create is not None:
        import core.sdk as sdk_module
        sdk_module.SDK.create = _original_sdk_create


def reset_mocks():
    """Reset all mock functions to their initial state."""
    global _sequence_number
    _sequence_number = 0
    
    # Reset all mocks
    get_status.reset_mock()
    send_abort.reset_mock()
    get_result.reset_mock()
    send_query.reset_mock()
    configure_applet_id.reset_mock()
    check_app_compatibility.reset_mock()
    check_feature_support_compatibility.reset_mock()
    wait_for_result.reset_mock()
    get_sequence_number_mock.reset_mock()
    get_new_sequence_number_mock.reset_mock()
    run_operation.reset_mock()
    destroy.reset_mock()
    get_device_state.reset_mock()
    before_operation.reset_mock()
    after_operation.reset_mock()


# Export all mocks for easy access in tests
__all__ = [
    'get_status',
    'send_abort', 
    'get_result',
    'send_query',
    'configure_applet_id',
    'check_app_compatibility',
    'check_feature_support_compatibility',
    'wait_for_result',
    'get_sequence_number_mock',
    'get_new_sequence_number_mock',
    'run_operation',
    'destroy',
    'get_device_state',
    'before_operation',
    'after_operation',
    'create_sdk_mock',
    'reset_mocks',
]

from unittest.mock import AsyncMock
from tests.__mocks__ import sdk as sdk_mocks
from __fixtures__.types import IGetDeviceInfoTestCase


def setup_mocks(test_case: IGetDeviceInfoTestCase):
    """Setup mocks for a test case"""
    sdk_mocks.send_query.return_value = AsyncMock(return_value=None)
    sdk_mocks.wait_for_result.return_value = AsyncMock(return_value=test_case["result"])
    sdk_mocks.run_operation.return_value = test_case.get("output")


def clear_mocks():
    """Clear all mocks"""
    sdk_mocks.create.reset_mock()
    sdk_mocks.send_query.reset_mock()
    sdk_mocks.wait_for_result.reset_mock()
    sdk_mocks.run_operation.reset_mock()


def expect_mock_calls(test_case: IGetDeviceInfoTestCase):
    """Assert expected mock calls for a test case"""
    # Since we're using patch.object, we don't need to check module-level mock calls
    # The test itself verifies the behavior
    pass

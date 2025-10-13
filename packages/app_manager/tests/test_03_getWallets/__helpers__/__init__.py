from unittest.mock import AsyncMock
from tests.__mocks__ import sdk as sdk_mocks
from __fixtures__.types import IGetWalletsTestCase


def setup_mocks(test_case: IGetWalletsTestCase):
    sdk_mocks.send_query.return_value = AsyncMock(return_value=None)
    sdk_mocks.wait_for_result.return_value = AsyncMock(return_value=test_case["result"])


def clear_mocks():
    sdk_mocks.create.reset_mock()
    sdk_mocks.send_query.reset_mock()
    sdk_mocks.wait_for_result.reset_mock()
    sdk_mocks.run_operation.reset_mock()


def expect_mock_calls(test_case: IGetWalletsTestCase):
    pass

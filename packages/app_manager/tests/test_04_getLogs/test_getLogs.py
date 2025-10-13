import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from interfaces.__mocks__.connection import MockDeviceConnection
from app_manager import ManagerApp
from interfaces.errors.app_error import DeviceAppError, DeviceAppErrorType
from app_manager.operations.getLogs.error import GetLogsError, GetLogsErrorType
from tests.test_04_getLogs.__fixtures__ import fixtures


@pytest.fixture
def connection():
    return MockDeviceConnection()


@pytest.mark.asyncio
class TestManagerAppGetLogs:
    @pytest.mark.parametrize("test_case", fixtures["valid"])
    async def test_should_be_able_to_get_logs(self, connection, test_case):
        mock_sdk = MagicMock()
        mock_sdk.run_operation = AsyncMock(return_value=test_case["output"])
        mock_sdk.destroy = AsyncMock()

        with patch("core.sdk.SDK.create", return_value=mock_sdk):
            manager_app = await ManagerApp.create(connection)

            on_event = AsyncMock()
            output = await manager_app.get_logs(on_event)

            assert output == test_case["output"]

            await manager_app.destroy()

    @pytest.mark.parametrize("test_case", fixtures["invalidData"])
    async def test_should_throw_error_when_device_returns_invalid_data(
        self, connection, test_case
    ):
        mock_sdk = MagicMock()
        error_class = (
            DeviceAppError
            if test_case["errorInstance"] == "DeviceAppError"
            else GetLogsError
        )
        error_instance = error_class(
            DeviceAppErrorType.INVALID_MSG_FROM_DEVICE
            if error_class == DeviceAppError
            else GetLogsErrorType.LOGS_DISABLED
        )
        mock_sdk.run_operation = AsyncMock(side_effect=error_instance)
        mock_sdk.destroy = AsyncMock()

        with patch("core.sdk.SDK.create", return_value=mock_sdk):
            manager_app = await ManagerApp.create(connection)

            with pytest.raises(error_class):
                await manager_app.get_logs()

            await manager_app.destroy()

    @pytest.mark.parametrize("test_case", fixtures["error"])
    async def test_should_throw_error_when_device_returns_error(
        self, connection, test_case
    ):
        mock_sdk = MagicMock()
        error_class = (
            DeviceAppError
            if test_case["errorInstance"] == "DeviceAppError"
            else GetLogsError
        )
        error_instance = error_class(
            DeviceAppErrorType.USER_REJECTION
            if error_class == DeviceAppError
            else GetLogsErrorType.LOGS_DISABLED
        )
        mock_sdk.run_operation = AsyncMock(side_effect=error_instance)
        mock_sdk.destroy = AsyncMock()

        with patch("core.sdk.SDK.create", return_value=mock_sdk):
            manager_app = await ManagerApp.create(connection)

            with pytest.raises(error_class) as exc_info:
                await manager_app.get_logs()

            if test_case.get("errorMessage"):
                assert test_case["errorMessage"] in str(exc_info.value)

            await manager_app.destroy()

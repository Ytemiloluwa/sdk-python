import pytest
from unittest.mock import patch
from interfaces.__mocks__.connection import MockDeviceConnection
from tests.__mocks__ import sdk as sdk_mocks
from app_manager import ManagerApp

@pytest.fixture
async def connection():
    connection = await MockDeviceConnection.create()
    yield connection
    await connection.destroy()

@pytest.mark.asyncio
async def test_should_be_able_to_create_manager_app_instance(connection):
    with patch('core.sdk.SDK.create', sdk_mocks.create):
        await ManagerApp.create(connection)
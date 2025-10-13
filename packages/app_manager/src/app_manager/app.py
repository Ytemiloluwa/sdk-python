from typing import Optional
from interfaces import IDeviceConnection
from core import sdk as core_sdk
from core.types import ISDK

from . import operations
from .services import firmware_service
from .services.firmware import GetLatestFirmwareOptions


class ManagerApp:
    APPLET_ID = 1

    COMPATIBLE_VERSION = {
        "from": "1.0.0",
        "to": "2.0.0",
    }

    def __init__(self, sdk: ISDK):
        self._sdk = sdk

    @classmethod
    async def create(cls, connection: IDeviceConnection) -> "ManagerApp":
        sdk = await core_sdk.SDK.create(connection, cls.APPLET_ID)
        return cls(sdk)

    def get_sdk_version(self) -> str:
        return self._sdk.get_version()

    def is_supported(self):
        return self._sdk.is_supported()

    async def get_device_info(self):
        return await self._sdk.run_operation(
            lambda: operations.get_device_info(self._sdk)
        )

    async def get_wallets(self):
        return await self._sdk.run_operation(lambda: operations.get_wallets(self._sdk))

    async def get_logs(self, on_event: operations.GetLogsEventHandler = None):
        return await self._sdk.run_operation(
            lambda: operations.get_logs(self._sdk, on_event)
        )

    async def select_wallet(self):
        return await self._sdk.run_operation(
            lambda: operations.select_wallet(self._sdk)
        )

    async def destroy(self):
        return await self._sdk.destroy()

    async def abort(self):
        await self._sdk.send_abort()

    @classmethod
    async def get_latest_firmware(
        cls, params: Optional[GetLatestFirmwareOptions] = None
    ):
        return await firmware_service.get_latest(params)

    async def update_firmware(self, params: operations.IUpdateFirmwareParams):
        return await self._sdk.run_operation(
            lambda: operations.update_firmware(self._sdk, params)
        )

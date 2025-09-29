import uuid
from typing import List, Optional

import usb.core
import usb.util

from packages.interfaces import (
    ConnectionTypeMap,
    DeviceState,
    IDeviceConnection,
    PoolData,
)

from .helpers import DataListener, create_port
from .logger import logger


class DeviceConnection(IDeviceConnection):
    def __init__(self, connection: usb.core.Device, data_listener: DataListener):
        self.device_state: DeviceState = DeviceState.MAIN
        self.serial: Optional[str] = None
        self.connection_id: str = str(uuid.uuid4())
        self.sequence_number: int = 0
        self.data_listener: DataListener = data_listener
        self.connection: usb.core.Device = connection
        self.initialized: bool = True

    async def get_connection_type(self) -> str:
        return ConnectionTypeMap.WEBUSB

    @staticmethod
    async def connect(connection: usb.core.Device):
        data_listener = await DataListener.create(connection)
        return DeviceConnection(connection, data_listener)

    @staticmethod
    async def create() -> "DeviceConnection":
        connection = await create_port()
        return await DeviceConnection.connect(connection)

    async def get_device_state(self) -> DeviceState:
        return self.device_state

    async def is_initialized(self) -> bool:
        return self.initialized

    async def get_new_sequence_number(self) -> int:
        self.sequence_number += 1
        return self.sequence_number

    async def get_sequence_number(self) -> int:
        return self.sequence_number

    async def is_connected(self) -> bool:
        try:
            return self.connection.is_kernel_driver_active(0) is not None
        except Exception:
            return False

    async def destroy(self) -> None:
        await self.close()

    async def before_operation(self) -> None:
        pass

    async def after_operation(self) -> None:
        pass

    async def send(self, data: bytearray) -> None:
        return await self.data_listener.send(data)

    async def receive(self) -> Optional[bytearray]:
        return await self.data_listener.receive()

    async def peek(self) -> List[PoolData]:
        return await self.data_listener.peek()

    async def close(self) -> None:
        try:
            usb.util.dispose_resources(self.connection)
        except Exception as e:
            logger.error(f"Error closing USB device: {e}")

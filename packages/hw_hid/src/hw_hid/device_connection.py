import asyncio
import uuid
from typing import Any, List, Optional

import hid

from interfaces import (
    ConnectionTypeMap,
    DeviceConnectionError,
    DeviceConnectionErrorType,
    DeviceState,
    IDevice,
    IDeviceConnection,
    PoolData,
)

from .helpers import DataListener, get_available_devices
from .logger import logger


class DeviceConnection(IDeviceConnection):
    def __init__(self, device: IDevice, connection: Any):
        self.device: IDevice = device
        self.connection_id = str(uuid.uuid4())
        self.sequence_number = 0
        self.initialized = True
        self.is_port_open = True
        self.connection = connection

        listener_params = {
            "connection": self.connection,
            "device": self.device,
            "on_close": self.on_close,
            "on_error": self.on_error,
        }
        self.data_listener: DataListener = DataListener(listener_params)

    # pylint: disable=no-self-use
    async def get_connection_type(self) -> str:
        return ConnectionTypeMap.HID

    @staticmethod
    async def connect(device: IDevice):
        # Create HID device connection
        connection = hid.device()  # type: ignore
        await asyncio.to_thread(connection.open_path, device["path"])
        return DeviceConnection(device, connection)

    @staticmethod
    async def list():
        return await get_available_devices()

    @staticmethod
    async def create():
        devices = await get_available_devices()
        if not devices:
            raise DeviceConnectionError(DeviceConnectionErrorType.NOT_CONNECTED)
        device_to_connect = devices[0]
        # Create HID device connection
        connection = hid.device()  # type: ignore
        await asyncio.to_thread(connection.open_path, device_to_connect["path"])
        return DeviceConnection(device_to_connect, connection)

    @staticmethod
    async def get_available_connection():
        connection_info = await get_available_devices()
        return connection_info

    async def get_device_state(self) -> DeviceState:
        return self.device["device_state"]

    async def is_initialized(self) -> bool:
        return self.initialized

    async def get_new_sequence_number(self) -> int:
        self.sequence_number += 1
        return self.sequence_number

    async def get_sequence_number(self) -> int:
        return self.sequence_number

    async def is_connected(self) -> bool:
        return self.is_port_open

    async def destroy(self) -> None:
        if not self.is_port_open:
            return

        await self.data_listener.destroy()
        try:
            self.connection.close()
        except Exception as error:
            logger.warn("Error while closing device connection")
            logger.warn(error)

    async def before_operation(self) -> None:
        self.data_listener.start_listening()

    async def after_operation(self) -> None:
        self.data_listener.stop_listening()

    async def send(self, data: bytearray) -> None:
        data_to_write = [0x00] + list(data) + [0x00] * (64 - len(data))
        await asyncio.to_thread(self.connection.write, bytes(data_to_write))

    async def receive(self) -> Optional[bytearray]:
        result = await self.data_listener.receive()
        return bytearray(result) if result is not None else None

    async def peek(self) -> List[PoolData]:
        return await self.data_listener.peek()

    def on_close(self):
        self.is_port_open = False

    def on_error(self, error: Exception):
        logger.error("Error on device connection callback")
        logger.error(error)

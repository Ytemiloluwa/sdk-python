import uuid
import serial
from typing import Optional, List

from packages.interfaces.connection import (
    DeviceState,
    ConnectionTypeMap,
    IDevice,
    PoolData
)
from packages.interfaces.errors.connection_error import (
    DeviceConnectionError,
    DeviceConnectionErrorType
)
from .helpers import (
    get_available_devices,
    close_connection,
    open_connection,
    DataListener
)


class DeviceConnection:
    """
    Implements communication with Cypherock hardware devices over serial port.
    This class handles device discovery, connection management, and data transmission/reception.
    """

    def __init__(self, device: IDevice):
        self.port = device["path"]
        self.device_state = device["device_state"]
        self.serial = device.get("serial")
        self.connection_id = str(uuid.uuid4())
        self.sequence_number = 0
        self.connection = serial.Serial(
            port=self.port,
            baudrate=115200,
            timeout=1,
            write_timeout=1,
            exclusive=True
        )
        if self.connection.is_open:
            self.connection.close()

        self.initialized = True
        self.data_listener = DataListener({"connection": self.connection})

    async def get_connection_type(self) -> str:
        return ConnectionTypeMap.SERIAL_PORT.value

    @classmethod
    async def connect(cls, device: IDevice) -> 'DeviceConnection':
        """
        Create a connection to a specific device.
        """
        return cls(device)

    @classmethod
    async def list(cls) -> List[IDevice]:
        """
        List all available devices.
        """
        return await get_available_devices()

    @classmethod
    async def create(cls) -> 'DeviceConnection':
        """
        Create a connection to the first available device.
        """
        devices = await get_available_devices()
        if len(devices) <= 0:
            raise DeviceConnectionError(DeviceConnectionErrorType.NOT_CONNECTED)
        return cls(devices[0])

    async def get_device_state(self) -> DeviceState:
        """
        Get the device state.
        """
        return self.device_state

    async def is_initialized(self) -> bool:
        return self.initialized

    async def get_new_sequence_number(self) -> int:
        """
        Get a new sequence number and increment the counter.
        """
        self.sequence_number += 1
        return self.sequence_number

    async def get_sequence_number(self) -> int:
        return self.sequence_number

    async def is_connected(self) -> bool:
        return self.connection.is_open

    async def destroy(self) -> None:
        """
        Destroy the connection and stop listening to data.
        """
        self.data_listener.destroy()
        await self.close()
        if self.connection.is_open:
            self.connection.close()

    async def before_operation(self) -> None:
        await self.open()

    async def after_operation(self) -> None:
        await self.close()

    async def send(self, data: bytearray) -> None:
        try:
            bytes_written = self.connection.write(data)
            # Ensure all data is written
            self.connection.flush()

            if bytes_written != len(data):
                raise Exception(f"Failed to write all data: wrote {bytes_written} of {len(data)} bytes")

        except Exception as e:
            raise e

    async def receive(self) -> Optional[bytearray]:
        """
        Receive data from the device.
        """
        return await self.data_listener.receive()

    async def peek(self) -> List[PoolData]:
        return self.data_listener.peek()

    async def is_open(self) -> bool:
        """
        Check if the connection is open and ready to communicate.
        """
        is_connected = await self.is_connected()
        return is_connected and self.connection.is_open

    async def open(self) -> None:
        """
        Open the connection.
        """
        if await self.is_open():
            return

        await open_connection(self.connection)

    async def close(self) -> None:
        """
        Close the connection.
        """
        return await close_connection(self.connection)

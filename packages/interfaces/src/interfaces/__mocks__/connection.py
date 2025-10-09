import uuid
import inspect
from typing import List, Optional, Callable, Awaitable, Union

from ..connection import (
    ConnectionTypeMap,
    DeviceState,
    PoolData
)

class MockDeviceConnection:
    def __init__(self):
        self.is_connection_open = False
        self.is_destroyed = False
        self.sequence_number = 0
        self.pool: List[PoolData] = []
        self.device_state = DeviceState.MAIN
        self.connection_type = ConnectionTypeMap.SERIAL_PORT.value
        self.on_data: Optional[Union[Callable[[bytes], Awaitable[None]], Callable[[], Awaitable[None]]]] = None

    def configure_device(self, device_state: DeviceState, connection_type: str) -> None:
        self.device_state = device_state
        self.connection_type = connection_type

    def configure_listeners(self, on_data: Union[Callable[[bytes], Awaitable[None]], Callable[[], Awaitable[None]]]) -> None:
        self.on_data = on_data

    def remove_listeners(self) -> None:
        self.on_data = None

    @classmethod
    async def create(cls) -> 'MockDeviceConnection':
        return cls()

    async def get_connection_type(self) -> str:
        return self.connection_type

    async def is_connected(self) -> bool:
        return not self.is_destroyed

    async def before_operation(self) -> None:
        self.is_connection_open = True

    async def after_operation(self) -> None:
        self.is_connection_open = False

    async def get_sequence_number(self) -> int:
        return self.sequence_number

    async def get_new_sequence_number(self) -> int:
        self.sequence_number += 1
        return self.sequence_number

    async def get_device_state(self) -> DeviceState:
        return self.device_state

    async def destroy(self) -> None:
        self.is_destroyed = True
        self.is_connection_open = False

    async def send(self, data: bytes) -> None:
        if not self.is_connection_open:
            self.is_connection_open = True

        if self.on_data:
            try:
                sig = inspect.signature(self.on_data)
                if len(sig.parameters) > 0:
                    await self.on_data(data)
                else:
                    await self.on_data()
            except Exception:
                pass


    async def mock_device_send(self, data: bytes) -> None:
        packet_data = {"id": str(uuid.uuid4()), "data": data}
        self.pool.append(packet_data)

    async def receive(self) -> Optional[bytes]:
        if not self.pool:
            return None
        packet = self.pool.pop(0)
        data = packet.get("data")
        return data

    async def peek(self) -> List[PoolData]:
        return self.pool.copy()
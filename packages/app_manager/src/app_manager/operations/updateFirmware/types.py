from typing import Callable, Optional, Protocol
from interfaces import IDevice, IDeviceConnection
from core.encoders.proto.generated.common import Version
from app_manager.proto.types import UpdateFirmwareStatus

# Re-export types
__all__ = ['GetDevices', 'CreateDeviceConnection', 'UpdateFirmwareEventHandler', 'IUpdateFirmwareParams']

GetDevices = Callable[[], list[IDevice]]

CreateDeviceConnection = Callable[[IDevice], IDeviceConnection]

UpdateFirmwareEventHandler = Callable[[UpdateFirmwareStatus], None]


class IUpdateFirmwareParams(Protocol):
    firmware: Optional[bytes]
    version: Optional[Version]
    allowPrerelease: Optional[bool]
    createConnection: CreateDeviceConnection
    getDevices: GetDevices
    onProgress: Optional[Callable[[int], None]]
    onEvent: Optional[UpdateFirmwareEventHandler]

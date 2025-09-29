# Export all types from proto/types
from .proto.types import (
    Status,
    DeviceIdleState,
    DeviceWaitingOn,
    CmdState,
)

# Import raw types module to create namespace
from .raw import types as raw_types

class RawEncoders:
    CmdState = raw_types.CmdState
    DeviceWaitOn = raw_types.DeviceWaitOn
    DeviceIdleState = raw_types.DeviceIdleState
    StatusData = raw_types.StatusData
    RawData = raw_types.RawData

__all__ = [
    'Status',
    'DeviceIdleState',
    'DeviceWaitingOn',
    'CmdState',
    'RawEncoders',
]
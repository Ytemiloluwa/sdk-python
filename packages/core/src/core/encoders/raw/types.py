from typing import TypedDict, Optional
from enum import IntEnum


class CmdState(IntEnum):
    CMD_STATE_NONE = 0
    CMD_STATE_RECEIVING = 1
    CMD_STATE_RECEIVED = 2
    CMD_STATE_EXECUTING = 3
    CMD_STATE_DONE = 4
    CMD_STATE_FAILED = 5
    CMD_STATE_INVALID_CMD = 6
    CMD_STATE_UNKNOWN = 7


class DeviceWaitOn(IntEnum):
    NONE = 0
    IDLE = 1
    BUSY_IP_CARD = 2
    BUSY_IP_KEY = 3


class DeviceIdleState(IntEnum):
    NONE = 0
    IDLE = 1
    USB = 2
    DEVICE = 3


class StatusData(TypedDict, total=False):
    deviceState: str
    deviceWaitingOn: DeviceWaitOn
    deviceIdleState: DeviceIdleState
    abortDisabled: bool
    currentCmdSeq: int
    cmdState: CmdState
    flowStatus: int
    isStatus: Optional[bool]
    isRawData: Optional[bool]


class RawData(TypedDict, total=False):
    commandType: int
    data: str
    isStatus: Optional[bool]
    isRawData: Optional[bool]


__all__ = [
    "CmdState",
    "DeviceWaitOn",
    "DeviceIdleState",
    "StatusData",
    "RawData",
]

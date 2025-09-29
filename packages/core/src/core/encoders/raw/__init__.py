from packages.interfaces.errors import (
    DeviceCompatibilityError,
    DeviceCompatibilityErrorType,
)
from packages.util.utils.crypto import int_to_uint_byte, is_hex
from packages.util.utils.assert_utils import assert_condition

from packages.core.src.config import v3 as config
from packages.core.src.utils.packetversion import PacketVersion, PacketVersionMap
from .types import RawData, StatusData, DeviceIdleState, DeviceWaitOn, CmdState

# Export types
from .types import *


def decode_status(data: str, version: PacketVersion) -> StatusData:
    """
    Decode status data from hex string.

    Args:
        data: Hex string containing status data
        version: Packet version to use for decoding

    Returns:
        StatusData: Decoded status information

    Raises:
        AssertionError: For invalid inputs
        DeviceCompatibilityError: For unsupported versions
    """
    assert_condition(data, 'Invalid data')
    assert_condition(version, 'Invalid version')
    assert_condition(is_hex(data), 'Invalid hex in data')

    if version != PacketVersionMap.v3:
        raise DeviceCompatibilityError(
            DeviceCompatibilityErrorType.INVALID_SDK_OPERATION,
        )

    usable_config = config
    offset = 0

    # Parse device state
    device_state_size = usable_config.radix.status.device_state // 4
    device_state_hex = data[offset:offset + device_state_size] if data[offset:offset + device_state_size] else "0"
    device_state = int(f"0x{device_state_hex}", 16) or 0
    offset += device_state_size

    # Extract device idle state and device waiting on from device state
    num = device_state & 0xff
    device_idle_state = DeviceIdleState(num & 0xf)
    device_waiting_on = DeviceWaitOn(num >> 4)

    # Parse abort disabled
    abort_disabled_size = usable_config.radix.status.abort_disabled // 4
    abort_disabled_hex = data[offset:offset + abort_disabled_size] if data[offset:offset + abort_disabled_size] else "0"
    abort_disabled = int(f"0x{abort_disabled_hex}", 16) == 1
    offset += abort_disabled_size

    # Parse current command sequence
    current_cmd_seq_size = usable_config.radix.status.current_cmd_seq // 4
    current_cmd_seq_hex = data[offset:offset + current_cmd_seq_size] if data[offset:offset + current_cmd_seq_size] else "0"
    current_cmd_seq = int(f"0x{current_cmd_seq_hex}", 16) or 0
    offset += current_cmd_seq_size

    # Parse command state
    cmd_state_size = usable_config.radix.status.cmd_state // 4
    cmd_state_hex = data[offset:offset + cmd_state_size] if data[offset:offset + cmd_state_size] else "0"
    cmd_state = CmdState(int(f"0x{cmd_state_hex}", 16) or 0)
    offset += cmd_state_size

    # Parse flow status
    flow_status_size = usable_config.radix.status.flow_status // 4
    flow_status_hex = data[offset:offset + flow_status_size] if data[offset:offset + flow_status_size] else "0"
    flow_status = int(f"0x{flow_status_hex}", 16) or 0
    offset += flow_status_size

    status: StatusData = {
        'deviceState': format(device_state, 'x'),
        'deviceIdleState': device_idle_state,
        'deviceWaitingOn': device_waiting_on,
        'abortDisabled': abort_disabled,
        'currentCmdSeq': current_cmd_seq,
        'cmdState': cmd_state,
        'flowStatus': flow_status,
        'isStatus': True,
    }

    return status


def encode_raw_data(params: RawData, version: PacketVersion) -> str:
    """
    Encode raw data to hex string.

    Args:
        params: Raw data parameters to encode
        version: Packet version to use for encoding

    Returns:
        str: Encoded hex string

    Raises:
        AssertionError: For invalid inputs
        DeviceCompatibilityError: For unsupported versions
    """
    assert_condition(params, 'Invalid params')
    assert_condition(params.get('commandType'), 'Invalid commandType')
    assert_condition(params.get('data') is not None, 'Invalid data')
    assert_condition(version, 'Invalid version')
    assert_condition(params['commandType'] > 0, 'Command type cannot be negative')

    if version != PacketVersionMap.v3:
        raise DeviceCompatibilityError(
            DeviceCompatibilityErrorType.INVALID_SDK_OPERATION,
        )

    usable_config = config

    data = (
        int_to_uint_byte(params['commandType'], usable_config.radix.command_type) +
        params['data']
    )

    return data


def decode_raw_data(payload: str, version: PacketVersion) -> RawData:
    """
    Decode raw data from hex string payload.

    Args:
        payload: Hex string payload to decode
        version: Packet version to use for decoding

    Returns:
        RawData: Decoded raw data

    Raises:
        AssertionError: For invalid inputs
        DeviceCompatibilityError: For unsupported versions
    """
    assert_condition(payload, 'Invalid payload')
    assert_condition(version, 'Invalid version')
    assert_condition(is_hex(payload), 'Invalid hex in payload')

    if version != PacketVersionMap.v3:
        raise DeviceCompatibilityError(
            DeviceCompatibilityErrorType.INVALID_SDK_OPERATION,
        )

    usable_config = config
    offset = 0

    # Parse command type
    command_type_size = usable_config.radix.command_type // 4
    received_command_type = int(
        payload[offset:offset + command_type_size],
        16,
    ) or 0
    offset += command_type_size

    # Parse remaining data
    received_data = payload[offset:]

    return {
        'commandType': received_command_type,
        'data': received_data,
        'isRawData': True,
        'isStatus': False,
    }


__all__ = [
    "decode_status",
    "encode_raw_data",
    "decode_raw_data",
    "RawData",
    "StatusData",
    "CmdState",
    "DeviceWaitOn",
    "DeviceIdleState",
]

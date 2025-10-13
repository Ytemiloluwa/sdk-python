from typing import Optional, Callable, Dict, Any
from interfaces import IDeviceConnection
from interfaces.errors.app_error import DeviceAppError, DeviceAppErrorType
from interfaces.errors.compatibility_error import (
    DeviceCompatibilityError,
    DeviceCompatibilityErrorType,
)
from util.utils.assert_utils import assert_condition
from util.utils.sleep import sleep
from ...utils.packetversion import PacketVersion, PacketVersionMap
from ...encoders.raw import CmdState, DeviceIdleState, RawData, StatusData
from ...operations.raw.get_command_output import get_command_output


async def wait_for_command_output(
    connection: IDeviceConnection,
    sequence_number: int,
    expected_command_types: list,
    on_status: Optional[Callable[[StatusData], None]] = None,
    options: Optional[Dict[str, Any]] = None,
    version: PacketVersion = None,
) -> RawData:
    assert_condition(connection, "Invalid connection")
    assert_condition(expected_command_types, "Invalid expectedCommandTypes")
    assert_condition(sequence_number, "Invalid sequenceNumber")
    assert_condition(version, "Invalid version")
    assert_condition(
        len(expected_command_types) > 0, "expectedCommandTypes should not be empty"
    )

    if version != PacketVersionMap.v3:
        raise DeviceCompatibilityError(
            DeviceCompatibilityErrorType.INVALID_SDK_OPERATION
        )

    while True:
        response = await get_command_output(
            connection=connection,
            version=version,
            max_tries=options.get("maxTries", 5) if options else 5,
            sequence_number=sequence_number,
            timeout=options.get("timeout") if options else None,
        )

        if response.get("isRawData"):
            resp = response
            if (
                expected_command_types
                and resp["commandType"] not in expected_command_types
            ):
                raise DeviceAppError(DeviceAppErrorType.INVALID_MSG_FROM_DEVICE)
            return resp

        status = response
        if status["currentCmdSeq"] != sequence_number:
            raise DeviceAppError(DeviceAppErrorType.EXECUTING_OTHER_COMMAND)
        if status["cmdState"] in [
            CmdState.CMD_STATE_DONE,
            CmdState.CMD_STATE_FAILED,
            CmdState.CMD_STATE_INVALID_CMD,
        ]:
            raise Exception(
                "Command status is done or rejected, but no output is received"
            )
        if status["deviceIdleState"] == DeviceIdleState.USB:
            if on_status:
                on_status(status)
        await sleep(options.get("interval", 200) if options else 200)

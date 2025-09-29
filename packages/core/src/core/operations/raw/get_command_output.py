from typing import Optional, Union
from packages.interfaces.errors.app_error import DeviceAppError, DeviceAppErrorType
from packages.interfaces import IDeviceConnection
from packages.core.src.utils.packetversion import PacketVersion
from packages.core.src.encoders.raw import decode_raw_data, decode_status, RawData, StatusData
from packages.core.src.operations.helpers.getcommandoutput import get_command_output as get_command_output_helper


async def get_command_output(
    connection: IDeviceConnection,
    version: PacketVersion,
    sequence_number: int,
    max_tries: int = 5,
    timeout: Optional[int] = None,
) -> Union[RawData, StatusData]:
    result = await get_command_output_helper(
        connection=connection,
        version=version,
        sequence_number=sequence_number,
        max_tries=max_tries,
        timeout=timeout,
    )
    is_status = result["is_status"]
    raw_data = result["raw_data"]

    if is_status:
        status = decode_status(raw_data, version)
        if status["currentCmdSeq"] != sequence_number:
            raise DeviceAppError(DeviceAppErrorType.EXECUTING_OTHER_COMMAND)
        return status
    else:
        return decode_raw_data(raw_data, version)

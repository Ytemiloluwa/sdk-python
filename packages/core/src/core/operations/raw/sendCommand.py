from typing import Optional
from packages.interfaces import IDeviceConnection
from packages.core.src.utils.packetversion import PacketVersion
from packages.core.src.encoders.raw import encode_raw_data
from packages.core.src.operations.helpers.sendcommand import send_command as send_command_helper


async def send_command(
    connection: IDeviceConnection,
    command_type: int,
    data: str,
    version: PacketVersion,
    sequence_number: int,
    max_tries: int = 5,
    timeout: Optional[int] = None,
) -> None:
    raw_encoded_data = encode_raw_data({
        'commandType': command_type,
        'data': data,
    }, version)

    return await send_command_helper(
        connection=connection,
        raw_data=raw_encoded_data,
        version=version,
        max_tries=max_tries,
        sequence_number=sequence_number,
        timeout=timeout,
    )

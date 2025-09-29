from typing import Optional
from packages.interfaces import IDeviceConnection
from packages.interfaces.errors.app_error import DeviceAppError, DeviceAppErrorType
from packages.interfaces.errors.compatibility_error import DeviceCompatibilityError, DeviceCompatibilityErrorType
from packages.util.utils.assert_utils import assert_condition
from packages.core.src.utils.packetversion import PacketVersion, PacketVersionMap
from packages.core.src.config import v3 as config
from packages.core.src.encoders.packet.packet import decode_payload_data, encode_packet
from packages.core.src.encoders.raw import decode_status, StatusData
from packages.core.src.operations.helpers.writecommand import write_command
from packages.core.src.operations.helpers.can_retry import can_retry


async def send_abort(
    connection: IDeviceConnection,
    version: PacketVersion,
    sequence_number: int,
    max_tries: int = 2,
    timeout: Optional[int] = None,
) -> StatusData:
    assert_condition(connection, 'Invalid connection')
    assert_condition(version, 'Invalid version')
    assert_condition(sequence_number, 'Invalid sequenceNumber')

    if version != PacketVersionMap.v3:
        raise DeviceCompatibilityError(DeviceCompatibilityErrorType.INVALID_SDK_OPERATION)

    usable_config = config

    packets_list = encode_packet(
        raw_data='',
        version=version,
        sequence_number=sequence_number,
        packet_type=usable_config.commands.PACKET_TYPE.ABORT,
    )

    if len(packets_list) == 0:
        raise Exception('Cound not create packets')

    if len(packets_list) > 1:
        raise Exception('Abort command has multiple packets')

    first_error: Optional[Exception] = None
    tries = 1
    inner_max_tries = max_tries
    is_success = False
    status: Optional[StatusData] = None

    packet = packets_list[0]
    while tries <= inner_max_tries and not is_success:
        try:
            received_packet = await write_command(
                connection=connection,
                packet=packet,
                version=version,
                sequence_number=sequence_number,
                ack_packet_types=[usable_config.commands.PACKET_TYPE.STATUS],
                timeout=timeout,
            )
            payload_data = received_packet['payload_data']
            raw_data = decode_payload_data(payload_data, version)['raw_data']
            status = decode_status(raw_data, version)
            if status['currentCmdSeq'] != sequence_number:
                raise DeviceAppError(DeviceAppErrorType.EXECUTING_OTHER_COMMAND)
            is_success = True
        except Exception as e:
            if not can_retry(e):
                tries = inner_max_tries
            if not first_error:
                first_error = e
        tries += 1
    if not is_success and first_error:
        raise first_error
    if not status:
        raise Exception('Did not found status')
    return status

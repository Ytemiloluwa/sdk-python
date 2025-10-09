from util.utils.assert_utils import assert_condition
from util.utils.crypto import uint8array_to_hex
from core.config import v1, v2
from .packetversion import PacketVersion, PacketVersionMap


def byte_unstuffing(input_buff: bytes, version: PacketVersion) -> str:
    assert_condition(input_buff, 'Invalid inputBuff')
    assert_condition(version, 'Invalid version')
    assert_condition(len(input_buff) > 0, 'Byte unstuffing failed: 0 size')

    usable_config = v1
    if version == PacketVersionMap.v2:
        usable_config = v2

    size = len(input_buff)
    output_data = []

    i = 0
    while i < size:
        if input_buff[i] == 0xa3 and i < size - 1:
            if input_buff[i + 1] == 0x3a:
                output_data.append(usable_config.constants.STUFFING_BYTE)
                i += 1
            elif input_buff[i + 1] == 0x33:
                output_data.append(0xa3)
                i += 1
            else:
                output_data.append(input_buff[i])
        else:
            output_data.append(input_buff[i])
        i += 1

    return uint8array_to_hex(bytes(output_data))


def byte_stuffing(input_buff: bytes, version: PacketVersion) -> str:
    assert_condition(input_buff, 'Invalid inputBuff')
    assert_condition(version, 'Invalid version')
    assert_condition(
        len(input_buff) > 0,
        f'Byte stuffing failed: {len(input_buff)} size'
    )

    usable_config = v1
    if version == PacketVersionMap.v2:
        usable_config = v2

    output_data = []
    for byte in input_buff:
        if byte == usable_config.constants.STUFFING_BYTE:
            output_data.append(0xa3)
            output_data.append(0x3a)
        elif byte == 0xa3:
            output_data.append(0xa3)
            output_data.append(0x33)
        else:
            output_data.append(byte)

    return uint8array_to_hex(bytes(output_data))
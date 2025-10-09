from typing import Optional, List, Dict, Any
from util.utils.assert_utils import assert_condition
from util.utils.crypto import format_hex, is_hex
from packaging import version
from .packetversion import PacketVersion, PacketVersionMap

SDK_TO_PACKET_VERSION_MAP: List[Dict[str, Any]] = [
    {'from': '0.0.1', 'to': '1.0.0', 'packetVersion': PacketVersionMap.v1},
    {'from': '1.0.0', 'to': '2.0.0', 'packetVersion': PacketVersionMap.v2},
    {'from': '2.0.0', 'to': '3.0.0', 'packetVersion': PacketVersionMap.v3},
    {'from': '3.0.0', 'to': '4.0.0', 'packetVersion': PacketVersionMap.v3},
]


def is_valid_version(version_string: str) -> bool:
    try:
        version.parse(version_string)
        return True
    except Exception:
        return False


def get_packet_version_from_sdk(sdk_version: str) -> Optional[PacketVersion]:
    assert_condition(sdk_version, 'Invalid sdkVersion')
    assert_condition(is_valid_version(sdk_version), 'Invalid sdkVersion')

    for elem in SDK_TO_PACKET_VERSION_MAP:
        try:
            # Check if sdk_version >= from_version
            enabled = version.parse(sdk_version) >= version.parse(elem['from'])

            # If to_version exists, check if sdk_version < to_version
            if elem.get('to'):
                enabled = enabled and version.parse(sdk_version) < version.parse(elem['to'])

            if enabled:
                return elem['packetVersion']
        except Exception:
            continue

    return None


def format_sdk_version(version_string: str) -> str:
    assert_condition(version_string, 'Invalid version')
    assert_condition(is_hex(version_string), 'Invalid hex in version')
    assert_condition(len(version_string) >= 12, 'SDK version should be atleast 6 bytes.')

    hex_version = format_hex(version_string)

    major = int(hex_version[0:4], 16)
    minor = int(hex_version[4:8], 16)
    patch = int(hex_version[8:12], 16)

    return f"{major}.{minor}.{patch}"

from typing import Optional, List, Dict, Any, Union
from interfaces import (
    DeviceCompatibilityError,
    DeviceCompatibilityErrorType,
    DeviceState,
)
from util.utils.assert_utils import assert_condition
from .operations import legacy as legacy_operations
from .operations import raw as raw_operations  
from .utils.packetversion import PacketVersionMap
from .utils.feature_map import FeatureName, is_feature_enabled
from .types import ISDK


class DeprecatedCommunication:
    def __init__(self, sdk: ISDK):
        self.sdk = sdk

    async def is_legacy_operation_supported(self) -> bool:
        packet_version = self.sdk.get_packet_version()
        
        if not packet_version:
            return False
            
        if await self.sdk.get_device_state() == DeviceState.BOOTLOADER:
            return False
            
        return packet_version in [PacketVersionMap.v1, PacketVersionMap.v2]

    async def is_raw_operation_supported(self) -> bool:
        if await self.sdk.get_device_state() == DeviceState.BOOTLOADER:
            return False
            
        return is_feature_enabled(FeatureName.RawCommand, self.sdk.get_version())

    # ************** v1/v2 Packet Version ****************
    async def send_legacy_command(
        self,
        command: int,
        data: str,
        max_tries: Optional[int] = None,
        timeout: Optional[int] = None,
    ) -> None:
        await self.sdk.validate_not_in_bootloader_mode()
        packet_version = self.sdk.get_packet_version()

        assert_condition(
            packet_version,
            DeviceCompatibilityError(
                DeviceCompatibilityErrorType.DEVICE_NOT_SUPPORTED,
            ),
        )

        return await legacy_operations.send_data(
            self.sdk.get_connection(),
            command,
            data,
            packet_version,
            max_tries,
            timeout,
        )

    async def receive_legacy_command(
        self, 
        commands: List[int], 
        timeout: Optional[int] = None
    ) -> Dict[str, Union[int, str]]:
        await self.sdk.validate_not_in_bootloader_mode()
        packet_version = self.sdk.get_packet_version()

        assert_condition(
            packet_version,
            DeviceCompatibilityError(
                DeviceCompatibilityErrorType.DEVICE_NOT_SUPPORTED,
            ),
        )

        return await legacy_operations.receive_data(
            self.sdk.get_connection(),
            commands,
            packet_version,
            timeout,
        )

    # ************** v3 Packet Version ****************
    async def send_command(self, params: Dict[str, Any]) -> None:
        await self.sdk.validate_not_in_bootloader_mode()
        packet_version = self.sdk.get_packet_version()

        assert_condition(
            packet_version,
            DeviceCompatibilityError(
                DeviceCompatibilityErrorType.DEVICE_NOT_SUPPORTED,
            ),
        )

        if not await self.is_raw_operation_supported():
            raise DeviceCompatibilityError(
                DeviceCompatibilityErrorType.INVALID_SDK_OPERATION,
            )

        max_tries = params.get("maxTries")
        if max_tries is None:
            max_tries = 5

        return await raw_operations.send_command(
            connection=self.sdk.get_connection(),
            data=params["data"],
            command_type=params["commandType"],
            sequence_number=params["sequenceNumber"],
            version=packet_version or PacketVersionMap.v3,
            max_tries=max_tries,
            timeout=params.get("timeout"),
        )

    async def get_command_output(
        self,
        sequence_number: int,
        max_tries: Optional[int] = None,
        timeout: Optional[int] = None,
    ):
        await self.sdk.validate_not_in_bootloader_mode()
        packet_version = self.sdk.get_packet_version()

        assert_condition(
            packet_version,
            DeviceCompatibilityError(
                DeviceCompatibilityErrorType.DEVICE_NOT_SUPPORTED,
            ),
        )

        if not await self.is_raw_operation_supported():
            raise DeviceCompatibilityError(
                DeviceCompatibilityErrorType.INVALID_SDK_OPERATION,
            )

        if max_tries is None:
            max_tries = 5

        return await raw_operations.get_command_output(
            connection=self.sdk.get_connection(),
            sequence_number=sequence_number,
            version=packet_version or PacketVersionMap.v3,
            max_tries=max_tries,
            timeout=timeout,
        )

    async def wait_for_command_output(self, params: Dict[str, Any]):
        await self.sdk.validate_not_in_bootloader_mode()
        packet_version = self.sdk.get_packet_version()

        assert_condition(
            packet_version,
            DeviceCompatibilityError(
                DeviceCompatibilityErrorType.DEVICE_NOT_SUPPORTED,
            ),
        )

        if not await self.is_raw_operation_supported():
            raise DeviceCompatibilityError(
                DeviceCompatibilityErrorType.INVALID_SDK_OPERATION,
            )

        return await raw_operations.wait_for_command_output(
            connection=self.sdk.get_connection(),
            version=packet_version or PacketVersionMap.v3,
            sequence_number=params["sequenceNumber"],
            expected_command_types=params["expectedCommandTypes"],
            on_status=params.get("onStatus"),
            options=params.get("options"),
        )

    async def get_command_status(
        self, 
        max_tries: Optional[int] = None, 
        timeout: Optional[int] = None
    ):
        await self.sdk.validate_not_in_bootloader_mode()
        packet_version = self.sdk.get_packet_version()

        assert_condition(
            packet_version,
            DeviceCompatibilityError(
                DeviceCompatibilityErrorType.DEVICE_NOT_SUPPORTED,
            ),
        )

        if not await self.is_raw_operation_supported():
            raise DeviceCompatibilityError(
                DeviceCompatibilityErrorType.INVALID_SDK_OPERATION,
            )

        if max_tries is None:
            max_tries = 5

        return await raw_operations.get_status(
            connection=self.sdk.get_connection(),
            version=packet_version or PacketVersionMap.v3,
            max_tries=max_tries,
            timeout=timeout,
        )

    async def send_command_abort(
        self,
        sequence_number: int,
        max_tries: Optional[int] = None,
        timeout: Optional[int] = None,
    ):
        await self.sdk.validate_not_in_bootloader_mode()
        packet_version = self.sdk.get_packet_version()

        assert_condition(
            packet_version,
            DeviceCompatibilityError(
                DeviceCompatibilityErrorType.DEVICE_NOT_SUPPORTED,
            ),
        )

        if not await self.is_raw_operation_supported():
            raise DeviceCompatibilityError(
                DeviceCompatibilityErrorType.INVALID_SDK_OPERATION,
            )

        if max_tries is None:
            max_tries = 2

        return await raw_operations.send_abort(
            connection=self.sdk.get_connection(),
            version=packet_version or PacketVersionMap.v3,
            sequence_number=sequence_number,
            max_tries=max_tries,
            timeout=timeout,
        )


__all__ = ["DeprecatedCommunication"]

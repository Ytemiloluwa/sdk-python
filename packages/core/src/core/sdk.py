from typing import Optional, Dict, Any, Callable, Awaitable, List
from interfaces import (
    DeviceBootloaderError,
    DeviceBootloaderErrorType,
    DeviceCommunicationError,
    DeviceCommunicationErrorType,
    DeviceCompatibilityError,
    DeviceCompatibilityErrorType,
    DeviceState,
    IDeviceConnection,
)
from util import assert_condition
from .utils.version_compare import compare_versions
from .operations import bootloader as bootloader_operations
from .operations import legacy as legacy_operations
from .operations import proto as operations
from . import commands
from .utils.sdk_version import get_packet_version_from_sdk, format_sdk_version
from .utils.packetversion import PacketVersion, PacketVersionMap
from .utils.feature_map import FeatureName, is_feature_enabled
from .types import IFeatureSupport, ISDK
from .deprecated import DeprecatedCommunication
from .encoders.proto.types import DeviceIdleState
from .encoders.raw.types import DeviceIdleState as RawDeviceIdleState
from .utils.logger import logger
from .encoders.proto.generated.core import AppVersionResultResponse
from interfaces.errors.app_error import DeviceAppError, DeviceAppErrorType


class SDK:
    def __init__(
        self,
        connection: IDeviceConnection,
        applet_id: int,
        version: str,
        packet_version: Optional[PacketVersion] = None,
    ):
        self.connection = connection
        self.version = version
        self.packet_version = packet_version
        self.applet_id = applet_id
        self.deprecated = DeprecatedCommunication(self)
        self.app_versions_map: Optional[AppVersionResultResponse] = None

    @classmethod
    async def create(
        cls,
        connection: IDeviceConnection,
        applet_id: int,
        options: Optional[Dict[str, Any]] = None,
    ) -> ISDK:
        max_tries = options.get("max_tries") if options else None
        timeout = options.get("timeout") if options else None
        
        sdk_data = await cls.get_sdk_version(connection, max_tries, timeout)
        return cls(
            connection,
            applet_id,
            sdk_data["sdkVersion"],
            sdk_data.get("packetVersion"),
        )

    def get_connection(self) -> IDeviceConnection:
        return self.connection

    def get_version(self) -> str:
        return self.version

    def get_packet_version(self) -> Optional[PacketVersion]:
        return self.packet_version

    async def is_supported(self) -> bool:
        if await self.get_device_state() == DeviceState.BOOTLOADER:
            return False

        return is_feature_enabled(FeatureName.ProtoCommand, self.get_version())

    async def get_sequence_number(self) -> int:
        return await self.connection.get_sequence_number()

    async def get_new_sequence_number(self) -> int:
        return await self.connection.get_new_sequence_number()

    async def before_operation(self) -> None:
        return await self.connection.before_operation()

    async def after_operation(self) -> None:
        return await self.connection.after_operation()

    def configure_applet_id(self, applet_id: int) -> None:
        self.applet_id = applet_id

    async def destroy(self) -> None:
        return await self.connection.destroy()

    async def is_in_bootloader(self) -> bool:
        return await self.get_device_state() == DeviceState.BOOTLOADER

    async def get_device_state(self) -> DeviceState:
        return await self.connection.get_device_state()

    # ************** v3 Packet Version with protobuf ****************
    async def send_query(
        self,
        data: bytes,
        options: Optional[Dict[str, Any]] = None,
    ) -> None:
        await self.validate_not_in_bootloader_mode()
        assert_condition(
            self.packet_version,
            DeviceCompatibilityError(
                DeviceCompatibilityErrorType.DEVICE_NOT_SUPPORTED,
            ),
        )

        if not await self.is_supported():
            raise DeviceCompatibilityError(
                DeviceCompatibilityErrorType.INVALID_SDK_OPERATION,
            )

        sequence_number = options.get("sequence_number") if options else None
        if sequence_number is None:
            sequence_number = await self.get_new_sequence_number()
            
        max_tries = options.get("max_tries") if options else None
        timeout = options.get("timeout") if options else None

        # Set defaults for None values
        if max_tries is None:
            max_tries = 5

        return await operations.send_query(
            connection=self.connection,
            data=data,
            applet_id=self.applet_id,
            sequence_number=sequence_number,
            version= PacketVersionMap.v3,
            max_tries=max_tries,
            timeout=timeout,
        )

    async def get_result(self, options: Optional[Dict[str, Any]] = None):
        await self.validate_not_in_bootloader_mode()
        assert_condition(
            self.packet_version,
            DeviceCompatibilityError(
                DeviceCompatibilityErrorType.DEVICE_NOT_SUPPORTED,
            ),
        )

        if not await self.is_supported():
            raise DeviceCompatibilityError(
                DeviceCompatibilityErrorType.INVALID_SDK_OPERATION,
            )

        sequence_number = options.get("sequence_number") if options else None
        if sequence_number is None:
            sequence_number = await self.get_sequence_number()
            
        max_tries = options.get("max_tries") if options else None
        timeout = options.get("timeout") if options else None

        # Set defaults for None values
        if max_tries is None:
            max_tries = 5

        return await operations.get_result(
            connection=self.connection,
            applet_id=self.applet_id,
            sequence_number=sequence_number,
            version = PacketVersionMap.v3,
            max_tries=max_tries,
            timeout=timeout,
        )

    async def wait_for_result(self, params: Optional[Dict[str, Any]] = None):
        await self.validate_not_in_bootloader_mode()
        assert_condition(
            self.packet_version,
            DeviceCompatibilityError(
                DeviceCompatibilityErrorType.DEVICE_NOT_SUPPORTED,
            ),
        )

        if not await self.is_supported():
            raise DeviceCompatibilityError(
                DeviceCompatibilityErrorType.INVALID_SDK_OPERATION,
            )

        sequence_number = params.get("sequence_number") if params else None
        if sequence_number is None:
            sequence_number = await self.get_sequence_number()
            
        on_status = params.get("on_status") if params else None
        options = params.get("options") if params else None

        return await operations.wait_for_result(
            connection=self.connection,
            version=self.packet_version or PacketVersionMap.v3,
            applet_id=self.applet_id,
            sequence_number=sequence_number,
            on_status=on_status,
            options=options,
        )

    async def get_status(
        self,
        max_tries: Optional[int] = None,
        timeout: Optional[int] = None,
        dont_log: Optional[bool] = None,
    ):
        await self.validate_not_in_bootloader_mode()
        assert_condition(
            self.packet_version,
            DeviceCompatibilityError(
                DeviceCompatibilityErrorType.DEVICE_NOT_SUPPORTED,
            ),
        )

        if not await self.is_supported():
            raise DeviceCompatibilityError(
                DeviceCompatibilityErrorType.INVALID_SDK_OPERATION,
            )

        # Set defaults for None values
        if max_tries is None:
            max_tries = 5
        if dont_log is None:
            dont_log = False

        return await operations.get_status(
            connection=self.connection,
            version = PacketVersionMap.v3,
            max_tries=max_tries,
            timeout=timeout,
            dont_log=dont_log,
        )

    async def send_abort(self, options: Optional[Dict[str, Any]] = None):
        await self.validate_not_in_bootloader_mode()
        assert_condition(
            self.packet_version,
            DeviceCompatibilityError(
                DeviceCompatibilityErrorType.DEVICE_NOT_SUPPORTED,
            ),
        )

        if not await self.is_supported():
            raise DeviceCompatibilityError(
                DeviceCompatibilityErrorType.INVALID_SDK_OPERATION,
            )

        sequence_number = options.get("sequence_number") if options else None
        if sequence_number is None:
            sequence_number = await self.get_new_sequence_number()
            
        max_tries = options.get("max_tries") if options else None
        timeout = options.get("timeout") if options else None

        # Set defaults for None values
        if max_tries is None:
            max_tries = 5

        return await operations.send_abort(
            connection=self.connection,
            sequence_number=sequence_number,
            version= PacketVersionMap.v3,
            max_tries=max_tries,
            timeout=timeout,
        )

    async def get_app_versions(
        self,
        on_status: Optional[Callable[[Any], None]] = None,
        options: Optional[Dict[str, Any]] = None,
    ):
        await self.validate_not_in_bootloader_mode()
        assert_condition(
            self.packet_version,
            DeviceCompatibilityError(
                DeviceCompatibilityErrorType.DEVICE_NOT_SUPPORTED,
            ),
        )

        if not await self.is_supported():
            raise DeviceCompatibilityError(
                DeviceCompatibilityErrorType.INVALID_SDK_OPERATION,
            )

        if not self.app_versions_map:
            result = await commands.get_app_versions(
                commands.GetAppVersionsParams(
                    connection=self.connection,
                    sequence_number=await self.get_new_sequence_number(),
                    on_status=on_status,
                    options=options,
                )
            )
            self.app_versions_map = result
            return result

        return self.app_versions_map

    async def get_app_version(self, app_id: int):
        await self.get_app_versions()
        if not self.app_versions_map or not self.app_versions_map.app_versions:
            return None
            
        for app in self.app_versions_map.app_versions:
            if app.id == app_id:
                return app.version
        return None

    async def check_feature_support_compatibility(self, features: List[IFeatureSupport]) -> None:
        app_version_result = await self.get_app_version(self.applet_id)

        if not app_version_result:
            return

        app_version = f"{app_version_result.major}.{app_version_result.minor}.{app_version_result.patch}"

        for feature in features:
            is_compatible = compare_versions(feature["from_version"], app_version) < 1
            if not is_compatible:
                logger.warn(
                    f"Feature {feature['name']} is supported only from >{feature['from_version']}, "
                    f"your current app version is {app_version}"
                )
                raise DeviceCompatibilityError(
                    DeviceCompatibilityErrorType.INVALID_SDK_OPERATION,
                )

    async def check_app_compatibility(
        self,
        version: Dict[str, str],
        options: Optional[Dict[str, Any]] = None,
    ) -> None:
        app_versions_result = await self.get_app_versions(None, options)
        
        app_version_result = None
        for app in app_versions_result.app_versions:
            if app.id == self.applet_id:
                app_version_result = app.version
                break

        if not app_version_result:
            return

        app_version = f"{app_version_result.major}.{app_version_result.minor}.{app_version_result.patch}"

        is_compatible = compare_versions(version["from"], app_version) < 1

        if version.get("to"):
            is_compatible = is_compatible and compare_versions(version["to"], app_version) > 0

        if not is_compatible:
            raise DeviceCompatibilityError(
                DeviceCompatibilityErrorType.INVALID_SDK_OPERATION,
            )

    # ************** Bootloader operations ****************
    async def send_bootloader_abort(self, options: Optional[Dict[str, Any]] = None) -> None:
        if not await self.is_in_bootloader():
            raise DeviceBootloaderError(
                DeviceBootloaderErrorType.NOT_IN_BOOTLOADER,
            )

        return await bootloader_operations.send_bootloader_abort(self.connection, options)

    async def send_bootloader_data(
        self,
        data: str,
        on_progress: Optional[Callable[[int], None]] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> None:
        if not await self.is_in_bootloader():
            raise DeviceBootloaderError(
                DeviceBootloaderErrorType.NOT_IN_BOOTLOADER,
            )

        return await bootloader_operations.send_bootloader_data(
            self.connection,
            data,
            on_progress,
            options,
        )

    async def make_device_ready(self) -> None:
        if await self.is_supported():
            await self.ensure_if_usb_idle()

            status = await self.get_status()
            if status.device_idle_state in [
                DeviceIdleState.DEVICE_IDLE_STATE_USB,
                DeviceIdleState.DEVICE_IDLE_STATE_DEVICE,
            ]:
                if status.abort_disabled:
                    raise DeviceAppError(DeviceAppErrorType.EXECUTING_OTHER_COMMAND)

                await self.send_abort()
        elif await self.deprecated.is_raw_operation_supported():
            status = await self.deprecated.get_command_status()
            if status.device_idle_state in [
                RawDeviceIdleState.DEVICE,
                RawDeviceIdleState.DEVICE,
            ]:
                if status.abort_disabled:
                    raise DeviceAppError(DeviceAppErrorType.EXECUTING_OTHER_COMMAND)

                await self.deprecated.send_command_abort(await self.get_sequence_number())

    async def run_operation(self, operation: Callable[[], Awaitable[Any]]) -> Any:
        try:
            await self.connection.before_operation()
            await self.make_device_ready()

            result = await operation()

            if await self.connection.is_connected():
                await self.connection.after_operation()

            return result
        except Exception as error:
            if await self.connection.is_connected():
                await self.connection.after_operation()

            raise error

    async def validate_not_in_bootloader_mode(self) -> None:
        if await self.is_in_bootloader():
            raise DeviceCommunicationError(
                DeviceCommunicationErrorType.IN_BOOTLOADER,
            )

    async def start_session(
        self,
        on_status: Optional[Callable[[Any], None]] = None,
        options: Optional[Dict[str, Any]] = None,
    ):
        await self.validate_not_in_bootloader_mode()
        assert_condition(
            self.packet_version,
            DeviceCompatibilityError(
                DeviceCompatibilityErrorType.DEVICE_NOT_SUPPORTED,
            ),
        )

        if not await self.is_supported():
            raise DeviceCompatibilityError(
                DeviceCompatibilityErrorType.INVALID_SDK_OPERATION,
            )

        return await commands.start_session(
            commands.StartSessionParams(
                connection=self.connection,
                get_new_sequence_number= self.get_new_sequence_number,
                get_sequence_number=self.get_sequence_number,
                on_status=on_status,
                options=options,
            )
        )

    async def close_session(
        self,
        on_status: Optional[Callable[[Any], None]] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> None:
        await self.validate_not_in_bootloader_mode()
        assert_condition(
            self.packet_version,
            DeviceCompatibilityError(
                DeviceCompatibilityErrorType.DEVICE_NOT_SUPPORTED,
            ),
        )

        if not await self.is_supported():
            raise DeviceCompatibilityError(
                DeviceCompatibilityErrorType.INVALID_SDK_OPERATION,
            )

        return await commands.close_session(
            commands.CloseSessionParams(
                connection=self.connection,
                get_new_sequence_number=self.get_new_sequence_number,
                get_sequence_number=self.get_sequence_number,
                on_status=on_status,
                options=options,
            )
        )

    async def ensure_if_usb_idle(self) -> None:
        try:
            if await self.is_supported():
                await operations.wait_for_idle(
                    connection=self.connection,
                    version = PacketVersionMap.v3,
                )
        except Exception as error:
            logger.warn("Error while checking for idle state")
            logger.warn(error)

    @staticmethod
    async def get_sdk_version(
        connection: IDeviceConnection,
        max_tries: Optional[int] = None,
        timeout: Optional[int] = None,
    ) -> Dict[str, Any]:
        assert_condition(connection, "Invalid connection")

        if await connection.get_device_state() == DeviceState.BOOTLOADER:
            return {"sdkVersion": "0.0.0"}

        retries = 0
        inner_max_tries = max_tries or 2
        first_error = DeviceCommunicationError(
            DeviceCommunicationErrorType.UNKNOWN_COMMUNICATION_ERROR,
        )

        await connection.before_operation()
        while retries < inner_max_tries:
            try:
                await legacy_operations.send_data(
                    connection,
                    88,
                    "00",
                    PacketVersionMap.v1,
                    inner_max_tries,
                )

                sdk_version_data = await legacy_operations.receive_data(
                    connection,
                    [88],
                    PacketVersionMap.v1,
                    timeout or 5000,
                )

                sdk_version = format_sdk_version(sdk_version_data["data"])
                packet_version = get_packet_version_from_sdk(sdk_version)

                await connection.after_operation()
                return {
                    "sdkVersion": sdk_version,
                    "packetVersion": packet_version,
                }
            except Exception as error:
                retries += 1
                first_error = error

        await connection.after_operation()
        raise first_error


__all__ = ["SDK"]

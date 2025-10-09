from typing import Protocol, TypedDict, List, Optional, Callable, Awaitable, Union, Any, Dict
from interfaces import DeviceState, IDeviceConnection
from .utils.packetversion import PacketVersion
from .encoders.raw.types import RawData, StatusData
from .encoders.proto.generated.core import AppVersionResultResponse
from .encoders.proto.generated.common import Version


class IDeprecatedCommunication(Protocol):
    async def is_legacy_operation_supported(self) -> bool:
        ...
    
    async def is_raw_operation_supported(self) -> bool:
        ...
    
    async def send_legacy_command(
        self,
        command: int,
        data: str,
        max_tries: Optional[int] = None,
        timeout: Optional[int] = None,
    ) -> None:
        ...
    
    async def receive_legacy_command(
        self,
        commands: List[int],
        timeout: Optional[int] = None,
    ) -> Dict[str, Union[int, str]]:
        ...
    
    async def send_command(self, params: Dict[str, Any]) -> None:
        ...
    
    async def get_command_output(
        self,
        sequence_number: int,
        max_tries: Optional[int] = None,
        timeout: Optional[int] = None,
    ) -> Union[StatusData, RawData]:
        ...
    
    async def wait_for_command_output(self, params: Dict[str, Any]) -> RawData:
        ...
    
    async def get_command_status(
        self,
        max_tries: Optional[int] = None,
        timeout: Optional[int] = None,
    ) -> StatusData:
        ...
    
    async def send_command_abort(
        self,
        sequence_number: int,
        max_tries: Optional[int] = None,
        timeout: Optional[int] = None,
    ) -> StatusData:
        ...


class IFeatureSupport(TypedDict):
    name: str
    from_version: str


class ISDK(Protocol):
    deprecated: IDeprecatedCommunication
    
    def get_connection(self) -> IDeviceConnection:
        ...
    
    def get_version(self) -> str:
        ...
    
    def get_packet_version(self) -> Optional[PacketVersion]:
        ...
    
    async def is_supported(self) -> bool:
        ...
    
    async def get_sequence_number(self) -> int:
        ...
    
    async def get_new_sequence_number(self) -> int:
        ...
    
    async def before_operation(self) -> None:
        ...
    
    async def after_operation(self) -> None:
        ...
    
    def configure_applet_id(self, applet_id: int) -> None:
        ...
    
    async def destroy(self) -> None:
        ...
    
    async def is_in_bootloader(self) -> bool:
        ...
    
    async def get_device_state(self) -> DeviceState:
        ...
    
    async def send_query(
        self,
        data: bytes,
        options: Optional[Dict[str, Any]] = None,
    ) -> None:
        ...
    
    async def get_result(
        self,
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        ...
    
    async def wait_for_result(
        self,
        params: Optional[Dict[str, Any]] = None,
    ) -> bytes:
        ...
    
    async def get_status(
        self,
        max_tries: Optional[int] = None,
        timeout: Optional[int] = None,
        dont_log: Optional[bool] = None,
    ) -> Any:  # Status from proto types
        ...
    
    async def send_abort(
        self,
        options: Optional[Dict[str, Any]] = None,
    ) -> Any:  # Status from proto types
        ...
    
    async def get_app_versions(
        self,
        on_status: Optional[Callable[[Any], None]] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> AppVersionResultResponse:
        ...
    
    async def get_app_version(self, app_id: int) -> Optional[Version]:
        ...
    
    async def check_app_compatibility(
        self,
        version: Dict[str, str],
        options: Optional[Dict[str, Any]] = None,
    ) -> None:
        ...
    
    async def check_feature_support_compatibility(
        self,
        features: List[IFeatureSupport],
    ) -> None:
        ...
    
    async def send_bootloader_abort(
        self,
        options: Optional[Dict[str, Any]] = None,
    ) -> None:
        ...
    
    async def send_bootloader_data(
        self,
        data: str,
        on_progress: Optional[Callable[[int], None]] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> None:
        ...
    
    async def run_operation(self, operation: Callable[[], Awaitable[Any]]) -> Any:
        ...
    
    async def validate_not_in_bootloader_mode(self) -> None:
        ...
    
    async def start_session(
        self,
        on_status: Optional[Callable[[Any], None]] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        ...
    
    async def close_session(
        self,
        on_status: Optional[Callable[[Any], None]] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> None:
        ...


__all__ = [
    "IDeprecatedCommunication",
    "IFeatureSupport", 
    "ISDK",
]

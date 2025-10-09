from typing import Optional, Callable, Dict, Any
from interfaces import IDeviceConnection
from ..encoders.proto.generated.core import Msg, AppVersionCmd, AppVersionRequest, AppVersionIntiateRequest
from ..operations.helpers.sendcommand import send_command
from ..operations.proto import wait_for_result
from ..utils.packetversion import PacketVersionMap
from ..utils.common_error import assert_or_throw_invalid_result, parse_common_error
from util.utils.assert_utils import assert_condition
from util.utils.crypto import uint8array_to_hex
from interfaces.errors.app_error import DeviceAppError, DeviceAppErrorType


class GetAppVersionsParams:
    def __init__(
        self,
        connection: IDeviceConnection,
        sequence_number: int,
        on_status: Optional[Callable[[Any], None]] = None,
        options: Optional[Dict[str, Any]] = None,
    ):
        self.connection = connection
        self.sequence_number = sequence_number
        self.on_status = on_status
        self.options = options or {}


async def get_app_versions(params: GetAppVersionsParams):
    assert_condition(params.connection, 'Invalid connection')
    assert_condition(params.sequence_number, 'Invalid sequenceNumber')
    max_tries = params.options.get('maxTries')
    timeout = params.options.get('timeout')
    version = PacketVersionMap.v3
    msg = Msg(
        app_version=AppVersionCmd(
            request=AppVersionRequest(
                initiate=AppVersionIntiateRequest()
            )
        )
    )
    msg_data = uint8array_to_hex(bytes(msg))
    await send_command(
        connection=params.connection,
        proto_data=msg_data,
        raw_data='',
        version=version,
        max_tries=max_tries,
        sequence_number=params.sequence_number,
        timeout=timeout,
    )
    result = await wait_for_result(
        connection=params.connection,
        applet_id=0,
        sequence_number=params.sequence_number,
        version=version,
        allow_core_data=True,
        on_status=params.on_status,
        options=params.options,
    )
    try:
        msg = Msg.parse(result)
    except TypeError:
        try:
            msg = Msg().parse(result)
        except Exception:
            raise DeviceAppError(DeviceAppErrorType.INVALID_MSG_FROM_DEVICE)
    except Exception:
        raise DeviceAppError(DeviceAppErrorType.INVALID_MSG_FROM_DEVICE)
    response = msg.app_version.response if msg.app_version and msg.app_version.response else None
    assert_or_throw_invalid_result(response)
    if response.common_error:
        parse_common_error(response.common_error)
    assert_or_throw_invalid_result(getattr(response, 'result', None))
    return getattr(response, 'result', None)

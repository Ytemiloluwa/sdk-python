from typing import Optional, Callable, Dict, Any, Awaitable
from packages.interfaces import IDeviceConnection
from packages.core.src.encoders.proto.generated.core import (
    Msg, SessionCloseCmd, SessionCloseRequest, SessionCloseClearRequest, SessionCloseResponse
)
from packages.core.src.operations.helpers.sendcommand import send_command
from packages.core.src.operations.proto import wait_for_result
from packages.core.src.utils.packetversion import PacketVersionMap
from packages.core.src.utils.common_error import assert_or_throw_invalid_result, parse_common_error
from packages.util.utils.assert_utils import assert_condition
from packages.util.utils.crypto import uint8array_to_hex
from packages.interfaces.errors.app_error import DeviceAppError, DeviceAppErrorType


class CloseSessionParams:
    def __init__(
        self,
        connection: IDeviceConnection,
        get_sequence_number: Callable[[], Awaitable[int]],
        get_new_sequence_number: Callable[[], Awaitable[int]],
        on_status: Optional[Callable[[Any], None]] = None,
        options: Optional[Dict[str, Any]] = None,
    ):
        self.connection = connection
        self.get_sequence_number = get_sequence_number
        self.get_new_sequence_number = get_new_sequence_number
        self.on_status = on_status
        self.options = options or {}


def build_session_close_msg() -> Msg:
    return Msg(
        session_close=SessionCloseCmd(
            request=SessionCloseRequest(
                clear=SessionCloseClearRequest()
            )
        )
    )


async def send_session_command(params: CloseSessionParams):
    max_tries = params.options.get('maxTries')
    timeout = params.options.get('timeout')
    msg = build_session_close_msg()
    msg_data = uint8array_to_hex(bytes(msg))
    await send_command(
        connection=params.connection,
        proto_data=msg_data,
        raw_data='',
        version=PacketVersionMap.v3,
        max_tries=max_tries,
        sequence_number=await params.get_new_sequence_number(),
        timeout=timeout,
    )


async def wait_for_session_result(params: CloseSessionParams) -> SessionCloseResponse:
    version = PacketVersionMap.v3
    result = await wait_for_result(
        connection=params.connection,
        applet_id=0,
        sequence_number=await params.get_sequence_number(),
        version=version,
        allow_core_data=True,
        on_status=params.on_status,
        options=params.options,
    )
    try:
        msg = Msg.parse(result)
    except Exception:
        raise DeviceAppError(DeviceAppErrorType.INVALID_MSG_FROM_DEVICE)
    response = msg.session_close.response if msg.session_close and msg.session_close.response else None
    assert_or_throw_invalid_result(response)
    if response.common_error:
        parse_common_error(response.common_error)
    return response


async def close_session(params: CloseSessionParams) -> None:
    assert_condition(params.connection, 'Invalid connection')
    assert_condition(params.get_new_sequence_number, 'Invalid getNewSequenceNumber')
    await send_session_command(params)
    result = await wait_for_session_result(params)
    clear = getattr(result, 'clear', None)
    assert_or_throw_invalid_result(clear)



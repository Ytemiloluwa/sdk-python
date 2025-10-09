from typing import Optional, Callable, Dict, Any, Awaitable
from interfaces import IDeviceConnection
from ..encoders.proto.generated.core import (
    Msg,
    SessionStartCmd,
    SessionStartRequest,
    SessionStartInitiateRequest,
    SessionStartBeginRequest,
    SessionStartResponse,
)
from ..operations.helpers.sendcommand import send_command
from ..operations.proto import wait_for_result
from ..services import initiate_server_session
from ..utils.packetversion import PacketVersionMap
from ..utils.common_error import assert_or_throw_invalid_result, parse_common_error
from util.utils.assert_utils import assert_condition
from util.utils.crypto import hex_to_uint8array, uint8array_to_hex
from interfaces.errors.app_error import DeviceAppError, DeviceAppErrorType


class StartSessionParams:
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


def build_session_start_msg(data: dict) -> Msg:
    if "request" in data and "initiate" in data["request"]:
        return Msg(
            session_start=SessionStartCmd(
                request=SessionStartRequest(initiate=SessionStartInitiateRequest())
            )
        )
    elif "request" in data and "start" in data["request"]:
        start = data["request"]["start"]
        return Msg(
            session_start=SessionStartCmd(
                request=SessionStartRequest(
                    start=SessionStartBeginRequest(
                        session_random_public=start["session_random_public"],
                        session_age=start["session_age"],
                        signature=start["signature"],
                        device_id=start["device_id"],
                    )
                )
            )
        )
    else:
        raise ValueError("Invalid session start data structure")


async def send_session_command(params: StartSessionParams, data: dict):
    max_tries = params.options.get("maxTries")
    timeout = params.options.get("timeout")
    msg = build_session_start_msg(data)
    msg_data = uint8array_to_hex(bytes(msg))
    await send_command(
        connection=params.connection,
        proto_data=msg_data,
        raw_data="",
        version=PacketVersionMap.v3,
        max_tries=max_tries,
        sequence_number=await params.get_new_sequence_number(),
        timeout=timeout,
    )


async def wait_for_session_result(params: StartSessionParams) -> SessionStartResponse:
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
    response = (
        msg.session_start.response
        if msg.session_start and msg.session_start.response
        else None
    )
    assert_or_throw_invalid_result(response)
    if response.common_error:
        parse_common_error(response.common_error)
    return response


async def start_session(params: StartSessionParams) -> Dict[str, Any]:
    assert_condition(params.connection, "Invalid connection")
    assert_condition(params.get_new_sequence_number, "Invalid getNewSequenceNumber")
    await send_session_command(
        params,
        {
            "request": {
                "initiate": {},
            },
        },
    )
    result = await wait_for_session_result(params)
    confirmation_initiate = getattr(result, "confirmation_initiate", None)
    assert_or_throw_invalid_result(confirmation_initiate)
    server_initiate_response = await initiate_server_session(confirmation_initiate)
    await send_session_command(
        params,
        {
            "request": {
                "start": {
                    "session_random_public": hex_to_uint8array(
                        server_initiate_response.get("publicKey", "")
                    ),
                    "session_age": server_initiate_response["sessionAge"],
                    "signature": hex_to_uint8array(
                        server_initiate_response.get("signature", "")
                    ),
                    "device_id": confirmation_initiate.deviceId,
                },
            },
        },
    )
    result2 = await wait_for_session_result(params)
    confirmation_start = getattr(result2, "confirmation_start", None)
    assert_or_throw_invalid_result(confirmation_start)
    assert_condition(
        server_initiate_response.get("sessionId"), "Invalid session ID from server"
    )
    assert_condition(
        server_initiate_response.get("sessionAge"), "Invalid session age from server"
    )
    return {
        "sessionId": server_initiate_response["sessionId"],
        "sessionAge": server_initiate_response["sessionAge"],
    }

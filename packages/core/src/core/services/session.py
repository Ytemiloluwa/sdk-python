from util.utils.crypto import uint8array_to_hex
from ..utils.http import http
from .types import IInitiateServerSessionParams, IInitiateServerSessionResult

BASE_URL = "/inheritance/device-session"


async def initiate_server_session(
    params: IInitiateServerSessionParams,
) -> IInitiateServerSessionResult:
    """
    Initiate a server session with the provided parameters.

    Args:
        params: Session initiation parameters containing device information

    Returns:
        IInitiateServerSessionResult: Server session result data
    """
    body = {
        "deviceId": uint8array_to_hex(params["deviceId"]),
        "deviceRandomPublic": uint8array_to_hex(params["deviceRandomPublic"]),
        "signature": uint8array_to_hex(params["signature"]),
        "postfix1": uint8array_to_hex(params["postfix1"]),
        "postfix2": uint8array_to_hex(params["postfix2"]),
        "keyIndex": params["keyIndex"],
    }

    res = await http.post(f"{BASE_URL}/create", body)

    print({"res": res})
    return res["data"]


__all__ = [
    "initiate_server_session",
]

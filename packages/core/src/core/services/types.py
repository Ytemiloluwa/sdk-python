from typing import TypedDict, Optional

class IInitiateServerSessionParams(TypedDict):
    deviceRandomPublic: bytes
    deviceId: bytes
    signature: bytes
    postfix1: bytes
    postfix2: bytes
    keyIndex: int


class IInitiateServerSessionResult(TypedDict, total=False):
    publicKey: Optional[str]
    sessionAge: Optional[int]
    signature: Optional[str]
    sessionId: Optional[str]


__all__ = [
    "IInitiateServerSessionParams",
    "IInitiateServerSessionResult",
]
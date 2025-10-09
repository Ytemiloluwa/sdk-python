from typing import Optional, Dict, Any
from util.utils.crypto import sha256
from ..services.authverification import (
    verify_serial_signature,
    verify_challenge_signature,
)


async def verify_card_serial_signature(params: Dict[str, Any]) -> Optional[bytes]:
    """
    Verify card serial signature with SHA256 message.

    Args:
        params: Dictionary containing:
            - serial: bytes
            - signature: bytes

    Returns:
        bytes if verified, None otherwise
    """
    return await verify_serial_signature(
        {**params, "message": await sha256(params["serial"])}
    )


async def verify_card_challenge_signature(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Verify card challenge signature with firmware version 0.0.0.

    Args:
        params: Dictionary containing:
            - serial: bytes
            - signature: bytes
            - challenge: bytes
            - email: Optional[str]
            - cysyncVersion: Optional[str]
            - onlyFailure: Optional[bool]
            - sessionId: Optional[str]

    Returns:
        Dictionary with isVerified and sessionId
    """
    return await verify_challenge_signature({**params, "firmwareVersion": "0.0.0"})

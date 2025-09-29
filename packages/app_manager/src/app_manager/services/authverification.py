from typing import Optional, Dict, Any
from packages.app_manager.src.utils import http
from packages.util.utils.crypto import hex_to_uint8array, uint8array_to_hex

BASE_URL = "/verification"


async def verify_serial_signature(params: Dict[str, Any]) -> Optional[bytes]:
    """
    Verify serial signature and return challenge if verified.
    
    Args:
        params: Dictionary containing:
            - serial: bytes
            - signature: bytes
            - postfix1: Optional[bytes]
            - postfix2: Optional[bytes]
            - message: Optional[bytes]
    
    Returns:
        bytes if verified, None otherwise
    """
    verify_params = {
        "serial": uint8array_to_hex(params["serial"]),
        "signature": uint8array_to_hex(params["signature"]),
        "postfix1": uint8array_to_hex(params["postfix1"]) if params.get("postfix1") else None,
        "postfix2": uint8array_to_hex(params["postfix2"]) if params.get("postfix2") else None,
    }
    
    # Only add message if it's provided (since it's not in the test fixtures)
    if params.get("message"):
        verify_params["message"] = uint8array_to_hex(params["message"])
    
    res = await http.post(f"{BASE_URL}/verify", verify_params)
    
    if res.get("data", {}).get("verified") is True:
        return hex_to_uint8array(res["data"]["challenge"])
    
    return None


async def verify_challenge_signature(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Verify challenge signature.
    
    Args:
        params: Dictionary containing:
            - serial: bytes
            - signature: bytes
            - postfix1: Optional[bytes]
            - postfix2: Optional[bytes]
            - challenge: bytes
            - firmwareVersion: str
            - isTestApp: Optional[bool]
            - email: Optional[str]
            - cysyncVersion: Optional[str]
            - sessionId: Optional[str]
            - onlyFailure: Optional[bool]
    
    Returns:
        Dictionary with isVerified and sessionId
    """
    verify_params = {
        "serial": uint8array_to_hex(params["serial"]),
        "signature": uint8array_to_hex(params["signature"]),
        "postfix1": uint8array_to_hex(params["postfix1"]) if params.get("postfix1") else None,
        "postfix2": uint8array_to_hex(params["postfix2"]) if params.get("postfix2") else None,
        "challenge": uint8array_to_hex(params["challenge"]),
        "firmwareVersion": params["firmwareVersion"],
    }
    
    # Only add optional parameters if they are provided
    if "isTestApp" in params:
        verify_params["isTestApp"] = params["isTestApp"]
    if params.get("email"):
        verify_params["email"] = params["email"]
    if params.get("cysyncVersion"):
        verify_params["cysyncVersion"] = params["cysyncVersion"]
    if params.get("sessionId"):
        verify_params["sessionId"] = params["sessionId"]
    if "onlyFailure" in params:
        verify_params["onlyFailure"] = params["onlyFailure"]
    
    res = await http.post(f"{BASE_URL}/challenge", verify_params)
    
    return {
        "isVerified": res.get("data", {}).get("verified", False),
        "sessionId": res.get("data", {}).get("sessionId"),
    }

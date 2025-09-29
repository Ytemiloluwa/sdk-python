from typing import Optional
from dataclasses import dataclass
from packages.app_manager.src.utils import http, download_file
from packages.util.utils.queryString import create_query_string
BASE_URL = "/firmware-stm"


@dataclass
class GetLatestFirmwareOptions:
    prerelease: Optional[bool] = None
    do_download: Optional[bool] = None


@dataclass
class LatestFirmware:
    version: str
    firmware: Optional[bytes] = None


async def get_latest(params: Optional[GetLatestFirmwareOptions] = None) -> LatestFirmware:
    """
    Get the latest firmware version and optionally download it.
    
    Args:
        params: Options for getting latest firmware
    
    Returns:
        LatestFirmware object with version and optional firmware data
    
    Raises:
        Exception: If no latest firmware is found
    """
    if params is None:
        params = GetLatestFirmwareOptions()
    
    query_params = {}
    if params.prerelease is not None:
        query_params["prerelease"] = params.prerelease
    
    query_string = create_query_string(query_params)
    url = f"{BASE_URL}/latest"
    if query_string:
        url += f"?{query_string}"
    
    response = await http.get(url)
    
    if not response.get("data", {}).get("firmware"):
        raise Exception("No latest firmware found")
    
    result = LatestFirmware(
        version=response["data"]["firmware"]["version"]
    )
    
    if params.do_download:
        result.firmware = await download_file(response["data"]["firmware"]["downloadUrl"])
    
    return result




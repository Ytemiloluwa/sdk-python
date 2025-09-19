from typing import Optional
from packages.interfaces import IDeviceConnection
from packages.util.utils.crypto import hex_to_uint8array
from packages.core.src.utils.logger import logger
from packages.core.src.utils.packetversion import PacketVersion
from packages.core.src.operations.helpers.getstatus import get_status as get_status_helper
from packages.core.src.encoders.proto.generated.core import Status


async def get_status(
    connection: IDeviceConnection,
    version: PacketVersion,
    max_tries: int = 5,
    timeout: Optional[int] = None,
    dont_log: bool = False,
) -> Status:
    result = await get_status_helper(
        connection=connection,
        version=version,
        max_tries=max_tries,
        timeout=timeout,
    )
    
    protobuf_data = result["protobuf_data"]
    # Some betterproto versions expose parse as an instance method
    try:
        status = Status.parse(hex_to_uint8array(protobuf_data))
    except TypeError:
        status = Status().parse(hex_to_uint8array(protobuf_data))
    
    if not dont_log:
        try:
            meta = {'status': status.to_dict()}
        except Exception:
            meta = {'status': str(status)}
        logger.debug('Received status', meta)
    
    return status

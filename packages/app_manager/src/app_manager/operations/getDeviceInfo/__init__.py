from packages.core.src.types import ISDK
from packages.util.utils import create_logger_with_prefix
from packages.app_manager.src.constants.appId import APP_VERSION
from packages.app_manager.src.proto.generated.manager import GetDeviceInfoResultResponse
from packages.app_manager.src.utils import assert_or_throw_invalid_result, OperationHelper
from packages.app_manager.src.utils import logger as rootlogger

logger = create_logger_with_prefix(rootlogger, "GetDeviceInfo")

async def get_device_info(sdk: ISDK) -> GetDeviceInfoResultResponse:
    logger.info('Started')
    await sdk.check_app_compatibility(APP_VERSION)

    helper = OperationHelper(sdk, 'getDeviceInfo', 'getDeviceInfo')

    await helper.send_query({"initiate": {}})
    result = await helper.wait_for_result()
    logger.verbose('GetDeviceInfoResponse', {"result": result})
    assert_or_throw_invalid_result(result.result)

    logger.info('Completed')
    return result.result

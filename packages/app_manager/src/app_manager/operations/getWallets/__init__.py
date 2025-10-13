from core.types import ISDK
from util.utils import create_logger_with_prefix
from app_manager.constants.appId import APP_VERSION
from app_manager.proto.generated.manager import GetWalletsResultResponse
from ...utils import assert_or_throw_invalid_result, OperationHelper
from ...utils import logger as rootlogger

logger = create_logger_with_prefix(rootlogger, "GetWallets")


async def get_wallets(sdk: ISDK) -> GetWalletsResultResponse:
    logger.info("Started")

    await sdk.check_app_compatibility(APP_VERSION)

    helper = OperationHelper(sdk, "getWallets", "getWallets")

    await helper.send_query({"initiate": {}})
    result = await helper.wait_for_result()
    logger.verbose("GetWalletsResponse", result)
    assert_or_throw_invalid_result(result.result)

    logger.info("Completed")
    return result.result

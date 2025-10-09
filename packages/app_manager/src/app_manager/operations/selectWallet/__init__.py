from core.types import ISDK
from util.utils import create_logger_with_prefix
from app_manager.constants.appId import APP_VERSION
from app_manager.proto.generated.manager import SelectWalletResultResponse
from ...utils import assert_or_throw_invalid_result, OperationHelper
from ...utils import logger as rootlogger

logger = create_logger_with_prefix(rootlogger, 'SelectWallet')


async def select_wallet(sdk: ISDK) -> SelectWalletResultResponse:
    logger.info('Started')

    await sdk.check_app_compatibility(APP_VERSION)

    helper = OperationHelper(sdk, 'selectWallet', 'selectWallet')

    await helper.send_query({"initiate": {}})
    result = await helper.wait_for_result()
    logger.verbose('SelectWalletResponse', result)
    assert_or_throw_invalid_result(result.result)

    logger.info('Completed')
    return result.result


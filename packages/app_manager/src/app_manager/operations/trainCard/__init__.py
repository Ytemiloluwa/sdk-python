from packages.core.src.types import ISDK
from packages.util.utils import create_logger_with_prefix, create_status_listener
from packages.app_manager.src.constants.appId import APP_VERSION
from packages.app_manager.src.proto.generated.manager import TrainCardResult, TrainCardStatus
from packages.app_manager.src.utils import assert_or_throw_invalid_result, OperationHelper
from packages.app_manager.src.utils import logger as rootlogger
from .types import ITrainCardParams, TrainCardEventHandler

# Re-export types
__all__ = ['train_card', 'ITrainCardParams', 'TrainCardEventHandler']

logger = create_logger_with_prefix(rootlogger, 'TrainCard')


async def train_card(
    sdk: ISDK,
    params: ITrainCardParams,
) -> TrainCardResult:
    logger.info('Started')

    await sdk.check_app_compatibility(APP_VERSION)

    helper = OperationHelper(sdk, 'trainCard', 'trainCard')

    on_status, force_status_update = create_status_listener({
        'enums': TrainCardStatus,
        'onEvent': params.onEvent,
        'logger': logger,
    })

    await helper.send_query({"initiate": {}})
    result = await helper.wait_for_result(on_status)
    logger.verbose('TrainCardResponse', {"result": result})
    assert_or_throw_invalid_result(result.result)

    force_status_update(TrainCardStatus.TRAIN_CARD_STATUS_CARD_TAPPED)

    if len(result.result.walletList) > 0:
        is_self_created = await params.onWallets(result.result)

        await helper.send_query({"walletVerify": {"selfCreated": is_self_created}})

        flow_complete = await helper.wait_for_result(on_status)
        logger.verbose('TrainCardResponse', {"result": result})
        assert_or_throw_invalid_result(flow_complete.flowComplete)

    logger.info('Completed')
    return result.result

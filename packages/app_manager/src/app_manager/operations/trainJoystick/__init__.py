from typing import Optional
from core.types import ISDK
from util.utils import create_logger_with_prefix, create_status_listener
from app_manager.constants.appId import APP_VERSION
from app_manager.proto.generated.types import TrainJoystickStatus
from ...utils import assert_or_throw_invalid_result, OperationHelper
from ...utils import logger as rootlogger
from .types import TrainJoystickEventHandler

# Re-export types
__all__ = ['train_joystick', 'TrainJoystickEventHandler']

logger = create_logger_with_prefix(rootlogger, 'TrainJoystick')


async def train_joystick(
    sdk: ISDK,
    on_event: Optional[TrainJoystickEventHandler] = None,
) -> None:
    logger.info('Started')

    await sdk.check_app_compatibility(APP_VERSION)

    helper = OperationHelper(sdk, 'trainJoystick', 'trainJoystick')

    on_status, force_status_update = create_status_listener({
        'enums': TrainJoystickStatus,
        'onEvent': on_event,
        'logger': logger,
    })

    await helper.send_query({"initiate": {}})
    result = await helper.wait_for_result(on_status)
    logger.verbose('TrainJoystickResponse', {"result": result})
    assert_or_throw_invalid_result(result.result)

    force_status_update(TrainJoystickStatus.TRAIN_JOYSTICK_CENTER)
    logger.info('Completed')

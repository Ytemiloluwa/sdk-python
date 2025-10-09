from typing import Optional
from core.types import ISDK
from util.utils import create_logger_with_prefix, create_status_listener
from ...constants.appId import APP_VERSION
from ...proto.generated.manager import GetLogsStatus, GetLogsErrorResponse
from ...utils import assert_or_throw_invalid_result, OperationHelper
from ...utils import logger as rootlogger
from .types import GetLogsError, GetLogsErrorType, GetLogsEventHandler

__all__ = ['get_logs', 'GetLogsError', 'GetLogsErrorType', 'GetLogsEventHandler']

logger = create_logger_with_prefix(rootlogger, 'GetLogs')


def parse_get_logs_error(error: Optional[GetLogsErrorResponse]) -> None:
    if error is None:
        return

    error_types_map = {
        'logsDisabled': GetLogsErrorType.LOGS_DISABLED,
    }

    for key, error_type in error_types_map.items():
        if hasattr(error, key) and getattr(error, key):
            raise GetLogsError(error_type)


async def fetch_logs_data(helper: OperationHelper, on_status) -> str:
    result = await helper.wait_for_result(on_status)

    parse_get_logs_error(result.error)
    assert_or_throw_invalid_result(result.logs)

    return result.logs


async def get_logs(
    sdk: ISDK,
    on_event: Optional[GetLogsEventHandler] = None,
) -> str:
    logger.info('Started')
    helper = OperationHelper(sdk, 'getLogs', 'getLogs')

    await sdk.check_app_compatibility(APP_VERSION)

    on_status, force_status_update = create_status_listener({
        'enums': GetLogsStatus,
        'onEvent': on_event,
        'logger': logger,
    })

    # ASCII decoder for log data
    def decode_ascii(data: bytes) -> str:
        return data.decode('ascii', errors='replace')

    all_logs: list[str] = []
    is_confirmed = False
    has_more = False

    await helper.send_query({"initiate": {}})

    while True:
        result = await fetch_logs_data(helper, on_status)

        if not is_confirmed:
            force_status_update(GetLogsStatus.GET_LOGS_STATUS_USER_CONFIRMED)

        is_confirmed = True
        has_more = result.hasMore

        all_logs.append(decode_ascii(result.data))

        if has_more:
            await helper.send_query({"fetchNext": {}})
        else:
            break

    logger.info('Completed')
    return ''.join(all_logs)


from interfaces.logger import ILogger, LogCreator
from util.utils.logger import (
    create_default_console_logger,
    update_logger_object,
)

logger_service_name = "sdk-app-btc"

logger: ILogger = create_default_console_logger(logger_service_name)


def update_logger(create_logger: LogCreator) -> None:
    """
    Update the logger for the BTC app.

    Args:
        create_logger: Function to create a new logger
    """
    from core.utils.logger import update_logger as update_logger_core

    update_logger_core(create_logger)
    update_logger_object(
        {
            "current_logger": logger,
            "new_logger": create_logger(logger_service_name),
        }
    )

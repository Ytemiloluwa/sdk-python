from interfaces.logger import ILogger, LogCreator
from util.utils.logger import (
    create_default_console_logger,
    update_logger_object,
)

# Logger service name constant
logger_service_name = "sdk-hw-webusb"

# Create the default logger
logger: ILogger = create_default_console_logger(logger_service_name)


def update_logger(create_logger: LogCreator) -> None:
    update_logger_object(
        {"currentLogger": logger, "newLogger": create_logger(logger_service_name)}
    )

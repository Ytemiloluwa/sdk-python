from interfaces.logger import ILogger, LogCreator
from util.utils.logger import create_default_console_logger, update_logger_object

logger_service_name = "sdk-app-manager"
logger: ILogger = create_default_console_logger(logger_service_name)

def update_logger(create_logger: LogCreator) -> None:
    update_logger_object({
        "current_logger":logger,
        "new_logger":create_logger(logger_service_name)
    })
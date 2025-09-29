from typing import Callable
from packages.app_manager.src.proto.generated.types import GetLogsStatus
from .error import GetLogsError, GetLogsErrorType

# Re-export error types
__all__ = ['GetLogsError', 'GetLogsErrorType', 'GetLogsEventHandler']

GetLogsEventHandler = Callable[[GetLogsStatus], None]

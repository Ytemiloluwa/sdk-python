from typing import Callable
from app_manager.proto.generated.types import GetLogsStatus
from .error import GetLogsError, GetLogsErrorType

# Re-export error types
__all__ = ['GetLogsError', 'GetLogsErrorType', 'GetLogsEventHandler']

GetLogsEventHandler = Callable[[GetLogsStatus], None]

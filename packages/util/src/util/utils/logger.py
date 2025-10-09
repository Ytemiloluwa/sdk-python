from typing import Any, Dict, Optional, cast
import datetime
from interfaces.logger import ILogger, LogLevel
from .config import config

log_level_priority = {"error": 0, "warn": 1, "info": 2, "verbose": 3, "debug": 4}


def do_log(level: LogLevel) -> bool:
    current_priority = log_level_priority.get(level)
    allowed_priority = log_level_priority.get(config.get("LOG_LEVEL", "info"), 2)

    if current_priority is None:
        return False
    return allowed_priority >= current_priority


def create_default_meta(
    service: str, meta: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    result = {"service": service, "timestamp": datetime.datetime.now().isoformat()}
    if meta is not None:
        result.update(meta)
    return result


class DefaultConsoleLogger:
    def __init__(self, service: str):
        self._service = service

    def _log(
        self, level: LogLevel, message: Any, meta: Optional[Dict[str, Any]] = None
    ):
        if do_log(level):
            print(
                f"{level.upper()}: {message} {create_default_meta(self._service, meta)}"
            )

    def info(self, message: Any, meta: Optional[Dict[str, Any]] = None) -> None:
        self._log("info", message, meta)

    def debug(self, message: Any, meta: Optional[Dict[str, Any]] = None) -> None:
        self._log("debug", message, meta)

    def verbose(self, message: Any, meta: Optional[Dict[str, Any]] = None) -> None:
        self._log("verbose", message, meta)

    def warn(self, message: Any, meta: Optional[Dict[str, Any]] = None) -> None:
        self._log("warn", message, meta)

    def error(self, message: Any, meta: Optional[Dict[str, Any]] = None) -> None:
        self._log("error", message, meta)


def create_default_console_logger(service: str) -> ILogger:
    return DefaultConsoleLogger(service)


def update_logger_object(params: Dict[str, Any]) -> None:
    new_logger = cast(ILogger, params.get("newLogger"))
    current_logger = cast(ILogger, params.get("currentLogger"))

    if not (new_logger and current_logger):
        return

    for key in ("info", "error", "warn", "debug", "verbose"):
        new_method = getattr(new_logger, key, None)
        if callable(new_method):

            def create_wrapper(method_to_call):
                def wrapper(
                    message: Any, meta: Optional[Dict[str, Any]] = None
                ) -> None:
                    new_message = (
                        message.to_json() if hasattr(message, "to_json") else message
                    )
                    new_meta = meta.to_json() if hasattr(meta, "to_json") else meta
                    method_to_call(new_message, new_meta)

                return wrapper

            setattr(current_logger, key, create_wrapper(new_method))


class PrefixedLogger:
    def __init__(self, original_logger: ILogger, prefix: str):
        self._logger = original_logger
        self._prefix = prefix

    def _call_original(
        self, level: LogLevel, message: Any, meta: Optional[Dict[str, Any]] = None
    ):
        new_meta = meta or {}
        new_meta["component"] = self._prefix

        original_method = getattr(self._logger, level)
        if isinstance(message, str):
            original_method(f"{self._prefix}: {message}", new_meta)
        else:
            original_method(message, new_meta)

    def info(self, message: Any, meta: Optional[Dict[str, Any]] = None) -> None:
        self._call_original("info", message, meta)

    def debug(self, message: Any, meta: Optional[Dict[str, Any]] = None) -> None:
        self._call_original("debug", message, meta)

    def warn(self, message: Any, meta: Optional[Dict[str, Any]] = None) -> None:
        self._call_original("warn", message, meta)

    def error(self, message: Any, meta: Optional[Dict[str, Any]] = None) -> None:
        self._call_original("error", message, meta)

    def verbose(self, message: Any, meta: Optional[Dict[str, Any]] = None) -> None:
        self._call_original("verbose", message, meta)


def create_logger_with_prefix(logger: ILogger, name: str) -> ILogger:
    return PrefixedLogger(logger, name)

from typing import Any, Callable, Dict, Protocol, TypeVar, Union, runtime_checkable, overload
@runtime_checkable
class LogMethod(Protocol):
    @overload
    def __call__(self, message: Any) -> None:
        ...
    @overload
    def __call__(self, message: Any, meta: Dict[str, Any]) -> None:
        ...
    def __call__(self, message: Any, meta: Dict[str, Any] = None) -> None:
        ...

@runtime_checkable
class ILogger(Protocol):
    info: LogMethod
    error: LogMethod
    warn: LogMethod
    debug: LogMethod
    verbose: LogMethod

LogLevel = Union['info', 'error', 'warn', 'debug', 'verbose']


@runtime_checkable
class LogWithServiceAndMethod(Protocol):
    @overload
    def __call__(self, service: str, level: LogLevel, message: Any) -> None:
        ...
    @overload
    def __call__(self, service: str, level: LogLevel, message: Any, meta: Dict[str, Any]) -> None:
        ...
    def __call__(self, service: str, level: LogLevel, message: Any, meta: Dict[str, Any] = None) -> None:
        ...

T = TypeVar('T', bound=ILogger)
LogCreator = Callable[[str], T]
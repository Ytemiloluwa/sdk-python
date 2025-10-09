from typing import Dict, Callable, Awaitable
from unittest.mock import AsyncMock, patch
from ..services.types import IInitiateServerSessionParams, IInitiateServerSessionResult

InitiateServerSessionType = Callable[[IInitiateServerSessionParams], Awaitable[IInitiateServerSessionResult]]
StartServerSessionType = Callable[[Dict[str, str]], Awaitable[None]]

initiate_server_session: AsyncMock = AsyncMock()
start_server_session: AsyncMock = AsyncMock()

patch.multiple(
    'core.services',
    initiate_server_session=initiate_server_session,
    start_server_session=start_server_session
).start()

__all__ = [
    'initiate_server_session',
    'start_server_session',
]
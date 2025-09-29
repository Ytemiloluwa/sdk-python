from typing import Dict, Any, Callable, Awaitable
from unittest.mock import AsyncMock, patch

SendCommandType = Callable[[Dict[str, Any]], Awaitable[None]]
WaitForResultType = Callable[[Dict[str, Any]], Awaitable[bytes]]

send_command: AsyncMock = AsyncMock()
wait_for_result: AsyncMock = AsyncMock()

patch('packages.core.src.operations.helpers.sendCommand.send_command', send_command).start()
patch('packages.core.src.operations.proto.waitForResult.wait_for_result', wait_for_result).start()

__all__ = [
    'send_command',
    'wait_for_result',
]

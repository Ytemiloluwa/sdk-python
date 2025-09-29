from unittest.mock import AsyncMock
from packages.app_manager.src.utils import http

# Create mock functions
post = AsyncMock()
get = AsyncMock()

# Mock the module
http.post = post
http.get = get

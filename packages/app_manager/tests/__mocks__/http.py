from unittest.mock import AsyncMock
from .utils import http

# Create mock functions
post = AsyncMock()
get = AsyncMock()

# Mock the module
http.post = post
http.get = get

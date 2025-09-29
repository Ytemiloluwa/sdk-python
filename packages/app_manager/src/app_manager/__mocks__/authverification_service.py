from unittest.mock import AsyncMock
from packages.app_manager.src.services import authverification

# Create mock functions
verify_serial_signature = AsyncMock()
verify_challenge_signature = AsyncMock()

# Mock the module
authverification.verify_serial_signature = verify_serial_signature
authverification.verify_challenge_signature = verify_challenge_signature

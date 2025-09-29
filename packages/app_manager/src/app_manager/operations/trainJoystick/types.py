from typing import Callable, Optional
from packages.app_manager.src.proto.generated.types import TrainJoystickStatus

# Re-export types
__all__ = ['TrainJoystickEventHandler']

TrainJoystickEventHandler = Callable[[TrainJoystickStatus], None]

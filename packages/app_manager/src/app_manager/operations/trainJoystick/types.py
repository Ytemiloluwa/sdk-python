from typing import Callable, Optional
from app_manager.proto.generated.types import TrainJoystickStatus

# Re-export types
__all__ = ['TrainJoystickEventHandler']

TrainJoystickEventHandler = Callable[[TrainJoystickStatus], None]

from dataclasses import dataclass
from typing import Callable, Optional
from packages.app_manager.src.proto.generated.types import AuthCardStatus


AuthCardEventHandler = Callable[[AuthCardStatus], None]


@dataclass
class IAuthCardParams:
    card_number: Optional[int] = None
    is_pair_required: Optional[bool] = None
    on_event: Optional[AuthCardEventHandler] = None
    email: Optional[str] = None
    cysync_version: Optional[str] = None
    only_failure: Optional[bool] = None
    session_id: Optional[str] = None

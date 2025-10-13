from .types import IFixtures
from .invalid_data import invalidData
from .valid import valid
from .error import error

fixtures: IFixtures = {
    "valid": valid,
    "invalidData": invalidData,
    "error": error,
}

from .types import IFixtures
from . import error
from . import invalid_data
from . import valid

fixtures: IFixtures = {
    "valid": valid.valid,
    "error": error.error,
    "invalid_data": invalid_data.invalid_data,
}

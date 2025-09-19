from .types import Fixtures
from .error import error_fixtures
from .invalidData import invalid_data_fixtures
from .valid import valid_fixtures
from .invalidArgs import invalid_args_fixtures

fixtures = Fixtures(
    valid=valid_fixtures,
    error=error_fixtures,
    invalid_data=invalid_data_fixtures,
    invalid_args=invalid_args_fixtures,
)

__all__ = [
    'fixtures',
    'error_fixtures',
    'invalid_data_fixtures', 
    'valid_fixtures',
    'invalid_args_fixtures',
]



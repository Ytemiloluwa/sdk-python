import pytest
from packages.util.utils.config import get_env_variable, Config

class TestConfig:

    def test_config_with_custom_env(self, monkeypatch):
        monkeypatch.setenv("API_CYPHEROCK", "https://test.cypherock.com")
        config = Config()
        assert config is not None
        assert config.API_CYPHEROCK == "https://test.cypherock.com"

    def test_config_with_default_values(self, monkeypatch):
        monkeypatch.delenv("API_CYPHEROCK", raising=False)
        config = Config()
        assert config is not None
        assert config.API_CYPHEROCK == "https://api.cypherock.com"

    def test_get_env_variable_error(self):
        with pytest.raises(ValueError):
            get_env_variable("TEST")



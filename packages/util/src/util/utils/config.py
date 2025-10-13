import os


def get_env_variable(key: str, default_value: str = None) -> str:
    value = None

    if key in os.environ:
        value = os.environ[key]
    if value is not None:
        return value

    if default_value is not None:
        return default_value

    raise ValueError(f"ENVIRONMENT VARIABLE '{key}' NOT SPECIFIED.")


class Config:
    def __init__(self):
        self.API_CYPHEROCK = get_env_variable(
            "API_CYPHEROCK", "https://api.cypherock.com"
        )
        self.LOG_LEVEL = get_env_variable("LOG_LEVEL", "debug")

    def get(self, key: str, default=None):
        return getattr(self, key, default)

    def __getitem__(self, key: str):
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(f"Configuration key '{key}' not found")


config = Config()

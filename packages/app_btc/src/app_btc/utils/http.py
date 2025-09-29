import httpx
from packages.util.utils.config import config

http = httpx.Client(base_url=config.API_CYPHEROCK)


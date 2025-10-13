import httpx
from util.utils.config import config

http = httpx.Client(base_url=config.API_CYPHEROCK)

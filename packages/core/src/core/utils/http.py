import httpx
from util.utils import config

http = httpx.Client(base_url=config.API_CYPHEROCK)


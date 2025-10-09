import httpx
from util.utils.config import config

http = httpx.Client(base_url=config.API_CYPHEROCK)


async def download_file(url: str) -> bytes:
    """
    Download a file from the given URL and return as bytes.

    Args:
        url: The URL to download from

    Returns:
        The file content as bytes
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.content
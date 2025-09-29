import asyncio
async def sleep(ms: int) -> None:
    await asyncio.sleep(ms / 1000)

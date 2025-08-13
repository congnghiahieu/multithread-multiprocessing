import asyncio


async def main():
    await asyncio.sleep(1)  # non-blocking
    print("Done")


asyncio.run(main())

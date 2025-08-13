# demo_get_running_loop.py
import asyncio
import os
import threading


async def main():
    loop = asyncio.get_running_loop()
    print(f"[loop] pid={os.getpid()} tid={threading.get_native_id()} loop={loop!r}")


if __name__ == "__main__":
    asyncio.run(main())

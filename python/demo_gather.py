# demo_gather.py
import asyncio
import os
import threading
import time


async def one(i, delay):
    t0 = time.perf_counter()
    print(f"[one-{i}] start pid={os.getpid()} tid={threading.get_native_id()}")
    await asyncio.sleep(delay)
    dur = time.perf_counter() - t0
    print(f"[one-{i}] end   dur={dur:.3f}s")
    return i, dur


async def main():
    t0 = time.perf_counter()
    results = await asyncio.gather(*(one(i, 0.5) for i in range(5)))
    print(
        f"[gather] results={results} total={time.perf_counter() - t0:.3f}s (≈ max delay)"
    )


if __name__ == "__main__":
    asyncio.run(main())

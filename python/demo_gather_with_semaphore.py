# demo_gather_with_semaphore.py
import asyncio
import time


async def fetch(i, sem):
    async with sem:
        t0 = time.perf_counter()
        await asyncio.sleep(1)  # pretend network
        return i, time.perf_counter() - t0


async def main():
    sem = asyncio.Semaphore(1000)  # cap in-flight concurrency
    t0 = time.perf_counter()
    results = await asyncio.gather(*(fetch(i, sem) for i in range(1000)))
    print(f"fetched={len(results)} in {time.perf_counter() - t0:.3f}s")


if __name__ == "__main__":
    asyncio.run(main())

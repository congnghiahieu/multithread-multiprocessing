# asyncio_io.py
import asyncio
import os
import threading
import time


async def io_task(i, delay=1.0):
    start = time.perf_counter()
    # asyncio runs in one thread by default; thread id shows that.
    print(f"[A] start task={i} pid={os.getpid()} tid={threading.get_native_id()}")
    await asyncio.sleep(delay)  # non-blocking; yields to the event loop
    dur = time.perf_counter() - start
    print(
        f"[A]  end  task={i} pid={os.getpid()} tid={threading.get_native_id()} dur={dur:.3f}s"
    )


async def main():
    t0 = time.perf_counter()
    await asyncio.gather(*(io_task(i) for i in range(5)))
    print(f"[A] total={time.perf_counter() - t0:.3f}s (≈ max of sleeps)")


if __name__ == "__main__":
    asyncio.run(main())

# asyncio_blocking_vs_offload.py
import os
import time
import asyncio
import threading


def blocking_file_read(path):
    # Simulate blocking file I/O with sleep + read
    time.sleep(0.5)
    with open(path, "rb") as f:
        return len(f.read())


async def bad_task(i, path):
    start = time.perf_counter()
    print(f"[A-BAD] start task={i} pid={os.getpid()} tid={threading.get_native_id()}")
    # BAD: blocks the entire event loop for ~0.5s
    size = blocking_file_read(path)
    dur = time.perf_counter() - start
    print(f"[A-BAD]  end  task={i} size={size} dur={dur:.3f}s")
    return size


async def good_task(i, path):
    start = time.perf_counter()
    print(f"[A-GOOD] start task={i} pid={os.getpid()} tid={threading.get_native_id()}")
    loop = asyncio.get_running_loop()
    # GOOD: run blocking call in default threadpool
    size = await loop.run_in_executor(None, blocking_file_read, path)
    dur = time.perf_counter() - start
    print(f"[A-GOOD]  end  task={i} size={size} dur={dur:.3f}s")
    return size


async def main():
    # prepare a small file
    with open("sample.bin", "wb") as f:
        f.write(b"x" * 100_0000)

    print("\n-- BAD: blocking in the event loop --")
    t0 = time.perf_counter()
    await asyncio.gather(*(bad_task(i, "sample.bin") for i in range(5)))
    print(f"[A-BAD] total={time.perf_counter() - t0:.3f}s (≈ sum, loop blocked)")

    print("\n-- GOOD: offloaded blocking to threadpool --")
    t1 = time.perf_counter()
    await asyncio.gather(*(good_task(i, "sample.bin") for i in range(5)))
    print(f"[A-GOOD] total={time.perf_counter() - t1:.3f}s (≈ max)")


if __name__ == "__main__":
    asyncio.run(main())

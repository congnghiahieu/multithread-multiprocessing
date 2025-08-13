# demo_run_in_executor.py
import asyncio
import os
import threading
import time


def blocking_file_read(path):
    print(f"[blocking_file_read] pid={os.getpid()} tid={threading.get_native_id()}")
    time.sleep(0.3)  # simulate slow disk
    with open(path, "rb") as f:
        return len(f.read())


async def main():
    with open("tmp.bin", "wb") as f:
        f.write(b"x" * 1_000_000)

    loop = asyncio.get_running_loop()
    print(f"[start] pid={os.getpid()} tid={threading.get_native_id()}")

    # BAD (would block loop): size = blocking_file_read("tmp.bin")
    # GOOD: offload to default thread pool
    size = await loop.run_in_executor(None, blocking_file_read, "tmp.bin")
    print(f"[done] size={size} pid={os.getpid()} tid={threading.get_native_id()}")


if __name__ == "__main__":
    asyncio.run(main())

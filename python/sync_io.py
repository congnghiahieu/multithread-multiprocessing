# sync_io.py
import os
import threading
import time


def io_task(i, delay=1.0):
    start = time.perf_counter()
    print(f"[SYNC] start task={i} pid={os.getpid()} tid={threading.get_native_id()}")
    time.sleep(delay)  # blocks this thread (the only thread)
    dur = time.perf_counter() - start
    print(
        f"[SYNC]  end  task={i} pid={os.getpid()} tid={threading.get_native_id()} dur={dur:.3f}s"
    )


def main():
    t0 = time.perf_counter()
    for i in range(5):
        io_task(i)
    print(f"[SYNC] total={time.perf_counter() - t0:.3f}s (≈ sum of sleeps)")


if __name__ == "__main__":
    main()

# futures_demo.py
import math
import os
import threading
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor


def io_task(i, delay=1.0):
    start = time.perf_counter()
    print(f"[F-IO] start task={i} pid={os.getpid()} tid={threading.get_native_id()}")
    time.sleep(delay)
    return f"task={i} dur={time.perf_counter() - start:.3f}s"


def cpu_task(i, n=10**6):
    start = time.perf_counter()
    print(f"[F-CPU] start task={i} pid={os.getpid()}")
    s = 0
    for k in range(1, n):
        s += math.isqrt(k)
    return f"task={i} dur={time.perf_counter() - start:.3f}s sum={s}"


def main():
    t0 = time.perf_counter()
    with ThreadPoolExecutor(max_workers=5) as tp:
        print(list(tp.map(io_task, range(5))))
    print(f"[F-IO] total={time.perf_counter() - t0:.3f}s (≈ max of sleeps)")

    t1 = time.perf_counter()
    with ProcessPoolExecutor() as pp:
        print(list(pp.map(cpu_task, range(4))))
    print(f"[F-CPU] total={time.perf_counter() - t1:.3f}s (parallel)")


if __name__ == "__main__":
    main()

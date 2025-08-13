# cpu_threading_bad.py
import math
import os
import threading
import time


def cpu_task(i, n=10**7):
    start = time.perf_counter()
    print(f"[TC] start task={i} pid={os.getpid()} tid={threading.get_native_id()}")
    s = 0
    for k in range(1, n):
        s += math.isqrt(k)  # pure Python CPU work -> contends on GIL
    dur = time.perf_counter() - start
    print(
        f"[TC]  end  task={i} pid={os.getpid()} tid={threading.get_native_id()} dur={dur:.3f}s"
    )
    return s


def main():
    t0 = time.perf_counter()
    threads = [threading.Thread(target=cpu_task, args=(i,)) for i in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print(f"[TC] total={time.perf_counter() - t0:.3f}s (≈ ~sequential, due to GIL)")


if __name__ == "__main__":
    main()

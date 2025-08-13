# cpu_multiprocessing_good.py
import math
import os
import time
from multiprocessing import Process, Queue, current_process


def cpu_task(i, q, n=10**7):
    start = time.perf_counter()
    print(f"[PC] start task={i} pid={os.getpid()} procname={current_process().name}")
    s = 0
    for k in range(1, n):
        s += math.isqrt(k)
    dur = time.perf_counter() - start
    print(f"[PC]  end  task={i} pid={os.getpid()} dur={dur:.3f}s")
    q.put(s)


def main():
    t0 = time.perf_counter()
    q = Queue()
    procs = [Process(target=cpu_task, args=(i, q), name=f"proc-{i}") for i in range(4)]
    for p in procs:
        p.start()
    for p in procs:
        p.join()
    results = [q.get() for _ in procs]
    print(
        f"[PC] total={time.perf_counter() - t0:.3f}s (parallel across cores) sum={sum(results)}"
    )


if __name__ == "__main__":
    main()

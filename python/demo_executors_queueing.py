# demo_executors_queueing.py
import os
import time
import threading
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor


def io_task(i):
    time.sleep(0.1)
    return (i, os.getpid(), threading.get_native_id())


def cpu_task(i):
    s = 0
    for k in range(50_000):
        s += k * k
    return (i, os.getpid())


def show_thread_pool():
    maxw = min(32, (os.cpu_count() or 1) + 4)
    print(f"[ThreadPool] default max_workers={maxw}")
    jobs = 200
    t0 = time.perf_counter()
    with ThreadPoolExecutor() as ex:
        results = list(ex.map(io_task, range(jobs)))
    print(
        f"[ThreadPool] jobs={jobs} total={time.perf_counter() - t0:.3f}s "
        f"(~ jobs/ max_workers * 0.1s) example-result={results[:3]}"
    )


def show_process_pool():
    maxw = os.cpu_count() or 1
    print(f"[ProcessPool] default max_workers={maxw}")
    jobs = 200
    t0 = time.perf_counter()
    with ProcessPoolExecutor() as ex:
        results = list(ex.map(cpu_task, range(jobs), chunksize=10))
    print(
        f"[ProcessPool] jobs={jobs} total={time.perf_counter() - t0:.3f}s "
        f"(parallel across processes) example-result={results[:]}"
    )


if __name__ == "__main__":
    show_thread_pool()
    show_process_pool()

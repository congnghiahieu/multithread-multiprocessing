import math
import os
import threading
import time
from multiprocessing import Process


def cpu_task(n):
    print(f"Process ID: {os.getpid()}")
    print(f"Thread ID: {threading.get_native_id()}")
    print(f"Task {n} started")
    # Simulating CPU-bound task
    math.factorial(10**5)
    print(f"Task {n} done")


if __name__ == "__main__":
    start = time.perf_counter()
    procs = [Process(target=cpu_task, args=(i,)) for i in range(4)]
    for p in procs:
        p.start()
    for p in procs:
        p.join()
    print("Total:", time.perf_counter() - start)

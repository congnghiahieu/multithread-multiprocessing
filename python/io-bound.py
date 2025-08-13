import os
import threading
import time


def io_task(n):
    print(f"PID / TID : {os.getpid()} / {threading.get_native_id()}")
    print(f"Task {n} started")
    time.sleep(1)  # Simulating I/O operation
    print(f"Task {n} done")


start = time.perf_counter()
threads = [threading.Thread(target=io_task, args=(i,)) for i in range(5)]
for t in threads:
    t.start()
for t in threads:
    t.join()
end = time.perf_counter()
print(f"Total time: {end - start} seconds")
# Expected: ~1 second total, tasks overlap.

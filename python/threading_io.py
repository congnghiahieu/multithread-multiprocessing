# threading_io.py
import os
import threading
import time


def io_task(i, delay=1.0):
    start = time.perf_counter()
    print(
        f"[T] start task={i} pid={os.getpid()} tid={threading.get_native_id()} name={threading.current_thread().name}"
    )
    time.sleep(delay)  # releases GIL while sleeping (I/O wait), other threads can run
    dur = time.perf_counter() - start
    print(
        f"[T]  end  task={i} pid={os.getpid()} tid={threading.get_native_id()} dur={dur:.3f}s"
    )


def main():
    t0 = time.perf_counter()
    threads = [
        threading.Thread(target=io_task, args=(i,), name=f"worker-{i}")
        for i in range(5)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print(f"[T] total={time.perf_counter() - t0:.3f}s (≈ max of sleeps)")


if __name__ == "__main__":
    main()

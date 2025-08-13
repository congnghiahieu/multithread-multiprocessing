# benchmark_chunksize.py
from concurrent.futures import ProcessPoolExecutor
import os
import time

# --- tiny CPU-bound task (tweak INNER_LOOP to change per-task cost) ---
INNER_LOOP = 10_000  # small = IPC dominates; larger = compute dominates


def tiny_cpu_task(x: int) -> int:
    s = 0
    # deliberately tiny but non-trivial loop to burn a few microseconds
    for i in range(1, INNER_LOOP):
        s += (i * i) % 97
    return s ^ x


def bench(
    n_jobs=20_000,
    max_workers=None,
    chunksizes=(1, 2, 5, 10, 20, 50, 100, 200, 500, 1000),
):
    print(f"CPU(s)={os.cpu_count()} n_jobs={n_jobs} INNER_LOOP={INNER_LOOP}")
    rows = []
    for cs in chunksizes:
        t0 = time.perf_counter()
        with ProcessPoolExecutor(max_workers=max_workers) as ex:
            # map returns results lazily; consuming forces execution
            total = 0
            for r in ex.map(tiny_cpu_task, range(n_jobs), chunksize=cs):
                total ^= r
        dt = time.perf_counter() - t0
        rows.append((cs, dt, total))
        print(f"chunksize={cs:<5} time={dt:7.3f}s  checksum={total}")

    # compute relative speedups vs chunksize=1
    base = rows[0][1]
    print("\nSummary:")
    print("chunksize |   time(s) | speedup_vs_cs1")
    for cs, dt, _ in rows:
        sp = base / dt
        print(f"{cs:9d} | {dt:9.3f} | {sp:13.2f}x")


if __name__ == "__main__":
    bench()

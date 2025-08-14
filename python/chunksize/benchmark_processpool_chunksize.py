#!/usr/bin/env python3
# benchmark_processpool_chunksize.py
"""
Benchmark ProcessPoolExecutor.map with varying:
  - n_jobs (timeseries count)
  - INNER_LOOP (points per series)
  - chunksize (jobs per batch)

The worker computes a z-score-like pass per "series".
We generate data inside the worker to avoid pickling huge arrays.

Usage examples:
  python benchmark_processpool_chunksize.py
  python benchmark_processpool_chunksize.py --njobs 1 10 100 300 500 1000 --lengths 100 500 1000 2000 --repeats 3
  python benchmark_processpool_chunksize.py --max-workers 8 --quick
"""

from __future__ import annotations
import argparse
import math
import os
import random
import time
from concurrent.futures import ProcessPoolExecutor
from typing import List, Tuple


# ------------------------------
# Worker: "z-score" per series
# ------------------------------
def _gen_series(length: int, seed: int) -> List[float]:
    rnd = random.Random(seed)
    # Lightly non-trivial distribution
    return [rnd.gauss(0.0, 1.0) + 0.01 * (i % 10) for i in range(length)]


def compute_zscore_checksum(length: int, seed: int) -> float:
    """Simulate a z-score-like CPU pass; return a tiny checksum to keep IPC small."""
    xs = _gen_series(length, seed)
    # mean and std
    m = sum(xs) / len(xs)
    var = sum((x - m) ** 2 for x in xs) / len(xs)
    sd = math.sqrt(var) if var > 0 else 1.0
    zs = ((x - m) / sd for x in xs)
    # return checksum so we don't ship big arrays back
    return sum(abs(z) for z in zs)


def _compute_zscore_checksum_wrapper(args):
    return compute_zscore_checksum(*args)


# ------------------------------
# Benchmark runner
# ------------------------------
def bench_once(
    n_jobs: int,
    series_len: int,
    chunksize: int,
    max_workers: int | None,
) -> Tuple[float, float]:
    """
    Run one benchmark with given n_jobs, series_len, chunksize.
    Returns (elapsed_seconds, checksum_aggregate).
    """
    # cap chunksize so we don't starve workers
    if max_workers is None:
        max_workers = os.cpu_count() or 1
    cap = max(1, math.ceil(n_jobs / max_workers))
    chunksize_eff = max(1, min(chunksize, cap))

    t0 = time.perf_counter()
    checksum = 0.0
    with ProcessPoolExecutor(max_workers=max_workers) as ex:
        # map over pairs (length, seed) to avoid pickling large arrays
        it = ((series_len, i * 1315423911) for i in range(n_jobs))
        for r in ex.map(_compute_zscore_checksum_wrapper, it, chunksize=chunksize_eff):
            checksum += r
    dt = time.perf_counter() - t0
    return dt, checksum


def pct(x: float) -> str:
    return f"{x * 100:.1f}%"


def format_secs(s: float) -> str:
    if s < 1:
        return f"{s * 1000:.1f} ms"
    return f"{s:.3f} s"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--njobs",
        type=int,
        nargs="*",
        default=[1, 10, 50, 100, 300, 500, 1000],
        help="Timeseries counts to test (n_jobs).",
    )
    parser.add_argument(
        "--lengths",
        type=int,
        nargs="*",
        default=[100, 500, 1000, 2000],
        help="Data points per series (INNER_LOOP).",
    )
    parser.add_argument(
        "--chunksizes",
        type=int,
        nargs="*",
        help="Chunksizes to test. Default grid chosen based on typical tiny/medium tasks.",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=None,
        help="ProcessPoolExecutor max_workers (default: os.cpu_count()).",
    )
    parser.add_argument(
        "--repeats",
        type=int,
        default=2,
        help="Repetitions per configuration for stability.",
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Use a smaller default grid for faster runs.",
    )
    args = parser.parse_args()

    if args.quick:
        default_grid = [1, 2, 4, 8, 16, 32, 64]
    else:
        default_grid = [1, 2, 4, 8, 16, 32, 64, 96, 128, 192, 256, 384, 512, 768, 1024]

    chunksizes = args.chunksizes or default_grid
    max_workers = args.max_workers or (os.cpu_count() or 1)

    print(f"CPUs={os.cpu_count()}  max_workers={max_workers}")
    print(f"n_jobs grid: {args.njobs}")
    print(f"length grid: {args.lengths}")
    print(f"chunksizes:  {chunksizes}\n")

    results = []  # (n_jobs, length, chunksize, median_time, speedup_vs_cs1)

    # Benchmark all combinations
    for n in args.njobs:
        for L in args.lengths:
            # Establish baseline at chunksize=1
            baseline_times: List[float] = []
            for _ in range(args.repeats):
                dt, _ = bench_once(n, L, 1, max_workers)
                baseline_times.append(dt)
            base = sorted(baseline_times)[len(baseline_times) // 2]

            # Test all chunksizes; cap per n/max_workers to keep load balanced
            print(f"=== n_jobs={n}  length={L} ===")
            print("chunksize    median_time      speedup_vs_cs1")
            for cs in chunksizes:
                # Run a few repeats for stability
                dts = []
                for _ in range(args.repeats):
                    dt, _ = bench_once(n, L, cs, max_workers)
                    dts.append(dt)
                med = sorted(dts)[len(dts) // 2]
                speedup = base / med if med > 0 else float("inf")
                print(f"{cs:8d}    {format_secs(med):>12}      {speedup:6.2f}x")
                results.append((n, L, cs, med, speedup))
            print()

    # Pretty summary: best chunksize per (n_jobs, length)
    print("\n=== Best chunksize per configuration (by median time) ===")
    header = "n_jobs  length   best_cs   time        speedup"
    print(header)
    print("-" * len(header))
    # group by (n, L)
    from collections import defaultdict

    groups = defaultdict(list)
    for n, L, cs, med, sp in results:
        groups[(n, L)].append((cs, med, sp))
    for (n, L), rows in sorted(groups.items()):
        rows.sort(key=lambda r: r[1])  # by time
        best_cs, best_t, best_sp = rows[0]
        print(
            f"{n:6d}  {L:6d}   {best_cs:7d}   {format_secs(best_t):>10}   {best_sp:7.2f}x"
        )


if __name__ == "__main__":
    main()

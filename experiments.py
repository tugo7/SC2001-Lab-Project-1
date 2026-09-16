"""
Experiments comparing hybrid_sort (merge sort with an insertion-sort
cutoff at threshold S) against a plain merge_sort.

Run everything:      python experiments.py
Run one experiment:   python experiments.py n_sweep

Each experiment writes its CSV/plot output into results/.
"""

import csv
import math
import os
import random
import sys
import time

import matplotlib.pyplot as plt

from sorting import hybrid_sort, merge_sort, generate_data


RESULTS_DIR = "results"
MAX_VALUE = 10_000_000
SEED = 42


def _out(name):
    os.makedirs(RESULTS_DIR, exist_ok=True)
    return os.path.join(RESULTS_DIR, name)


def n_sweep(S=10, sizes=(1_000, 10_000, 100_000, 1_000_000, 10_000_000)):
    """Key comparisons vs. input size n, for a fixed threshold S."""
    random.seed(SEED)
    results = []

    for n in sizes:
        arr = generate_data(n, MAX_VALUE)
        comparisons = hybrid_sort(arr, 0, len(arr) - 1, S)
        results.append(comparisons)
        print(f"n={n:>10,} | comparisons={comparisons:>15,}")

    theoretical = [n * math.log2(n) for n in sizes]

    plt.figure(figsize=(8, 5))
    plt.plot(sizes, results, marker="o", label="Empirical key comparisons")
    plt.plot(sizes, theoretical, marker="o", linestyle="--", label="n log2(n) reference")
    plt.xscale("log")
    plt.xlabel("Input size n")
    plt.ylabel("Key comparisons")
    plt.title(f"Comparisons vs. n (S = {S})")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(_out("comparisons_vs_n.png"), dpi=150)
    plt.close()
    print(f"Saved {_out('comparisons_vs_n.png')}")


def s_sweep(n=1_000_000, S_values=(1, 2, 3, 5, 10, 20, 50, 100, 200, 500, 1000)):
    """Key comparisons and CPU time vs. threshold S, for a fixed input size n."""
    random.seed(SEED)
    arr = generate_data(n, MAX_VALUE)

    results = []
    for S in S_values:
        arr_copy = arr.copy()
        start = time.perf_counter()
        comparisons = hybrid_sort(arr_copy, 0, len(arr_copy) - 1, S)
        elapsed = time.perf_counter() - start
        assert arr_copy == sorted(arr), f"Not sorted correctly for S={S}"
        results.append((S, comparisons, elapsed))
        print(f"S={S:>5} | comparisons={comparisons:>15,} | time={elapsed:.4f}s")

    with open(_out("comparisons_vs_s.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["S", "comparisons", "cpu_time_seconds"])
        writer.writerows(results)

    plt.figure(figsize=(8, 5))
    plt.plot([r[0] for r in results], [r[1] for r in results], marker="o")
    plt.xlabel("S (insertion sort threshold)")
    plt.ylabel("Key comparisons")
    plt.title(f"Comparisons vs. S (n = {n:,})")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(_out("comparisons_vs_s.png"), dpi=150)
    plt.close()
    print(f"Saved {_out('comparisons_vs_s.csv')} and comparisons_vs_s.png")


def optimal_s(n_values=(1_000, 10_000, 100_000, 1_000_000, 10_000_000),
              S_values=(1, 2, 4, 6, 8, 10, 12, 16, 20, 24, 32, 48, 64)):
    """Sweeps S for each n to find the S that minimizes comparisons vs. CPU time."""
    results = []

    for n in n_values:
        random.seed(SEED)
        base_arr = generate_data(n, MAX_VALUE)

        for S in S_values:
            arr = base_arr.copy()
            start = time.perf_counter()
            comparisons = hybrid_sort(arr, 0, len(arr) - 1, S)
            elapsed = time.perf_counter() - start
            assert arr == sorted(base_arr), f"Not sorted correctly for n={n}, S={S}"
            results.append((n, S, comparisons, elapsed))
            print(f"n={n:>10,} | S={S:>4} | comparisons={comparisons:>15,} | time={elapsed:.4f}s")

    with open(_out("optimal_s_results.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["n", "S", "comparisons", "cpu_time_seconds"])
        writer.writerows(results)

    best_by_comparisons = {}
    best_by_time = {}
    for n, S, comparisons, elapsed in results:
        if n not in best_by_comparisons or comparisons < best_by_comparisons[n][1]:
            best_by_comparisons[n] = (S, comparisons, elapsed)
        if n not in best_by_time or elapsed < best_by_time[n][2]:
            best_by_time[n] = (S, comparisons, elapsed)

    with open(_out("optimal_s_summary.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "n",
            "optimal_S_by_comparisons", "comparisons_at_optimal_S_by_comparisons",
            "optimal_S_by_time", "cpu_time_at_optimal_S_by_time",
        ])
        for n in n_values:
            Sc, comparisons, _ = best_by_comparisons[n]
            St, _, elapsed = best_by_time[n]
            writer.writerow([n, Sc, comparisons, St, elapsed])
            print(f"n={n:>10,} | optimal S by comparisons = {Sc:<4} | optimal S by CPU time = {St:<4}")

    # comparisons vs S, one curve per n
    plt.figure(figsize=(9, 6))
    for n in n_values:
        subset = sorted((S, c) for (nn, S, c, _) in results if nn == n)
        plt.plot([s for s, _ in subset], [c for _, c in subset], marker="o", label=f"n = {n:,}")
    plt.xlabel("S (insertion sort threshold)")
    plt.ylabel("Key comparisons")
    plt.yscale("log")
    plt.title("Key Comparisons vs. S for Different Input Sizes")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(_out("optimal_s_comparisons_vs_s.png"), dpi=150)
    plt.close()

    # CPU time vs S, one curve per n
    plt.figure(figsize=(9, 6))
    for n in n_values:
        subset = sorted((S, t) for (nn, S, _, t) in results if nn == n)
        plt.plot([s for s, _ in subset], [t for _, t in subset], marker="o", label=f"n = {n:,}")
    plt.xlabel("S (insertion sort threshold)")
    plt.ylabel("CPU time (s)")
    plt.yscale("log")
    plt.title("CPU Time vs. S for Different Input Sizes")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(_out("optimal_s_time_vs_s.png"), dpi=150)
    plt.close()

    # optimal S vs n, both metrics
    plt.figure(figsize=(7, 5))
    plt.plot(n_values, [best_by_comparisons[n][0] for n in n_values],
              marker="o", label="Optimal S by comparisons")
    plt.plot(n_values, [best_by_time[n][0] for n in n_values],
              marker="s", label="Optimal S by CPU time")
    plt.xscale("log")
    plt.xlabel("Input size n")
    plt.ylabel("Optimal S")
    plt.title("Optimal S vs. Input Size n")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(_out("optimal_s_vs_n.png"), dpi=150)
    plt.close()

    print(f"Saved optimal-S results to {RESULTS_DIR}/")
    return best_by_time


def _load_optimal_s(n, default):
    path = _out("optimal_s_summary.csv")
    try:
        with open(path, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if int(row["n"]) == n:
                    return int(row["optimal_S_by_time"])
    except (FileNotFoundError, KeyError):
        pass
    return default


def comparison(n=10_000_000, S=None):
    """Compares hybrid_sort (at its CPU-time-optimal S) against plain merge_sort."""
    if S is None:
        S = _load_optimal_s(n, default=16)

    random.seed(SEED)
    base_arr = generate_data(n, MAX_VALUE)

    hybrid_arr = base_arr.copy()
    start = time.perf_counter()
    hybrid_comparisons = hybrid_sort(hybrid_arr, 0, len(hybrid_arr) - 1, S)
    hybrid_time = time.perf_counter() - start
    assert hybrid_arr == sorted(base_arr), "hybrid_sort output incorrect"

    merge_arr = base_arr.copy()
    start = time.perf_counter()
    merge_comparisons = merge_sort(merge_arr, 0, len(merge_arr) - 1)
    merge_time = time.perf_counter() - start
    assert merge_arr == sorted(base_arr), "merge_sort output incorrect"

    print(f"n = {n:,}, S (hybrid) = {S}\n")
    print(f"{'Algorithm':<22}{'Comparisons':>20}{'CPU time (s)':>18}")
    print(f"{'Hybrid sort':<22}{hybrid_comparisons:>20,}{hybrid_time:>18.4f}")
    print(f"{'Merge sort':<22}{merge_comparisons:>20,}{merge_time:>18.4f}")

    with open(_out("hybrid_vs_merge_results.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["algorithm", "n", "S", "comparisons", "cpu_time_seconds"])
        writer.writerow(["hybrid_sort", n, S, hybrid_comparisons, hybrid_time])
        writer.writerow(["merge_sort", n, "", merge_comparisons, merge_time])

    fig, axes = plt.subplots(1, 2, figsize=(10, 5))

    axes[0].bar([f"Hybrid Sort\n(S={S})", "Merge Sort"],
                [hybrid_comparisons, merge_comparisons], color=["#1f77b4", "#ff7f0e"])
    axes[0].set_ylabel("Key comparisons")
    axes[0].set_title(f"Key Comparisons (n = {n:,})")

    axes[1].bar([f"Hybrid Sort\n(S={S})", "Merge Sort"],
                [hybrid_time, merge_time], color=["#1f77b4", "#ff7f0e"])
    axes[1].set_ylabel("CPU time (s)")
    axes[1].set_title(f"CPU Time (n = {n:,})")

    plt.tight_layout()
    plt.savefig(_out("hybrid_vs_merge_comparison.png"), dpi=150)
    plt.close()
    print(f"Saved results to {RESULTS_DIR}/")


EXPERIMENTS = {
    "n_sweep": n_sweep,
    "s_sweep": s_sweep,
    "optimal_s": optimal_s,
    "comparison": comparison,
}


if __name__ == "__main__":
    names = sys.argv[1:] or list(EXPERIMENTS)

    for name in names:
        if name not in EXPERIMENTS:
            print(f"Unknown experiment '{name}'. Choose from: {', '.join(EXPERIMENTS)}")
            sys.exit(1)

    for name in names:
        print(f"\n=== {name} ===")
        EXPERIMENTS[name]()

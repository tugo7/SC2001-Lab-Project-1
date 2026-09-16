"""
Part (d): Compare the hybrid algorithm (using the optimal S found in
Part (c)(iii)) against the original merge sort, in terms of number of
key comparisons and CPU time, on a dataset of 10 million integers.
"""

import csv
import random
import time

import matplotlib.pyplot as plt

from hybrid_sort import hybrid_sort, generate_data
from merge_sort import merge_sort


N = 10_000_000
MAX_VALUE = 10_000_000
SEED = 42
DEFAULT_S = 16  # Part (c)(iii)'s CPU-time-optimal S values cluster in ~8-24; used if no summary CSV is found
OPTIMAL_S_SUMMARY = "part_c_iii_optimal_s_summary.csv"
OUTPUT_CSV = "part_d_results.csv"


def load_optimal_s(n=N, default=DEFAULT_S):
    # Part (c)(iii) finds two different "optimal" S values: minimizing key
    # comparisons is trivially achieved at S=1 (a pure merge sort always
    # makes fewer comparisons than insertion sort would for the same
    # block), while minimizing actual CPU time - the practically
    # meaningful notion of "best performance", and what Part (d) measures
    # - lands on a small non-trivial S. We use the latter here.
    try:
        with open(OPTIMAL_S_SUMMARY, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if int(row["n"]) == n:
                    return int(row["optimal_S_by_time"])
    except (FileNotFoundError, KeyError):
        pass
    return default


def run_comparison():
    optimal_s = load_optimal_s()

    random.seed(SEED)
    base_arr = generate_data(N, MAX_VALUE)

    # --- Hybrid sort ---
    hybrid_arr = base_arr.copy()
    start = time.perf_counter()
    hybrid_comparisons = hybrid_sort(hybrid_arr, 0, len(hybrid_arr) - 1, optimal_s)
    hybrid_time = time.perf_counter() - start
    assert hybrid_arr == sorted(base_arr), "Hybrid sort output incorrect"

    # --- Original merge sort ---
    merge_arr = base_arr.copy()
    start = time.perf_counter()
    merge_comparisons = merge_sort(merge_arr, 0, len(merge_arr) - 1)
    merge_time = time.perf_counter() - start
    assert merge_arr == sorted(base_arr), "Original merge sort output incorrect"

    print(f"n = {N:,}, S (hybrid) = {optimal_s}\n")
    print(f"{'Algorithm':<22}{'Comparisons':>20}{'CPU time (s)':>18}")
    print(f"{'Hybrid sort':<22}{hybrid_comparisons:>20,}{hybrid_time:>18.4f}")
    print(f"{'Original merge sort':<22}{merge_comparisons:>20,}{merge_time:>18.4f}")

    comparison_reduction = (1 - hybrid_comparisons / merge_comparisons) * 100
    time_reduction = (1 - hybrid_time / merge_time) * 100
    print(f"\nHybrid sort makes {comparison_reduction:.2f}% fewer key comparisons than merge sort")
    print(f"Hybrid sort is {time_reduction:.2f}% faster (CPU time) than merge sort")

    with open(OUTPUT_CSV, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["algorithm", "n", "S", "comparisons", "cpu_time_seconds"])
        writer.writerow(["hybrid_sort", N, optimal_s, hybrid_comparisons, hybrid_time])
        writer.writerow(["merge_sort", N, "", merge_comparisons, merge_time])
    print(f"\nSaved results to {OUTPUT_CSV}")

    plot_results(hybrid_comparisons, merge_comparisons, hybrid_time, merge_time, optimal_s)


def plot_results(hybrid_c, merge_c, hybrid_t, merge_t, optimal_s):
    fig, axes = plt.subplots(1, 2, figsize=(10, 5))

    axes[0].bar(["Hybrid Sort\n(S={})".format(optimal_s), "Merge Sort"],
                [hybrid_c, merge_c], color=["#1f77b4", "#ff7f0e"])
    axes[0].set_ylabel("Key comparisons")
    axes[0].set_title(f"Key Comparisons (n = {N:,})")

    axes[1].bar(["Hybrid Sort\n(S={})".format(optimal_s), "Merge Sort"],
                [hybrid_t, merge_t], color=["#1f77b4", "#ff7f0e"])
    axes[1].set_ylabel("CPU time (s)")
    axes[1].set_title(f"CPU Time (n = {N:,})")

    plt.tight_layout()
    plt.savefig("part_d_comparison.png", dpi=150)
    print("Saved plot to part_d_comparison.png")
    plt.close()


if __name__ == "__main__":
    run_comparison()

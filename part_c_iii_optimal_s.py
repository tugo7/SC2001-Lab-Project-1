"""
Part (c)(iii): Using different sizes of input datasets, study how to
determine an optimal value of S for the best performance of the hybrid
algorithm.

For each input size n (small to large), sweeps S over a range and records
the number of key comparisons. The S that minimizes comparisons for a
given n is taken as the empirical optimum for that n. Results let us see
whether the optimal S stays roughly constant or grows with n.
"""

import csv
import random
import time

import matplotlib.pyplot as plt

from hybrid_sort import hybrid_sort, generate_data


# Input sizes from small to large, spanning the range required by Part (b)
N_VALUES = [1_000, 10_000, 100_000, 1_000_000, 10_000_000]

# Threshold values to try for each n. Concentrated in the small range
# because theory (insertion cost ~ n*S/4, merge cost ~ n*log2(n/S)) predicts
# the optimum sits at a small constant S, independent of n.
S_VALUES = [1, 2, 4, 6, 8, 10, 12, 16, 20, 24, 32, 48, 64]

MAX_VALUE = 10_000_000  # range [1, MAX_VALUE] for generated integers
SEED = 42               # fixed seed so results are reproducible

RESULTS_CSV = "part_c_iii_results.csv"
SUMMARY_CSV = "part_c_iii_optimal_s_summary.csv"


def run_experiment():
    results = []  # list of (n, S, comparisons, cpu_time_seconds)

    for n in N_VALUES:
        # Same base array (per n) reused across every S so the S sweep is
        # a fair comparison - only S changes, not the input.
        random.seed(SEED)
        base_arr = generate_data(n, MAX_VALUE)

        for S in S_VALUES:
            arr = base_arr.copy()

            start = time.perf_counter()
            comparisons = hybrid_sort(arr, 0, len(arr) - 1, S)
            elapsed = time.perf_counter() - start

            assert arr == sorted(base_arr), f"Not sorted correctly for n={n}, S={S}"

            results.append((n, S, comparisons, elapsed))
            print(f"n={n:>10,} | S={S:>4} | comparisons={comparisons:>15,} | time={elapsed:.4f}s")

    return results


def save_results(results):
    with open(RESULTS_CSV, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["n", "S", "comparisons", "cpu_time_seconds"])
        writer.writerows(results)
    print(f"\nSaved raw results to {RESULTS_CSV}")


def find_optimal_s(results):
    # Two notions of "optimal" that turn out to disagree:
    #  - by_comparisons: the S that minimizes key comparisons. Since a pure
    #    merge sort (S=1) always does asymptotically fewer *comparisons*
    #    than insertion sort would for the same block (S log S vs S^2/4),
    #    this is trivially minimized at the smallest S tested.
    #  - by_time: the S that minimizes actual CPU time. This is the
    #    practically meaningful "best performance" S - insertion sort has
    #    much lower per-comparison overhead (no recursive calls, no
    #    sub-array copying), so it wins on the clock for small blocks even
    #    though it makes more comparisons.
    best_by_comparisons = {}
    best_by_time = {}
    for n, S, comparisons, elapsed in results:
        if n not in best_by_comparisons or comparisons < best_by_comparisons[n][1]:
            best_by_comparisons[n] = (S, comparisons, elapsed)
        if n not in best_by_time or elapsed < best_by_time[n][2]:
            best_by_time[n] = (S, comparisons, elapsed)

    with open(SUMMARY_CSV, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "n",
            "optimal_S_by_comparisons", "comparisons_at_optimal_S_by_comparisons",
            "optimal_S_by_time", "cpu_time_at_optimal_S_by_time",
        ])
        for n in N_VALUES:
            Sc, comparisons, _ = best_by_comparisons[n]
            St, _, elapsed = best_by_time[n]
            writer.writerow([n, Sc, comparisons, St, elapsed])
            print(f"n={n:>10,} | optimal S by comparisons = {Sc:<4} (comparisons={comparisons:,}) "
                  f"| optimal S by CPU time = {St:<4} (time={elapsed:.4f}s)")

    print(f"\nSaved optimal-S summary to {SUMMARY_CSV}")
    return best_by_comparisons, best_by_time


def plot_results(results, best_by_comparisons, best_by_time):
    # Comparisons vs S, one curve per n
    plt.figure(figsize=(9, 6))
    for n in N_VALUES:
        subset = sorted((S, c) for (nn, S, c, _) in results if nn == n)
        S_list = [s for s, _ in subset]
        c_list = [c for _, c in subset]
        plt.plot(S_list, c_list, marker="o", label=f"n = {n:,}")

    plt.xlabel("S (insertion sort threshold)")
    plt.ylabel("Number of key comparisons")
    plt.yscale("log")
    plt.title("Key Comparisons vs. S for Different Input Sizes")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("part_c_iii_comparisons_vs_S.png", dpi=150)
    print("Saved plot to part_c_iii_comparisons_vs_S.png")
    plt.close()

    # CPU time vs S, one curve per n
    plt.figure(figsize=(9, 6))
    for n in N_VALUES:
        subset = sorted((S, t) for (nn, S, _, t) in results if nn == n)
        S_list = [s for s, _ in subset]
        t_list = [t for _, t in subset]
        plt.plot(S_list, t_list, marker="o", label=f"n = {n:,}")

    plt.xlabel("S (insertion sort threshold)")
    plt.ylabel("CPU time (s)")
    plt.yscale("log")
    plt.title("CPU Time vs. S for Different Input Sizes")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("part_c_iii_time_vs_S.png", dpi=150)
    print("Saved plot to part_c_iii_time_vs_S.png")
    plt.close()

    # Optimal S vs n, for both metrics
    plt.figure(figsize=(7, 5))
    plt.plot(N_VALUES, [best_by_comparisons[n][0] for n in N_VALUES],
              marker="o", label="Optimal S by comparisons")
    plt.plot(N_VALUES, [best_by_time[n][0] for n in N_VALUES],
              marker="s", label="Optimal S by CPU time")
    plt.xscale("log")
    plt.xlabel("Input size n")
    plt.ylabel("Optimal S")
    plt.title("Optimal S vs. Input Size n")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("part_c_iii_optimal_S_vs_n.png", dpi=150)
    print("Saved plot to part_c_iii_optimal_S_vs_n.png")
    plt.close()


if __name__ == "__main__":
    results = run_experiment()
    save_results(results)
    best_by_comparisons, best_by_time = find_optimal_s(results)
    plot_results(results, best_by_comparisons, best_by_time)

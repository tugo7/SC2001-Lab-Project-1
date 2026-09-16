import random
import math
import matplotlib.pyplot as plt
# Sorts a small section of the array using insertion sort
# Returns the number of key comparisons made
def insertion_sort(arr, left, right):
    comparisons = 0

    for i in range(left + 1, right + 1):
        key = arr[i]
        j = i - 1

        while j >= left:
            # Comparing two values in the array = 1 key comparison
            comparisons += 1

            if arr[j] <= key:
                break

            arr[j + 1] = arr[j]
            j -= 1

        arr[j + 1] = key

    return comparisons


# Merges two sorted halves back together
# Also counts the key comparisons during merging
def merge(arr, left, mid, right):
    comparisons = 0

    # Make copies of the left and right halves
    left_arr = arr[left:mid + 1]
    right_arr = arr[mid + 1:right + 1]

    i = 0
    j = 0
    k = left

    while i < len(left_arr) and j < len(right_arr):
        comparisons += 1

        if left_arr[i] <= right_arr[j]:
            arr[k] = left_arr[i]
            i += 1
        else:
            arr[k] = right_arr[j]
            j += 1

        k += 1

    # Copy over any remaining elements
    while i < len(left_arr):
        arr[k] = left_arr[i]
        i += 1
        k += 1

    while j < len(right_arr):
        arr[k] = right_arr[j]
        j += 1
        k += 1

    return comparisons


# Hybrid merge + insertion sort
# If the current subarray size <= S, use insertion sort
# Otherwise keep splitting like normal merge sort
def hybrid_sort(arr, left, right, S):
    comparisons = 0

    # Only one element left, so it is already sorted
    if left >= right:
        return comparisons

    # Switch to insertion sort for small subarrays
    if right - left + 1 <= S:
        comparisons += insertion_sort(arr, left, right)

    else:
        mid = (left + right) // 2

        # Sort both halves recursively
        comparisons += hybrid_sort(arr, left, mid, S)
        comparisons += hybrid_sort(arr, mid + 1, right, S)

        # Merge the sorted halves
        comparisons += merge(arr, left, mid, right)

    return comparisons


# Generates n random integers from 1 to x
def generate_data(n, x):
    return [random.randint(1, x) for _ in range(n)]


# ----------------------------------------------------
# Part C(i): keep S fixed and increase input size n
# ----------------------------------------------------
# Guarded by __main__ so this module can be safely imported elsewhere
# (e.g. by the Part c(iii)/d experiment scripts) without re-running the
# whole experiment and blocking on plt.show() as a side effect.
if __name__ == "__main__":
    S = 10
    x = 10_000_000

    # Input sizes tested from 1,000 to 10 million
    sizes = [1_000, 10_000, 100_000, 1_000_000, 10_000_000]

    # Same seed so the experiment can be reproduced
    random.seed(42)

    results = []

    for n in sizes:
        arr = generate_data(n, x)

        comparisons = hybrid_sort(arr, 0, len(arr) - 1, S)

        # Store comparison count for graphing later
        results.append(comparisons)

        print("n =", n, "| Key comparisons =", comparisons)

    # n log2(n) reference to compare theoretical growth
    theoretical = [n * math.log2(n) for n in sizes]

    # Plot empirical results against theoretical n log n growth
    plt.plot(
        sizes,
        results,
        marker="o",
        label="Empirical key comparisons"
    )

    plt.plot(
        sizes,
        theoretical,
        marker="o",
        linestyle="--",
        label="n log2(n) reference"
    )

    # Log scale makes the large range of n easier to see
    plt.xscale("log")

    plt.xlabel("Input Size n")
    plt.ylabel("Number of Key Comparisons")
    plt.title("Hybrid Sort: Empirical vs n log2(n) Growth (S = 10)")

    plt.legend()
    plt.grid()

    # Save graph so we can use it in the presentation
    plt.savefig("comparisons_vs_n.png")

    plt.show()
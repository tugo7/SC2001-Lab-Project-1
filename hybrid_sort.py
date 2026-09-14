import random
import math
import matplotlib.pyplot as plt
def insertion_sort(arr, left, right):
    comparisons = 0

    for i in range(left + 1, right + 1):
        key = arr[i]
        j = i - 1

        while j >= left:
            comparisons += 1

            if arr[j] <= key:
                break

            arr[j + 1] = arr[j]
            j -= 1

        arr[j + 1] = key

    return comparisons

def merge(arr, left, mid, right):
    comparisons = 0

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

    while i < len(left_arr):
        arr[k] = left_arr[i]
        i += 1
        k += 1

    while j < len(right_arr):
        arr[k] = right_arr[j]
        j += 1
        k += 1

    return comparisons

def hybrid_sort(arr, left, right, S):
    comparisons = 0

    if left >= right:
        return comparisons

    # If the subarray is small enough, use insertion sort
    if right - left + 1 <= S:
        comparisons += insertion_sort(arr, left, right)

    else:
        mid = (left + right) // 2

        comparisons += hybrid_sort(arr, left, mid, S)
        comparisons += hybrid_sort(arr, mid + 1, right, S)

        comparisons += merge(arr, left, mid, right)

    return comparisons

def generate_data(n, x):
    return [random.randint(1, x) for _ in range(n)]

S = 10
x = 10_000_000

sizes = [1_000, 10_000, 100_000, 1_000_000, 10_000_000]

random.seed(42)

results = []

for n in sizes:
    arr = generate_data(n, x)

    comparisons = hybrid_sort(arr, 0, len(arr) - 1, S)

    results.append(comparisons)

    print("n =", n, "| Key comparisons =", comparisons)

# Theoretical n log2(n) reference
theoretical = [n * math.log2(n) for n in sizes]

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

plt.xscale("log")

plt.xlabel("Input Size n")
plt.ylabel("Number of Key Comparisons")
plt.title("Hybrid Sort: Empirical vs n log2(n) Growth (S = 10)")

plt.legend()
plt.grid()

plt.savefig("comparisons_vs_n.png")

plt.show()
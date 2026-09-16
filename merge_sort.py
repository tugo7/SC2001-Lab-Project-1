import random


# Merges two sorted halves back together
# Uses the same merge logic/comparison convention as hybrid_sort.merge()
# so that comparison counts between the two algorithms are directly comparable
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


# Original (plain) merge sort, as taught in lecture
# Always recurses down to single elements - no insertion sort fallback
def merge_sort(arr, left, right):
    comparisons = 0

    # Only one element left, so it is already sorted
    if left >= right:
        return comparisons

    mid = (left + right) // 2

    # Sort both halves recursively
    comparisons += merge_sort(arr, left, mid)
    comparisons += merge_sort(arr, mid + 1, right)

    # Merge the sorted halves
    comparisons += merge(arr, left, mid, right)

    return comparisons


# Generates n random integers from 1 to x
# (kept local so this module has no dependency on hybrid_sort.py)
def generate_data(n, x):
    return [random.randint(1, x) for _ in range(n)]


if __name__ == "__main__":
    random.seed(1)
    test = generate_data(5000, 100_000)
    comparisons = merge_sort(test, 0, len(test) - 1)
    assert test == sorted(test), "merge_sort produced an incorrect ordering"
    print(f"Self-test passed. n=5000, key comparisons={comparisons:,}")

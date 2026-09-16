import random


# Uses the same merge logic/comparison convention as hybrid_sort.merge()
# so that comparison counts between the two algorithms are directly comparable
def merge(arr, left, mid, right):
    """Merges the sorted halves arr[left:mid+1] and arr[mid+1:right+1] in place.

    Returns the number of key comparisons performed.
    """
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


def merge_sort(arr, left, right):
    """Plain merge sort - always recurses down to single elements.

    Returns the number of key comparisons performed.
    """
    if left >= right:
        return 0

    mid = (left + right) // 2

    comparisons = merge_sort(arr, left, mid)
    comparisons += merge_sort(arr, mid + 1, right)
    comparisons += merge(arr, left, mid, right)

    return comparisons


# Kept local so this module has no dependency on hybrid_sort.py
def generate_data(n, x):
    """Generates n random integers drawn uniformly from [1, x]."""
    return [random.randint(1, x) for _ in range(n)]


if __name__ == "__main__":
    random.seed(1)
    data = generate_data(5000, 100_000)

    test = data.copy()
    comparisons = merge_sort(test, 0, len(test) - 1)
    assert test == sorted(data), "merge_sort produced an incorrect ordering"

    print(f"Self-test passed (n={len(data):,}): {comparisons:,} comparisons")

import random


def insertion_sort(arr, left, right):
    """Sorts arr[left:right+1] in place using insertion sort.

    Returns the number of key comparisons performed.
    """
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


def hybrid_sort(arr, left, right, S):
    """Merge sort that switches to insertion sort once a subarray's size drops to S.

    Returns the number of key comparisons performed.
    """
    if left >= right:
        return 0

    if right - left + 1 <= S:
        return insertion_sort(arr, left, right)

    mid = (left + right) // 2

    comparisons = hybrid_sort(arr, left, mid, S)
    comparisons += hybrid_sort(arr, mid + 1, right, S)
    comparisons += merge(arr, left, mid, right)

    return comparisons


def generate_data(n, x):
    """Generates n random integers drawn uniformly from [1, x]."""
    return [random.randint(1, x) for _ in range(n)]


if __name__ == "__main__":
    random.seed(1)
    data = generate_data(5000, 100_000)

    test = data.copy()
    comparisons = hybrid_sort(test, 0, len(test) - 1, 16)
    assert test == sorted(data), "hybrid_sort produced an incorrect ordering"

    print(f"Self-test passed (n={len(data):,}, S=16): {comparisons:,} comparisons")

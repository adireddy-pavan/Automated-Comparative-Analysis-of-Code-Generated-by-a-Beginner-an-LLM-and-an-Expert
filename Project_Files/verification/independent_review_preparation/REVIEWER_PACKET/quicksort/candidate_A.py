def quicksort(arr):
    if len(arr) <= 1:
        return arr
    assert isinstance(arr, list)
    p = arr[0]
    less = []
    more = []
    for k in range(1, len(arr)):
        if arr[k] < p:
            less.append(arr[k])
        elif arr[k] > p:
            more.append(arr[k])
    return quicksort(less) + [p] + quicksort(more)

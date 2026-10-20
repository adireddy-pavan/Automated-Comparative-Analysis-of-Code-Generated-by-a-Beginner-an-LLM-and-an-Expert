def chunk_list(items, size):
    result = []
    n = len(items) // size
    for i in range(n):
        result.append(items[i * size:(i + 1) * size])
    return result

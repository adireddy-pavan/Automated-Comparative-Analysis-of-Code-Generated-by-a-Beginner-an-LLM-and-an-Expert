def is_subsequence(s, t):
    for ch in s:
        if ch not in t:
            return False
    return True

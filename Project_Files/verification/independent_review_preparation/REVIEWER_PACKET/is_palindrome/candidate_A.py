def is_palindrome(s):
    x = ""
    for c in s:
        if c.isalnum():
            x = x + c.lower()
    flag = True
    i = 0
    j = len(x) - 1
    while i < j:
        if x[i] != x[j]:
            flag = False
        i = i + 1
        j = j - 1
    return flag

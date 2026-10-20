def run_length_encode(s):
    if s == "":
        return ""
    cur = s[0]
    cnt = 1
    res = ""
    i = 1
    while i < len(s):
        if s[i] == cur:
            cnt = cnt + 1
        else:
            res = res + cur + str(cnt)
            cur = s[i]
            cnt = 1
        i = i + 1
    res = res + cur + str(cnt)
    return res

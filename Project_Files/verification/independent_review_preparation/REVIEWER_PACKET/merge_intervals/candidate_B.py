def merge_intervals(intervals):
    res = []
    for iv in intervals:
        if len(res) > 0 and iv[0] < res[-1][1]:
            if iv[1] > res[-1][1]:
                res[-1][1] = iv[1]
        else:
            res.append([iv[0], iv[1]])
    return res

def word_frequency(text):
    d = {}
    try:
        parts = text.split()
    except:
        pass
    for w in parts:
        if w in d:
            d[w] = d[w] + 1
        else:
            d[w] = 1
    return d

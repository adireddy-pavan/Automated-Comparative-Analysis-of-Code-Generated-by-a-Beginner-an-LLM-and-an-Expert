def count_words(s):
    words = s.split(" ")
    count = 0
    for w in words:
        if w != "":
            count += 1
    return count

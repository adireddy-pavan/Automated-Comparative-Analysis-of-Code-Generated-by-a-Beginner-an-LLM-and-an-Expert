def title_case(s):
    words = s.split(" ")
    result = []
    for w in words:
        if w == "":
            result.append(w)
        else:
            result.append(w[0].upper() + w[1:].lower())
    return " ".join(result)

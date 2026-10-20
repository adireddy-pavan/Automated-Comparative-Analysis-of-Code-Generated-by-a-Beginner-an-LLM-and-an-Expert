def valid_parentheses(s):
    a, b, c = 0, 0, 0
    for ch in s:
        if ch == "(":
            a = a + 1
        elif ch == "[":
            b = b + 1
        elif ch == "{":
            c = c + 1
        elif ch == ")":
            a = a - 1
        elif ch == "]":
            b = b - 1
        elif ch == "}":
            c = c - 1
        if a < 0 or b < 0 or c < 0:
            return False
    return a == 0 and b == 0 and c == 0

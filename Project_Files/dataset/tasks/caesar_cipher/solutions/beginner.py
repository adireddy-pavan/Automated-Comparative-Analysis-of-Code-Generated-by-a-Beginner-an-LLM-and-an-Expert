def caesar_cipher(text, shift):
    res = ""
    for ch in text:
        res = res + chr(ord(ch) + shift)
    return res

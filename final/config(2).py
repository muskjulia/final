REVERSE=False

DICT = 'dict.small.txt'
NTH = 1
GROUP_SIZE = 1
FNREV = (lambda x: x[::-1]) if REVERSE else (lambda x:x)
PREFIX = ("rev" if REVERSE else "fwd") + "-"
ALPHABET = 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ-'

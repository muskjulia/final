REVERSE=False

FNREV = (lambda x: x[::-1]) if REVERSE else (lambda x:x)
PREFIX = ("rev" if REVERSE else "fwd") + "-"

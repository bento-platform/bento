import sys

from termcolor import cprint

__all__ = [
    "err",
]


def err(msg):
    cprint(msg, "red", file=sys.stderr)

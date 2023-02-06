import sys

from termcolor import cprint

__all__ = [
    "info",
    "warn",
    "err",
]


def info(msg: str):
    cprint(msg, "blue", file=sys.stderr)


def warn(msg: str):
    cprint(msg, "yellow", file=sys.stderr)


def err(msg: str):
    cprint(msg, "red", file=sys.stderr)

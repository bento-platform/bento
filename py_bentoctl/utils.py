import sys

from termcolor import cprint

__all__ = [
    "task_print",
    "task_print_done",
    "info",
    "warn",
    "err",
]


def task_print(msg: str):
    print(msg, end=" ", file=sys.stderr)


def task_print_done(msg: str = "done."):
    cprint(msg, "green", file=sys.stderr)


def info(msg: str):
    cprint(msg, "blue", file=sys.stderr)


def warn(msg: str):
    cprint(msg, "yellow", file=sys.stderr)


def err(msg: str):
    cprint(msg, "red", file=sys.stderr)

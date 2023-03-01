import sys

from termcolor import cprint

__all__ = [
    "task_print",
    "task_print_done",
    "info",
    "warn",
    "err",
]


def task_print(msg: str) -> None:
    print(msg, end=" ", file=sys.stderr)


def task_print_done(msg: str = "done.") -> None:
    cprint(msg, "green", file=sys.stderr)


def info(msg: str) -> None:
    cprint(msg, "blue", file=sys.stderr)


def warn(msg: str) -> None:
    cprint(msg, "yellow", file=sys.stderr)


def err(msg: str) -> None:
    cprint(msg, "red", file=sys.stderr)

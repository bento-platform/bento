import docker
import sys

from termcolor import cprint

__all__ = [
    "task_print",
    "task_print_done",
    "info",
    "warn",
    "err",

    "indent_str",

    "get_docker_client",
]


def task_print(msg: str) -> None:
    print(msg, end=" ", file=sys.stderr)


def task_print_done(msg: str = "done.", color: str = "green") -> None:
    cprint(msg, color, file=sys.stderr)


def info(msg: str) -> None:
    cprint(msg, "blue", file=sys.stderr)


def warn(msg: str) -> None:
    cprint(msg, "yellow", file=sys.stderr)


def err(msg: str) -> None:
    cprint(msg, "red", file=sys.stderr)


def indent_str(msg: str, n: int) -> str:
    return "\n".join((" " * n) + m for m in msg.split("\n"))


def get_docker_client() -> docker.DockerClient:
    return docker.from_env()

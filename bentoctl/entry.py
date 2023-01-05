from __future__ import annotations
import argparse
import sys

from .auth_helper import init_auth

from typing import Callable, Optional

__version__ = "0.1.0"


def add_init_auth_args(_sp):
    pass


def exec_init_auth(_args):
    init_auth()


def main(args: Optional[list[str]] = None) -> int:
    args = args or sys.argv[1:]

    parser = argparse.ArgumentParser(
        description="Tools for managing a Bento deployment (development or production).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("--version", "-v", action="version", version=__version__)

    subparsers = parser.add_subparsers()

    def _add_subparser(arg: str, help_text: str, fn_exec_cmd: Callable, fn_add_args: Callable):
        subparser = subparsers.add_parser(arg, help=help_text)
        subparser.set_defaults(func=fn_exec_cmd)
        fn_add_args(subparser)

    _add_subparser(
        "init-auth",
        "Configure authentication for BentoV2 with a local Keycloak instance.",
        exec_init_auth,
        add_init_auth_args)

    p_args = parser.parse_args(args)

    if not getattr(p_args, "func", None):
        p_args = parser.parse_args(("--help",))

    p_args.func(p_args)
    return 0


if __name__ == "__main__":
    exit(main())

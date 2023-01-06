from __future__ import annotations
import argparse
import sys

from abc import ABC, abstractmethod

from .auth_helper import init_auth
from .config import BENTO_DOCKER_SERVICES
from .services import run_service, stop_service, clean_service

from typing import Optional, Type

__version__ = "0.1.0"


class SubCommand(ABC):

    @staticmethod
    def add_args(sp):
        pass

    @staticmethod
    @abstractmethod
    def exec(args):
        pass


class InitAuth(SubCommand):

    @staticmethod
    def exec(args):
        init_auth()


class Run(SubCommand):

    @staticmethod
    def add_args(sp):
        sp.add_argument(
            "service", type=str, choices=(*BENTO_DOCKER_SERVICES, "all"),
            help="Service to run, or 'all' to run everything.")

    @staticmethod
    def exec(args):
        run_service(args.service)


class Stop(SubCommand):

    @staticmethod
    def add_args(sp):
        sp.add_argument(
            "service", type=str, choices=(*BENTO_DOCKER_SERVICES, "all"),
            help="Service to stop, or 'all' to stop everything.")

    @staticmethod
    def exec(args):
        stop_service(args.service)


class Clean(SubCommand):

    @staticmethod
    def add_args(sp):
        sp.add_argument(
            "service", type=str, choices=(*BENTO_DOCKER_SERVICES, "all"),
            help="Service to clean, or 'all' to clean everything.")

    @staticmethod
    def exec(args):
        clean_service(args.service)


def main(args: Optional[list[str]] = None) -> int:
    args = args or sys.argv[1:]

    parser = argparse.ArgumentParser(
        description="Tools for managing a Bento deployment (development or production).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("--version", "-v", action="version", version=__version__)

    subparsers = parser.add_subparsers()

    def _add_subparser(arg: str, help_text: str, subcommand: Type[SubCommand]):
        subparser = subparsers.add_parser(arg, help=help_text)
        subparser.set_defaults(func=subcommand.exec)
        subcommand.add_args(subparser)

    _add_subparser("init-auth", "Configure authentication for BentoV2 with a local Keycloak instance.", InitAuth)
    _add_subparser("run", "Run Bento services.", Run)
    _add_subparser("stop", "Stop Bento services.", Stop)
    _add_subparser("stop", "Clean services.", Clean)

    p_args = parser.parse_args(args)

    if not getattr(p_args, "func", None):
        p_args = parser.parse_args(("--help",))

    p_args.func(p_args)
    return 0


if __name__ == "__main__":
    exit(main())

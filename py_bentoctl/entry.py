from __future__ import annotations
import argparse
import subprocess
import sys

from abc import ABC, abstractmethod

from .auth_helper import init_auth
from .config import BENTO_DOCKER_SERVICES
from . import services as s
from . import other_helpers as oh

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
            "service", type=str, nargs="?", default="all", choices=(*BENTO_DOCKER_SERVICES, "all"),
            help="Service to run, or 'all' to run everything.")
        sp.add_argument(
            "--pull", "-p", action="store_true",
            help="Try to pull the corresponding service image first.")

    @staticmethod
    def exec(args):
        if args.pull:
            s.pull_service(args.service)
        s.run_service(args.service)


class Stop(SubCommand):

    @staticmethod
    def add_args(sp):
        sp.add_argument(
            "service", type=str, nargs="?", default="all", choices=(*BENTO_DOCKER_SERVICES, "all"),
            help="Service to stop, or 'all' to stop everything.")

    @staticmethod
    def exec(args):
        s.stop_service(args.service)


class Restart(SubCommand):

    @staticmethod
    def add_args(sp):
        sp.add_argument(
            "service", type=str, nargs="?", default="all", choices=(*BENTO_DOCKER_SERVICES, "all"),
            help="Service to restart, or 'all' to restart everything.")

    @staticmethod
    def exec(args):
        s.restart_service(args.service)


class Clean(SubCommand):

    @staticmethod
    def add_args(sp):
        sp.add_argument(
            "service", type=str, choices=(*BENTO_DOCKER_SERVICES, "all"),
            help="Service to clean, or 'all' to clean everything.")

    @staticmethod
    def exec(args):
        s.clean_service(args.service)


class WorkOn(SubCommand):

    @staticmethod
    def add_args(sp):
        sp.add_argument("service", type=str, choices=BENTO_DOCKER_SERVICES, help="Service to work on.")

    @staticmethod
    def exec(args):
        s.work_on_service(args.service)


class Pull(SubCommand):

    @staticmethod
    def add_args(sp):
        sp.add_argument(
            "service", type=str, nargs="?", default="all", choices=(*BENTO_DOCKER_SERVICES, "all"),
            help="Service to pull image for.")

    @staticmethod
    def exec(args):
        s.pull_service(args.service)


class Shell(SubCommand):

    @staticmethod
    def add_args(sp):
        sp.add_argument(
            "service", type=str, choices=BENTO_DOCKER_SERVICES,
            help="Service to enter a shell for.")
        sp.add_argument(
            "--shell", "-s", default="/bin/bash", type=str, choices=("/bin/bash", "/bin/sh"),
            help="Shell to use inside the service container.")

    @staticmethod
    def exec(args):
        s.enter_shell_for_service(args.service, args.shell)


class RunShell(SubCommand):

    @staticmethod
    def add_args(sp):
        sp.add_argument(
            "service", type=str, choices=BENTO_DOCKER_SERVICES,
            help="Service to run a shell for.")
        sp.add_argument(
            "--shell", "-s", default="/bin/bash", type=str, choices=("/bin/bash", "/bin/sh"),
            help="Shell to run inside the service container.")

    @staticmethod
    def exec(args):
        s.run_as_shell_for_service(args.service, args.shell)


# Other helpers

class InitDirs(SubCommand):
    @staticmethod
    def exec(args):
        oh.init_dirs()

class InitCerts(SubCommand):
    @staticmethod
    def exec(args):
        oh.init_self_signed_certs()

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

    # Init helpers
    _add_subparser("init-dirs", "Initialize directories for BentoV2 structure.", InitDirs)
    _add_subparser("init-auth", "Configure authentication for BentoV2 with a local Keycloak instance.", InitAuth)
    _add_subparser("init-certs", "Initialize ssl certificates for bentov2 gateway domains.", InitCerts)

    # Service commands
    _add_subparser("run", "Run Bento services.", Run)
    _add_subparser("stop", "Stop Bento services.", Stop)
    _add_subparser("restart", "Restart Bento services.", Restart)
    _add_subparser("clean", "Clean services.", Clean)
    _add_subparser("work-on", "Work on a specific service in development mode.", WorkOn)
    _add_subparser("prod", "Switch a service back to production mode.", Run)  # Just an alias really
    _add_subparser("pull", "Pull the production image for a specific service.", Pull)
    _add_subparser("shell", "Run a shell inside an already-running service container.", Shell)
    _add_subparser("run-as-shell", "Run a shell inside a stopped service container.", RunShell)

    p_args = parser.parse_args(args)

    if not getattr(p_args, "func", None):
        p_args = parser.parse_args(("--help",))

    try:
        p_args.func(p_args)
    except subprocess.CalledProcessError:
        return 1

    return 0


if __name__ == "__main__":
    exit(main())

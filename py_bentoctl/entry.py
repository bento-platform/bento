from __future__ import annotations
import argparse
import subprocess
import sys

from abc import ABC, abstractmethod

from .auth_helper import init_auth
from .config import DOCKER_COMPOSE_SERVICES, BENTO_SERVICES_DATA
from . import config as c
from . import feature_helpers as fh
from . import services as s
from . import other_helpers as oh

from typing import Optional, Tuple, Type

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
            "service", type=str, nargs="?", default="all", choices=(*DOCKER_COMPOSE_SERVICES, "all"),
            help="Service to run, or 'all' to run everything.")
        sp.add_argument("--pull", "-p", action="store_true", help="Try to pull the corresponding service image first.")

    @staticmethod
    def exec(args):
        if args.pull:
            s.pull_service(args.service)

        if c.BENTO_CBIOPORTAL_ENABLED:
            fh.init_cbioportal()

        s.run_service(args.service)


class Stop(SubCommand):

    @staticmethod
    def add_args(sp):
        sp.add_argument(
            "service", type=str, nargs="?", default="all", choices=(*DOCKER_COMPOSE_SERVICES, "all"),
            help="Service to stop, or 'all' to stop everything.")

    @staticmethod
    def exec(args):
        s.stop_service(args.service)


class Restart(SubCommand):

    @staticmethod
    def add_args(sp):
        sp.add_argument(
            "service", type=str, nargs="?", default="all", choices=(*DOCKER_COMPOSE_SERVICES, "all"),
            help="Service to restart, or 'all' to restart everything.")
        sp.add_argument(
            "--pull", "-p", action="store_true",
            help="Try to pull the corresponding service image first.")

    @staticmethod
    def exec(args):
        if args.pull:
            s.pull_service(args.service)
        s.restart_service(args.service)


class Clean(SubCommand):

    @staticmethod
    def add_args(sp):
        sp.add_argument(
            "service", type=str, nargs="?", default="all", choices=(*DOCKER_COMPOSE_SERVICES, "all"),
            help="Service to clean, or 'all' to clean everything.")

    @staticmethod
    def exec(args):
        s.clean_service(args.service)


class WorkOn(SubCommand):

    @staticmethod
    def add_args(sp):
        sp.add_argument("service", type=str, choices=tuple(BENTO_SERVICES_DATA.keys()), help="Service to work on.")

    @staticmethod
    def exec(args):
        s.work_on_service(args.service)


class Prebuilt(SubCommand):

    @staticmethod
    def add_args(sp):
        sp.add_argument(
            "service", type=str, choices=tuple(BENTO_SERVICES_DATA.keys()),
            help="Service to switch to pre-built mode (will use an entirely pre-built image with code).")

    @staticmethod
    def exec(args):
        s.prod_service(args.service)


class Mode(SubCommand):

    @staticmethod
    def add_args(sp):
        sp.add_argument(
            "service", type=str, nargs="?", default="all",
            choices=(*BENTO_SERVICES_DATA.keys(), "all"),
            help="Displays the current mode of the service(s).")

    @staticmethod
    def exec(args):
        s.mode_service(args.service)


class Pull(SubCommand):

    @staticmethod
    def add_args(sp):
        sp.add_argument(
            "service", type=str, nargs="?", default="all",
            choices=(*DOCKER_COMPOSE_SERVICES, "all"), help="Service to pull image for.")

    @staticmethod
    def exec(args):
        s.pull_service(args.service)


class Shell(SubCommand):

    @staticmethod
    def add_args(sp):
        sp.add_argument("service", type=str, choices=DOCKER_COMPOSE_SERVICES, help="Service to enter a shell for.")
        sp.add_argument(
            "--shell", "-s",
            default="/bin/bash", type=str, choices=("/bin/bash", "/bin/sh"),
            help="Shell to use inside the service container.")

    @staticmethod
    def exec(args):
        s.enter_shell_for_service(args.service, args.shell)


class RunShell(SubCommand):

    @staticmethod
    def add_args(sp):
        sp.add_argument("service", type=str, choices=DOCKER_COMPOSE_SERVICES, help="Service to run a shell for.")
        sp.add_argument(
            "--shell", "-s",
            default="/bin/bash", type=str, choices=("/bin/bash", "/bin/sh"),
            help="Shell to run inside the service container.")

    @staticmethod
    def exec(args):
        s.run_as_shell_for_service(args.service, args.shell)


class Logs(SubCommand):

    @staticmethod
    def add_args(sp):
        sp.add_argument(
            "service", type=str, nargs="?", default="all", choices=(*DOCKER_COMPOSE_SERVICES, "all"),
            help="Service to check logs of.")
        sp.add_argument(
            "--follow", "-f", action="store_true",
            help="Whether to follow the logs (keep them open and show new entries).")

    @staticmethod
    def exec(args):
        s.logs_service(args.service, args.follow)


# Other helpers

class InitDirs(SubCommand):

    @staticmethod
    def exec(args):
        oh.init_dirs()


class InitCerts(SubCommand):

    @staticmethod
    def add_args(sp):
        sp.add_argument(
            "--force", "-f", action="store_true",
            help="Removes all previously created certs and keys before creating new ones.")

    @staticmethod
    def exec(args):
        oh.init_self_signed_certs(args.force)


class InitDocker(SubCommand):

    @staticmethod
    def exec(args):
        oh.init_docker()


class InitWeb(SubCommand):

    @staticmethod
    def add_args(sp):
        sp.add_argument(
            "service", type=str, choices=["public", "private"], help="Prepares the web applications for deployment.")
        sp.add_argument(
            "--force", "-f", action="store_true",
            help="Overwrites any existing branding/translation/etc.")

    @staticmethod
    def exec(args):
        oh.init_web(args.service, args.force)


class InitCBioPortal(SubCommand):

    @staticmethod
    def exec(args):
        fh.init_cbioportal()


class InitAll(SubCommand):

    @staticmethod
    def add_args(sp):
        pass

    @staticmethod
    def exec(args):
        oh.init_self_signed_certs(force=False)
        oh.init_dirs()
        oh.init_docker()
        oh.init_web("private", force=False)
        oh.init_web("public", force=False)
        if c.BENTO_CBIOPORTAL_ENABLED:
            fh.init_cbioportal()


def main(args: Optional[list[str]] = None) -> int:
    args = args or sys.argv[1:]

    # For remote interactive python debugging
    if '-d' in args or '--debug' in args:
        import debugpy

        debugpy.listen(5678)
        print("Waiting for debugger attach")
        print("Connect with a remote attach python debugger to start")
        debugpy.wait_for_client()
        debugpy.breakpoint()
        print('break on this line')

    parser = argparse.ArgumentParser(
        description="Tools for managing a Bento deployment (development or production).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("--version", "-v", action="version", version=__version__)
    parser.add_argument("--debug", "-d", action="store_true")
    subparsers = parser.add_subparsers()

    def _add_subparser(arg: str, help_text: str, subcommand: Type[SubCommand], aliases: Tuple[str, ...] = ()):
        subparser = subparsers.add_parser(arg, help=help_text, aliases=aliases)
        subparser.set_defaults(func=subcommand.exec)
        subcommand.add_args(subparser)

    # Generic initialization helpers
    _add_subparser("init-dirs", "Initialize directories for BentoV2 structure.", InitDirs)
    _add_subparser("init-auth", "Configure authentication for BentoV2 with a local Keycloak instance.", InitAuth)
    _add_subparser("init-certs", "Initialize ssl certificates for BentoV2 gateway domains.", InitCerts)
    _add_subparser("init-docker", "Initialize Docker configuration & networks.", InitDocker)
    _add_subparser("init-web", "Init web app (public or private) files", InitWeb)
    _add_subparser(
        "init-all",
        "Initialize certs, directories, Docker networks, secrets, and web portals. DOES NOT initialize Keycloak.",
        InitAll)

    # Feature-specific initialization commands
    _add_subparser("init-cbioportal", "Initialize cBioPortal if enabled", InitCBioPortal)

    # Service commands
    _add_subparser("run", "Run Bento services.", Run, aliases=("start",))
    _add_subparser("stop", "Stop Bento services.", Stop)
    _add_subparser("restart", "Restart Bento services.", Restart)
    _add_subparser("clean", "Clean services.", Clean)
    _add_subparser(
        "work-on", "Work on a specific service in a local development mode.", WorkOn, aliases=("dev", "develop"))
    _add_subparser("prebuilt", "Switch a service back to prebuilt mode.", Prebuilt, aliases=("pre-built", "prod"))
    _add_subparser(
        "mode", "See if a service (or which services) are in production/development mode.", Mode,
        aliases=("state", "status"))
    _add_subparser("pull", "Pull the production image for a specific service.", Pull)
    _add_subparser("shell", "Run a shell inside an already-running service container.", Shell, aliases=("sh",))
    _add_subparser("run-as-shell", "Run a shell inside a stopped service container.", RunShell)
    _add_subparser("logs", "Check logs for a service.", Logs)

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

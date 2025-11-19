from __future__ import annotations
import argparse
import os
import subprocess
import sys

import argcomplete

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Tuple, Type

# Lazy imports - these modules are heavy and slow down tab completion
# They will be imported on first use in the functions that need them
_config = None
_db_helpers = None
_feature_helpers = None
_services = None
_other_helpers = None
_utils = None
_auth_helper = None


def _get_config():
    global _config
    if _config is None:
        from . import config as c
        _config = c
    return _config


def _get_db_helpers():
    global _db_helpers
    if _db_helpers is None:
        from . import db_helpers as dh
        _db_helpers = dh
    return _db_helpers


def _get_feature_helpers():
    global _feature_helpers
    if _feature_helpers is None:
        from . import feature_helpers as fh
        _feature_helpers = fh
    return _feature_helpers


def _get_services():
    global _services
    if _services is None:
        from . import services as s
        _services = s
    return _services


def _get_other_helpers():
    global _other_helpers
    if _other_helpers is None:
        from . import other_helpers as oh
        _other_helpers = oh
    return _other_helpers


def _get_utils():
    global _utils
    if _utils is None:
        from . import utils as u
        _utils = u
    return _utils


def _get_auth_helper():
    global _auth_helper
    if _auth_helper is None:
        from .auth_helper import init_auth
        _auth_helper = init_auth
    return _auth_helper


# Static service lists for fast completions (these don't require loading config)
# These are used during tab completion to avoid loading the heavy config module
STATIC_ALL_SERVICES = (
    "all", "aggregation", "auth", "auth-db", "authz", "authz-db", "beacon",
    "cbioportal", "drs", "drop-box", "event-relay", "gateway", "gohan",
    "gohan-api", "gohan-elasticsearch", "katsu", "katsu-db", "notification",
    "public", "redis", "reference", "reference-db", "service-registry", "web", "wes"
)

STATIC_WORKABLE_SERVICES = (
    "aggregation", "authz", "beacon", "drs", "drop-box", "event-relay",
    "gateway", "gohan-api", "katsu", "notification", "public", "reference",
    "service-registry", "web", "wes"
)

STATIC_MULTI_SERVICE_PREFIXES = ("gohan",)


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
        _get_auth_helper()(docker_client=_get_utils().get_docker_client())


class Run(SubCommand):

    @staticmethod
    def add_args(sp):
        sp.add_argument(
            "service", type=str, nargs="?", default="all", choices=STATIC_ALL_SERVICES,
            help="Service to run, or 'all' to run everything.")
        sp.add_argument("--pull", "-p", action="store_true", help="Try to pull the corresponding service image first.")

    @staticmethod
    def exec(args):
        c = _get_config()
        s = _get_services()
        if args.pull:
            s.pull_service(args.service)

        if c.BENTO_FEATURE_CBIOPORTAL.enabled:
            _get_feature_helpers().init_cbioportal()

        s.run_service(args.service)


class Stop(SubCommand):

    @staticmethod
    def add_args(sp):
        sp.add_argument(
            "service", type=str, nargs="?", default="all", choices=STATIC_ALL_SERVICES,
            help="Service to stop, or 'all' to stop everything.")

    @staticmethod
    def exec(args):
        _get_services().stop_service(args.service)


class Restart(SubCommand):

    @staticmethod
    def add_args(sp):
        sp.add_argument(
            "service", type=str, nargs="?", default="all", choices=STATIC_ALL_SERVICES,
            help="Service to restart, or 'all' to restart everything.")
        sp.add_argument(
            "--pull", "-p", action="store_true",
            help="Try to pull the corresponding service image first.")

    @staticmethod
    def exec(args):
        s = _get_services()
        if args.pull:
            s.pull_service(args.service)
        s.restart_service(args.service)


class Clean(SubCommand):

    @staticmethod
    def add_args(sp):
        sp.add_argument(
            "service", type=str, nargs="?", default="all", choices=STATIC_ALL_SERVICES,
            help="Service to clean, or 'all' to clean everything.")

    @staticmethod
    def exec(args):
        _get_services().clean_service(args.service)


class WorkOn(SubCommand):

    @staticmethod
    def add_args(sp):
        sp.add_argument("service", type=str, choices=STATIC_WORKABLE_SERVICES, help="Service to work on.")

    @staticmethod
    def exec(args):
        _get_services().work_on_service(args.service)


class Prebuilt(SubCommand):

    @staticmethod
    def add_args(sp):
        sp.add_argument(
            "service", type=str, choices=STATIC_ALL_SERVICES,
            help="Service to switch to pre-built mode (will use an entirely pre-built image with code).")

    @staticmethod
    def exec(args):
        _get_services().prod_service(args.service)


class Mode(SubCommand):

    @staticmethod
    def add_args(sp):
        sp.add_argument(
            "service", type=str, nargs="?", default="all",
            choices=STATIC_ALL_SERVICES,
            help="Displays the current mode of the service(s).")

    @staticmethod
    def exec(args):
        _get_services().mode_service(args.service)


class Pull(SubCommand):

    @staticmethod
    def add_args(sp):
        sp.add_argument(
            "service", type=str, nargs="?", default="all",
            choices=STATIC_ALL_SERVICES,
            help="Service to pull image for.")

    @staticmethod
    def exec(args):
        _get_services().pull_service(args.service)


class Shell(SubCommand):

    @staticmethod
    def add_args(sp):
        # Exclude "all" from shell choices - can only shell into one service
        shell_services = tuple(s for s in STATIC_ALL_SERVICES if s != "all")
        sp.add_argument("service", type=str, choices=shell_services, help="Service to enter a shell for.")
        sp.add_argument(
            "--shell", "-s",
            default="/bin/bash", type=str, choices=("/bin/bash", "/bin/sh"),
            help="Shell to use inside the service container.")

    @staticmethod
    def exec(args):
        _get_services().enter_shell_for_service(args.service, args.shell)


class RunShell(SubCommand):

    @staticmethod
    def add_args(sp):
        # Exclude "all" from shell choices - can only shell into one service
        shell_services = tuple(s for s in STATIC_ALL_SERVICES if s != "all")
        sp.add_argument("service", type=str, choices=shell_services, help="Service to run a shell for.")
        sp.add_argument(
            "--shell", "-s",
            default="/bin/bash", type=str, choices=("/bin/bash", "/bin/sh"),
            help="Shell to run inside the service container.")

    @staticmethod
    def exec(args):
        _get_services().run_as_shell_for_service(args.service, args.shell)


class Logs(SubCommand):

    @staticmethod
    def add_args(sp):
        sp.add_argument(
            "service", type=str, nargs="?", default="all", choices=STATIC_ALL_SERVICES,
            help="Service to check logs of.")
        sp.add_argument(
            "--follow", "-f", action="store_true",
            help="Whether to follow the logs (keep them open and show new entries).")

    @staticmethod
    def exec(args):
        _get_services().logs_service(args.service, args.follow)


class ComposeConfig(SubCommand):

    @staticmethod
    def add_args(sp):
        sp.add_argument("--services", action="store_true", help="List services seen by Compose.")

    @staticmethod
    def exec(args):
        _get_services().compose_config(args.services)


# Other helpers

class InitDirs(SubCommand):

    @staticmethod
    def exec(args):
        _get_other_helpers().init_dirs()


class InitCerts(SubCommand):

    @staticmethod
    def add_args(sp):
        sp.add_argument(
            "--force", "-f", action="store_true",
            help="Removes all previously created certs and keys before creating new ones.")

    @staticmethod
    def exec(args):
        _get_other_helpers().init_self_signed_certs(args.force)


class InitDocker(SubCommand):

    @staticmethod
    def exec(args):
        _get_other_helpers().init_docker(client=_get_utils().get_docker_client())


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
        _get_other_helpers().init_web(args.service, args.force)


class InitCBioPortal(SubCommand):

    @staticmethod
    def exec(args):
        _get_feature_helpers().init_cbioportal()


class InitAll(SubCommand):

    @staticmethod
    def add_args(sp):
        pass

    @staticmethod
    def exec(args):
        oh = _get_other_helpers()
        oh.init_self_signed_certs(force=False)
        oh.init_dirs()
        oh.init_docker(client=_get_utils().get_docker_client())
        oh.init_web("private", force=False)
        oh.init_web("public", force=False)
        if _get_config().BENTO_FEATURE_CBIOPORTAL.enabled:
            _get_feature_helpers().init_cbioportal()


class InitConfig(SubCommand):

    @staticmethod
    def add_args(sp):
        sp.add_argument(
            "service",
            type=str,
            choices=["katsu", "beacon", "beacon-network"],
            help="Prepares services for deployment."
        )
        sp.add_argument(
            "--force", "-f", action="store_true",
            help="Overwrites any existing config.")

    @staticmethod
    def exec(args):
        _get_other_helpers().init_config(args.service, args.force)


class PgDump(SubCommand):

    @staticmethod
    def add_args(sp):
        sp.add_argument("dir", type=Path, help="Path to a new directory for the database dump files.")

    @staticmethod
    def exec(args):
        _get_db_helpers().pg_dump(args.dir)


class PgLoad(SubCommand):

    @staticmethod
    def add_args(sp):
        sp.add_argument("dir", type=Path, help="Path to a directory to load the database dump files from.")

    @staticmethod
    def exec(args):
        _get_db_helpers().pg_load(args.dir)


class ConvertPhenopacket(SubCommand):

    @staticmethod
    def add_args(sp):
        sp.add_argument("source", type=str, help="Source Phenopackets V1 JSON document to convert")
        sp.add_argument("target", nargs="?", default=None, type=str,
                        help="Optional target file path where to place the converted Phenopackets")

    @staticmethod
    def exec(args):
        # import asyncio
        # TODO: re-convert to async
        # asyncio.run(oh.convert_phenopacket_file(args.source, args.target))
        _get_other_helpers().convert_phenopacket_file(args.source, args.target)


def main(args: Optional[list[str]] = None) -> int:
    args = args or sys.argv[1:]

    # For remote interactive python debugging
    if "-d" in args or "--debug" in args:
        import debugpy

        debugpy.listen(5678)
        print("Waiting for debugger attach")
        print("Connect with a remote attach python debugger to start")
        debugpy.wait_for_client()
        debugpy.breakpoint()
        print("break on this line")

    parser = argparse.ArgumentParser(
        description="Tools for managing a Bento deployment (development or production).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

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
    _add_subparser("init-config", "Initialize configuration files for specific services.", InitConfig)

    # Feature-specific initialization commands
    _add_subparser("init-cbioportal", "Initialize cBioPortal if enabled", InitCBioPortal)

    # Database commands
    #  - Postgres:
    _add_subparser("pg-dump", "Dump contents of all Postgres database containers to a directory.", PgDump)
    _add_subparser("pg-load", "Load contents of all Postgres database containers from a directory.", PgLoad)

    # Other commands
    _add_subparser("convert-pheno",
                   "Convert a Phenopacket V1 JSON document to V2", ConvertPhenopacket, aliases=("conv",))

    # Service commands
    _add_subparser("run", "Run Bento services.", Run, aliases=("start", "up"))
    _add_subparser("stop", "Stop Bento services.", Stop, aliases=("down",))
    _add_subparser("restart", "Restart Bento services.", Restart)
    _add_subparser("clean", "Clean services.", Clean)
    _add_subparser(
        "work-on", "Work on a specific service in a local development mode.", WorkOn,
        aliases=("dev", "develop", "local"))
    _add_subparser("prebuilt", "Switch a service back to prebuilt mode.", Prebuilt, aliases=("pre-built", "prod"))
    _add_subparser(
        "mode", "See if a service (or which services) are in production/development mode.", Mode,
        aliases=("state", "status"))
    _add_subparser("pull", "Pull the image for a specific service.", Pull)
    _add_subparser("shell", "Run a shell inside an already-running service container.", Shell, aliases=("sh",))
    _add_subparser("run-as-shell", "Run a shell inside a stopped service container.", RunShell)
    _add_subparser("logs", "Check logs for a service.", Logs)
    _add_subparser("compose-config", "Generate Compose config YAML.", ComposeConfig)

    argcomplete.autocomplete(parser)
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

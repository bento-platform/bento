import os
import pathlib
import subprocess

from termcolor import cprint

from .config import BENTO_DOCKER_SERVICES, COMPOSE, BENTO_SERVICES_DATA

__all__ = [
    "run_service",
    "stop_service",
    "restart_service",
    "clean_service",
    "work_on_service",
    "enter_shell_for_service",
    "run_as_shell_for_service",
]


def run_service(service: str):
    if service == "all":
        # special: run everything
        subprocess.check_call((*COMPOSE, "up", "-d"))
        return

    if service not in BENTO_DOCKER_SERVICES:
        cprint(f"  {service} not in list of services: {BENTO_DOCKER_SERVICES}", "red")
        exit(1)

    print(f"Running {service}...")
    subprocess.check_call((*COMPOSE, "up", "-d", service))


def stop_service(service: str):
    if service == "all":
        # special: stop everything
        subprocess.check_call((*COMPOSE, "down"))
        return

    if service not in BENTO_DOCKER_SERVICES:
        cprint(f"  {service} not in list of services: {BENTO_DOCKER_SERVICES}", "red")
        exit(1)

    print(f"Stopping {service}...")
    subprocess.check_call((*COMPOSE, "stop", service))


def restart_service(service: str):
    stop_service(service)
    run_service(service)


def clean_service(service: str):
    if service == "all":
        # special: stop everything
        for s in BENTO_DOCKER_SERVICES:
            clean_service(s)
        return

    if service not in BENTO_DOCKER_SERVICES:
        cprint(f"  {service} not in list of services: {BENTO_DOCKER_SERVICES}")
        exit(1)

    print(f"Stopping {service}...")
    subprocess.check_call((*COMPOSE, "rm", "-svf", service))


def work_on_service(service: str):
    if service == "all":
        cprint(f"  Cannot work on all services.", "red")
        exit(1)

    if service not in BENTO_DOCKER_SERVICES:
        cprint(f"  {service} not in list of services: {BENTO_DOCKER_SERVICES}")
        exit(1)

    repo_path = pathlib.Path.cwd() / "repos" / service

    if not repo_path.exists():
        # Clone the repository if it doesn't already exist
        cprint(f"  Cloning {service} repository into repos/ ...", "blue")
        subprocess.check_call(("git", "clone"))
        # TODO

    print(f"Running {service} in development mode...")
    subprocess.check_call((
        *COMPOSE,
        "up",
        "-f", "docker-compose.yaml",
        "-f", "docker-compose.dev.yaml",
        "-d", service,
    ))


def enter_shell_for_service(service: str, shell: str):
    if service not in BENTO_DOCKER_SERVICES:
        cprint(f"  {service} not in list of services: {BENTO_DOCKER_SERVICES}")
        exit(1)

    cmd = COMPOSE[0]
    compose_args = COMPOSE[1:]
    os.execvp(cmd, (cmd, *compose_args, "exec", "-it", service, shell))  # TODO: Detect shell


def run_as_shell_for_service(service: str, shell: str):
    if service not in BENTO_DOCKER_SERVICES:
        cprint(f"  {service} not in list of services: {BENTO_DOCKER_SERVICES}")
        exit(1)

    cmd = COMPOSE[0]
    compose_args = COMPOSE[1:]
    os.execvp(cmd, (cmd, *compose_args, "run", service, shell))  # TODO: Detect shell

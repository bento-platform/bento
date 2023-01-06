import os
import subprocess

from termcolor import cprint

from .config import BENTO_DOCKER_SERVICES, COMPOSE

__all__ = [
    "run_service",
    "stop_service",
    "clean_service",
    "enter_shell_for_service",
    "run_as_shell_for_service",
]


def run_service(service: str):
    if service == "all":
        # special: run everything
        for s in BENTO_DOCKER_SERVICES:
            run_service(s)
        return

    if service not in BENTO_DOCKER_SERVICES:
        cprint(f"  {service} not in list of services: {BENTO_DOCKER_SERVICES}")
        exit(1)

    print(f"Running {service}...")
    subprocess.check_call((*COMPOSE, "up", "-d", service))


def stop_service(service: str):
    if service == "all":
        # special: stop everything
        subprocess.check_call((*COMPOSE, "down"))

    if service not in BENTO_DOCKER_SERVICES:
        cprint(f"  {service} not in list of services: {BENTO_DOCKER_SERVICES}")
        exit(1)

    print(f"Stopping {service}...")
    subprocess.check_call((*COMPOSE, "stop", service))


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

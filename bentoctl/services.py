import subprocess

from termcolor import cprint

from .config import BENTO_DOCKER_SERVICES, COMPOSE

__all__ = [
    "run_service",
    "stop_service",
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
    subprocess.check_call((*COMPOSE, "down", service))

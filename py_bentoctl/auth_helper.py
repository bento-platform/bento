#!/usr/bin/env python3

import docker
import os
import requests
import subprocess
import sys
import urllib3

from termcolor import cprint

from typing import Optional

from .config import COMPOSE, MODE, DEV_MODE
from .utils import err

__all__ = ["init_auth"]

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

USE_EXTERNAL_IDP = os.getenv("BENTOV2_USE_EXTERNAL_IDP")
CLIENT_ID = os.getenv("BENTOV2_AUTH_CLIENT_ID")

PORTAL_PUBLIC_URL = os.getenv("BENTOV2_PORTAL_PUBLIC_URL")

AUTH_REALM = os.getenv("BENTOV2_AUTH_REALM")
AUTH_CLIENT_ID = os.getenv("BENTOV2_AUTH_CLIENT_ID")
AUTH_PUBLIC_URL = os.getenv("BENTOV2_AUTH_PUBLIC_URL")
AUTH_LOGIN_REDIRECT_PATH = os.getenv("BENTOV2_AUTH_LOGIN_REDIRECT_PATH")
AUTH_VOL_DIR = os.getenv("BENTOV2_AUTH_VOL_DIR")
AUTH_ADMIN_USER = os.getenv("BENTOV2_AUTH_ADMIN_USER")
AUTH_ADMIN_PASSWORD = os.getenv("BENTOV2_AUTH_ADMIN_PASSWORD")
AUTH_TEST_USER = os.getenv("BENTOV2_AUTH_TEST_USER")
AUTH_TEST_PASSWORD = os.getenv("BENTOV2_AUTH_TEST_PASSWORD")
AUTH_CONTAINER_NAME = os.getenv("BENTOV2_AUTH_CONTAINER_NAME")


if not AUTH_ADMIN_USER:
    err("Missing environment value for BENTOV2_AUTH_ADMIN_USER")
    exit(1)


docker_client = docker.from_env()


def make_keycloak_url(path: str) -> str:
    return f"{AUTH_PUBLIC_URL}/{path.lstrip('/')}"


def keycloak_req(
    path: str,
    method: str = "get",
    headers: Optional[dict] = None,
    bearer_token: Optional[str] = None,
    data: Optional[dict] = None,
    json: Optional[dict] = None,
) -> requests.Response:
    method = method.lower()

    if bearer_token:
        if not headers:
            headers = {}
        headers["Authorization"] = f"Bearer {bearer_token}"

    kwargs = dict(**(dict(headers=headers) if headers else {}), verify=not DEV_MODE)

    if method == "get":
        return requests.get(make_keycloak_url(path), **kwargs)
    if method == "post":
        return requests.post(
            make_keycloak_url(path),
            **(dict(data=data) if data else {}),
            **(dict(json=json) if json else {}),
            **kwargs)

    raise NotImplementedError


def init_auth():
    def get_session():
        res = keycloak_req("realms/master/protocol/openid-connect/token", method="post", data=dict(
            client_id="admin-cli",
            username=AUTH_ADMIN_USER,
            password=AUTH_ADMIN_PASSWORD,
            grant_type="password",
        ))

        if not res.ok:
            err(f"  Failed to sign in as {AUTH_ADMIN_USER}; {res.json()}")
            exit(1)

        return res.json()

    def create_realm_if_needed(token: str) -> None:
        existing_realms_res = keycloak_req("admin/realms", bearer_token=token)
        existing_realms = existing_realms_res.json()

        if not existing_realms_res.ok:
            err(f"    Failed to fetch existing realms: {existing_realms}")
            exit(1)

        for r in existing_realms:
            if r["realm"] == AUTH_REALM:
                cprint(f"    Found existing realm: {AUTH_REALM}; using that.", "yellow")
                return

        create_realm_res = keycloak_req("admin/realms", method="post", bearer_token=token, json={
            "realm": AUTH_REALM,
            "enabled": True,
            "editUsernameAllowed": False,
            "resetPasswordAllowed": False,
        })

        if not create_realm_res.ok:
            cprint(f"    Failed to create realm: {AUTH_REALM}; {create_realm_res.json()}", "red", file=sys.stderr)
            exit(1)

    def create_web_client_if_needed(token: str) -> str:
        p = f"admin/realms/{AUTH_REALM}/clients"

        def fetch_existing_client_id() -> Optional[str]:
            existing_clients_res = keycloak_req(p, bearer_token=token)
            existing_clients = existing_clients_res.json()

            if not existing_clients_res.ok:
                cprint(f"    Failed to fetch existing clients: {existing_clients}", "red", file=sys.stderr)
                exit(1)

            for c in existing_clients:
                if c["clientId"] == AUTH_CLIENT_ID:
                    cprint(f"    Found existing client: {AUTH_CLIENT_ID}; using that.", "yellow")
                    return c["id"]

            return None

        client_kc_id: Optional[str] = fetch_existing_client_id()
        if client_kc_id is None:
            create_client_res = keycloak_req(p, bearer_token=token, method="post", json={
                "clientId": AUTH_CLIENT_ID,
                "enabled": True,
                "protocol": "openid-connect",
                "implicitFlowEnabled": False,  # don't support insecure old implicit flow
                "standardFlowEnabled": True,
                "publicClient": False,
                "redirectUris": [
                    f"{PORTAL_PUBLIC_URL}{AUTH_LOGIN_REDIRECT_PATH}"
                ],
                "webOrigins": [
                    f"{PORTAL_PUBLIC_URL}",
                ],
                "attributes": {
                    "saml.assertion.signature": "false",
                    "saml.authnstatement": "false",
                    "saml.client.signature": "false",
                    "saml.encrypt": "false",
                    "saml.force.post.binding": "false",
                    "saml.multivalued.roles": "false",
                    "saml.onetimeuse.condition": "false",
                    "saml.server.signature": "false",
                    "saml.server.signature.keyinfo.ext": "false",
                    "saml_force_name_id_format": "false"
                }
            })
            if not create_client_res.ok:
                cprint(f"    Failed to create client: {AUTH_CLIENT_ID}; {create_client_res.json()}", "red",
                       file=sys.stderr)
                exit(1)

            client_kc_id = fetch_existing_client_id()

        # Fetch and return secret
        client_secret_res = keycloak_req(f"{p}/{client_kc_id}/client-secret", bearer_token=token)
        client_secret_data = client_secret_res.json()
        if not client_secret_res.ok:
            cprint(f"    Failed to get client secret for {AUTH_CLIENT_ID}; {client_secret_data}")
            exit(1)

        return client_secret_data["value"]

    def create_test_user_if_needed(token: str) -> None:
        p = f"admin/realms/{AUTH_REALM}/users"

        existing_users_res = keycloak_req(p, bearer_token=token)
        existing_users = existing_users_res.json()

        if not existing_users_res.ok:
            cprint(f"    Failed to fetch existing users: {existing_users}", "red", file=sys.stderr)
            exit(1)

        for u in existing_users:
            if u["username"] == AUTH_TEST_USER:
                cprint(f"    Found existing user: {AUTH_TEST_USER}; using that.", "yellow")
                return

        create_user_res = keycloak_req(p, bearer_token=token, method="post", json={
            "username": AUTH_TEST_USER,
            "enabled": True,
            "credentials": [{"type": "password", "value": AUTH_TEST_PASSWORD, "temporary": False}],
        })
        if not create_user_res.ok:
            cprint(f"    Failed to create user: {AUTH_TEST_USER}; {create_user_res.json()}", "red",
                   file=sys.stderr)
            exit(1)

    def success():
        cprint(f"    Success.", "green")

    if USE_EXTERNAL_IDP in ("1", "true"):
        print("Using external IdP, skipping setup.")
        exit(0)

    print(f"[bentoctl] Using internal IdP, setting up Keycloak...    (MODE={MODE})")

    try:
        docker_client.containers.get(AUTH_CONTAINER_NAME)
    except requests.exceptions.HTTPError:
        print(f"  Starting {AUTH_CONTAINER_NAME}...")
        # Not found, so we need to start it
        subprocess.check_call((*COMPOSE, "up", "-d", "auth"))
        success()

    print(f"  Signing in as {AUTH_ADMIN_USER}...")
    session = get_session()
    access_token = session["access_token"]
    success()

    print(f"  Creating realm: {AUTH_REALM}")
    create_realm_if_needed(access_token)
    success()

    print(f"  Creating web client: {AUTH_CLIENT_ID}")
    client_secret = create_web_client_if_needed(access_token)
    cprint(f"    Please set CLIENT_SECRET to {client_secret} in local.env and restart the gateway",
           "black", attrs=["bold"])
    success()

    print(f"  Creating user: {AUTH_TEST_USER}")
    create_test_user_if_needed(access_token)
    success()

    print(f"  Restarting the Keycloak container")
    try:
        kc = docker_client.containers.get(AUTH_CONTAINER_NAME)
        kc.restart()
        success()
    except requests.exceptions.HTTPError:
        # Not found
        cprint(f"    Could not find container: {AUTH_CONTAINER_NAME}. Is it running?", "red")

    cprint("Done.", "green")

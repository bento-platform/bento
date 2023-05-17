#!/usr/bin/env python3

import docker
import os
import requests
import subprocess
import urllib3

from termcolor import cprint
from urllib3.exceptions import InsecureRequestWarning

from typing import Optional

from . import config as c
from .utils import info, warn, err

__all__ = ["init_auth"]

urllib3.disable_warnings(InsecureRequestWarning)

USE_EXTERNAL_IDP = os.getenv("BENTOV2_USE_EXTERNAL_IDP")
CLIENT_ID = os.getenv("BENTOV2_AUTH_CLIENT_ID")

PORTAL_PUBLIC_URL = os.getenv("BENTOV2_PORTAL_PUBLIC_URL")
CBIOPORTAL_URL = os.getenv("BENTO_CBIOPORTAL_PUBLIC_URL")

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


def check_auth_admin_user():
    if not AUTH_ADMIN_USER:
        err("Missing environment value for BENTOV2_AUTH_ADMIN_USER")
        exit(1)


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

    kwargs = dict(**(dict(headers=headers) if headers else {}), verify=not c.DEV_MODE)

    if method == "get":
        return requests.get(make_keycloak_url(path), **kwargs)
    if method == "post":
        return requests.post(
            make_keycloak_url(path),
            **(dict(data=data) if data else {}),
            **(dict(json=json) if json else {}),
            **kwargs)

    raise NotImplementedError


def init_auth(docker_client: docker.DockerClient):
    check_auth_admin_user()

    def get_session():
        res = keycloak_req(
            "realms/master/protocol/openid-connect/token",
            method="post",
            data=dict(
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

        for realm in existing_realms:
            if realm["realm"] == AUTH_REALM:
                warn(f"    Found existing realm: {AUTH_REALM}; using that.")
                return

        create_realm_res = keycloak_req(
            "admin/realms",
            method="post",
            bearer_token=token,
            json={
                "realm": AUTH_REALM,
                "enabled": True,
                "editUsernameAllowed": False,
                "resetPasswordAllowed": False,
            })

        if not create_realm_res.ok:
            err(f"    Failed to create realm: {AUTH_REALM}; {create_realm_res.json()}")
            exit(1)

    def create_web_client_if_needed(token: str) -> None:
        p = f"admin/realms/{AUTH_REALM}/clients"

        def fetch_existing_client_id() -> Optional[str]:
            existing_clients_res = keycloak_req(p, bearer_token=token)
            existing_clients = existing_clients_res.json()

            if not existing_clients_res.ok:
                err(f"    Failed to fetch existing clients: {existing_clients}")
                exit(1)

            for client in existing_clients:
                if client["clientId"] == AUTH_CLIENT_ID:
                    warn(f"    Found existing client: {AUTH_CLIENT_ID}; using that.")
                    return client["id"]

            return None

        client_kc_id: Optional[str] = fetch_existing_client_id()
        if client_kc_id is None:
            cbio_enabled = c.BENTO_FEATURE_CBIOPORTAL.enabled
            create_client_res = keycloak_req(p, bearer_token=token, method="post", json={
                "clientId": AUTH_CLIENT_ID,
                "enabled": True,
                "protocol": "openid-connect",
                "implicitFlowEnabled": False,  # don't support insecure old implicit flow
                "standardFlowEnabled": True,
                "publicClient": True,  # public client - web now uses auth code + PKCE flow
                "redirectUris": [
                    f"{PORTAL_PUBLIC_URL}{AUTH_LOGIN_REDIRECT_PATH}",
                    *((f"{CBIOPORTAL_URL}{AUTH_LOGIN_REDIRECT_PATH}",) if cbio_enabled else ()),
                ],
                "webOrigins": [
                    f"{PORTAL_PUBLIC_URL}",
                    *((f"{CBIOPORTAL_URL}",) if cbio_enabled else ()),
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
                    "saml_force_name_id_format": "false",

                    "access.token.lifespan": 900,  # default access token lifespan: 15 minutes
                    "pkce.code.challenge.method": "S256",
                    "use.refresh.tokens": "true",
                }
            })
            if not create_client_res.ok:
                err(f"    Failed to create client: {AUTH_CLIENT_ID}; {create_client_res.json()}")
                exit(1)

            client_kc_id = fetch_existing_client_id()

        # Fetch and return secret
        client_secret_res = keycloak_req(f"{p}/{client_kc_id}/client-secret", bearer_token=token)
        client_secret_data = client_secret_res.json()
        if not client_secret_res.ok:
            err(f"    Failed to get client secret for {AUTH_CLIENT_ID}; {client_secret_data}")
            exit(1)

    def create_test_user_if_needed(token: str) -> None:
        p = f"admin/realms/{AUTH_REALM}/users"

        existing_users_res = keycloak_req(p, bearer_token=token)
        existing_users = existing_users_res.json()

        if not existing_users_res.ok:
            err(f"    Failed to fetch existing users: {existing_users}")
            exit(1)

        for u in existing_users:
            if u["username"] == AUTH_TEST_USER:
                warn(f"    Found existing user: {AUTH_TEST_USER}; using that.")
                return

        create_user_res = keycloak_req(
            p,
            bearer_token=token,
            method="post",
            json={
                "username": AUTH_TEST_USER,
                "enabled": True,
                "credentials": [
                    {
                        "type": "password",
                        "value": AUTH_TEST_PASSWORD,
                        "temporary": False
                    }
                ],
            })
        if not create_user_res.ok:
            err(f"    Failed to create user: {AUTH_TEST_USER}; {create_user_res.json()}")
            exit(1)

    def success():
        cprint("    Success.", "green")

    if USE_EXTERNAL_IDP in ("1", "true"):
        info("Using external IdP, skipping setup.")
        exit(0)

    info(f"[bentoctl] Using internal IdP, setting up Keycloak...    (DEV_MODE={c.DEV_MODE})")

    try:
        docker_client.containers.get(AUTH_CONTAINER_NAME)
    except requests.exceptions.HTTPError:
        info(f"  Starting {AUTH_CONTAINER_NAME}...")
        # Not found, so we need to start it
        subprocess.check_call((*c.COMPOSE, "up", "-d", "auth"))
        success()

    info(f"  Signing in as {AUTH_ADMIN_USER}...")
    session = get_session()
    access_token = session["access_token"]
    success()

    info(f"  Creating realm: {AUTH_REALM}")
    create_realm_if_needed(access_token)
    success()

    info(f"  Creating web client: {AUTH_CLIENT_ID}")
    create_web_client_if_needed(access_token)
    success()

    info(f"  Creating user: {AUTH_TEST_USER}")
    create_test_user_if_needed(access_token)
    success()

    info("  Restarting the Keycloak container")
    try:
        kc = docker_client.containers.get(AUTH_CONTAINER_NAME)
        kc.restart()
        success()
    except requests.exceptions.HTTPError:
        # Not found
        err(f"    Could not find container: {AUTH_CONTAINER_NAME}. Is it running?")

    cprint("Done.", "green")

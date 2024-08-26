#!/usr/bin/env python3

import docker
import os
import requests
import subprocess
import urllib3

from termcolor import cprint
from urllib3.exceptions import InsecureRequestWarning

from typing import List, Optional

from . import config as c
from .utils import info, warn, err

__all__ = ["init_auth"]

urllib3.disable_warnings(InsecureRequestWarning)

USE_EXTERNAL_IDP = os.getenv("BENTOV2_USE_EXTERNAL_IDP")
CLIENT_ID = os.getenv("BENTOV2_AUTH_CLIENT_ID")

PUBLIC_URL = os.getenv("BENTOV2_PUBLIC_URL")
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

CBIOPORTAL_CLIENT_ID = os.getenv("BENTO_CBIOPORTAL_CLIENT_ID")

WES_CLIENT_ID = os.getenv("BENTO_WES_CLIENT_ID")
WES_WORKFLOW_TIMEOUT = int(os.getenv("BENTOV2_WES_WORKFLOW_TIMEOUT"))

GRAFANA_CLIENT_ID = os.getenv("BENTO_GRAFANA_CLIENT_ID")
GRAFANA_PRIVATE_URL = os.getenv("BENTO_PRIVATE_GRAFANA_URL")

KC_ADMIN_API_ENDPOINT = f"admin/realms/{AUTH_REALM}"
KC_ADMIN_API_GROUP_ENDPOINT = f"{KC_ADMIN_API_ENDPOINT}/groups"
KC_ADMIN_API_CLIENTS_ENDPOINT = f"{KC_ADMIN_API_ENDPOINT}/clients"


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


def fetch_existing_client_id(token: str, client_id: str) -> Optional[str]:
    existing_clients_res = keycloak_req(KC_ADMIN_API_CLIENTS_ENDPOINT, bearer_token=token)
    existing_clients = existing_clients_res.json()

    if not existing_clients_res.ok:
        err(f"    Failed to fetch existing clients: {existing_clients}")
        exit(1)

    for client in existing_clients:
        if client["clientId"] == client_id:
            warn(f"    Found existing client: {client_id}; using that.")
            return client["id"]

    return None


def fetch_existing_group_id(token: str, group_name: str,
                            parent_id: str | None = None, verbose: bool = True) -> Optional[str]:
    endpoint = f"{KC_ADMIN_API_GROUP_ENDPOINT}/{parent_id}/children" if parent_id else KC_ADMIN_API_GROUP_ENDPOINT
    existing_groups_res = keycloak_req(endpoint, bearer_token=token)

    if not existing_groups_res.ok:
        err(f"    Failed to fetch group id associated with name: {group_name}")
        exit(1)

    exising_groups = existing_groups_res.json()
    for group in exising_groups:
        if group["name"] == group_name:
            if verbose:
                warn(f"    Found existing group: {group_name}; using that.")
            return group["id"]

    return None


def create_client_role_or_exit(token: str, client_id: str, role_name: str) -> None:
    client_roles_endpoint = f"{KC_ADMIN_API_CLIENTS_ENDPOINT}/{client_id}/roles"

    # Check if client role exists
    existing_role_res = keycloak_req(f"{client_roles_endpoint}/{role_name}", bearer_token=token,)
    if existing_role_res.ok:
        warn(f"    Found existing role: {role_name}; using that.")
        return

    # Create client role if needed
    res = keycloak_req(client_roles_endpoint, bearer_token=token, method="post", json={
        "clientRole": True,
        "name": role_name,
    })

    if not res.ok:
        err(f"    Failed to create {client_id} client role : {role_name}; {res.status_code} {res.json()}")
        exit(1)

    warn(f"    Created role: {role_name}.")


def create_group_or_exit(token: str, group_representation: dict, parent_id: str = None) -> Optional[str]:
    group_endpoint = f"{KC_ADMIN_API_GROUP_ENDPOINT}/{parent_id}/children" if parent_id else KC_ADMIN_API_GROUP_ENDPOINT
    group_type = f"sub-group of {parent_id}" if parent_id else "group"

    if existing_group_id := fetch_existing_group_id(token, group_representation["name"], parent_id):
        return existing_group_id

    res = keycloak_req(f"{group_endpoint}", bearer_token=token, method="post", json=group_representation)

    # group creation doesn't return the ID of the newly created group, extra request is required to obtain it
    created_group_id = fetch_existing_group_id(token, group_representation["name"], parent_id, verbose=False)
    if not res.ok or not created_group_id:
        err(f"    Failed to create {group_type}: {group_representation}; {res.status_code}")
        exit(1)

    warn(f"    Created {group_type}: {group_representation['name']}")
    return created_group_id


def create_keycloak_client_or_exit(
    token: str,
    client_id: str,
    public_client: bool,
    standard_flow_enabled: bool,
    service_accounts_enabled: bool,
    redirect_uris: List[str],
    web_origins: List[str],
    access_token_lifespan: int,
    use_refresh_tokens: bool,
) -> None:
    res = keycloak_req(KC_ADMIN_API_CLIENTS_ENDPOINT, bearer_token=token, method="post", json={
        "clientId": client_id,
        "enabled": True,
        "protocol": "openid-connect",
        "implicitFlowEnabled": False,  # don't support insecure old implicit flow
        "directAccessGrantsEnabled": False,  # don't support insecure old resource owner password flow
        "standardFlowEnabled": standard_flow_enabled,
        "serviceAccountsEnabled": service_accounts_enabled,
        "publicClient": public_client,  # if public client - uses auth code + PKCE flow rather than client secret
        "redirectUris": redirect_uris,
        "webOrigins": web_origins,
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

            **({
                # Allowed redirect_uri values when using the logout endpoint from Keycloak
                "post.logout.redirect.uris": "##".join(redirect_uris),
            } if standard_flow_enabled else {}),

            "access.token.lifespan": access_token_lifespan,  # default access token lifespan: 15 minutes
            "pkce.code.challenge.method": "S256",
            "use.refresh.tokens": str(use_refresh_tokens).lower(),

            **({
                "client_credentials.use_refresh_token": "false",
            } if service_accounts_enabled else {}),
        }
    })

    if not res.ok:
        err(f"    Failed to create client: {client_id}; {res.status_code} {res.json()}")
        exit(1)


def get_keycloak_client_secret(client_id: str, token: str):
    return keycloak_req(f"{KC_ADMIN_API_CLIENTS_ENDPOINT}/{client_id}/client-secret", bearer_token=token)


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
            err(f"  Failed to sign in as {AUTH_ADMIN_USER}; {res.status_code} {res.json()}")
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
            err(f"    Failed to create realm: {AUTH_REALM}; {create_realm_res.status_code} {create_realm_res.json()}")
            exit(1)

    def create_web_client_if_needed(token: str) -> None:
        web_client_kc_id: Optional[str] = fetch_existing_client_id(token, AUTH_CLIENT_ID)
        if web_client_kc_id is not None:
            return

        # Create the Bento public/web client
        create_keycloak_client_or_exit(
            token,
            AUTH_CLIENT_ID,
            public_client=True,
            standard_flow_enabled=True,
            service_accounts_enabled=False,
            redirect_uris=[
                f"{PUBLIC_URL}{AUTH_LOGIN_REDIRECT_PATH}",
                f"{PORTAL_PUBLIC_URL}{AUTH_LOGIN_REDIRECT_PATH}",
            ],
            web_origins=[PUBLIC_URL, PORTAL_PUBLIC_URL],
            access_token_lifespan=900,  # default access token lifespan: 15 minutes
            use_refresh_tokens=True,
        )

    def create_grafana_client_if_needed(token: str) -> None:
        grafana_client_kc_id: Optional[str] = fetch_existing_client_id(token, GRAFANA_CLIENT_ID)

        if grafana_client_kc_id is None:
            # Create the Bento WES client
            create_keycloak_client_or_exit(
                token,
                GRAFANA_CLIENT_ID,
                standard_flow_enabled=True,
                service_accounts_enabled=False,
                public_client=False,  # Use client secret for this one
                redirect_uris=[
                    f"{GRAFANA_PRIVATE_URL}/*"
                ],
                web_origins=[GRAFANA_PRIVATE_URL],
                access_token_lifespan=900,  # default access token lifespan: 15 minutes
                use_refresh_tokens=False,
            )
            grafana_client_kc_id = fetch_existing_client_id(token, GRAFANA_CLIENT_ID)

        # Fetch and print secret

        client_secret_res = get_keycloak_client_secret(grafana_client_kc_id, token)

        client_secret_data = client_secret_res.json()
        if not client_secret_res.ok:
            err(f"    Failed to get client secret for {GRAFANA_CLIENT_ID}; {client_secret_res.status_code} "
                f"{client_secret_data}")
            exit(1)

        client_secret = client_secret_data["value"]
        cprint(
            f"    Please set BENTO_GRAFANA_CLIENT_SECRET to {client_secret} in local.env and restart Grafana",
            attrs=["bold"],
        )

    def create_grafana_roles_if_needed(token: str) -> None:
        grafana_client_kc_id: Optional[str] = fetch_existing_client_id(token, GRAFANA_CLIENT_ID)

        for role_name in ["admin", "editor", "viewer"]:
            create_client_role_or_exit(token, grafana_client_kc_id, role_name)

    def create_grafana_groups_if_needed(token: str) -> None:
        parent_group = {"name": "grafana"}
        parent_group_id = create_group_or_exit(token, parent_group)

        sub_groups = [
            {"name": "admin"},
            {"name": "editor"},
            {"name": "viewer"}
        ]

        for subgroup in sub_groups:
            create_group_or_exit(token, subgroup, parent_id=parent_group_id)

    # noinspection PyUnusedLocal
    def create_cbioportal_client_if_needed(token: str) -> None:
        cbio_client_kc_id: Optional[str] = fetch_existing_client_id(token, CBIOPORTAL_CLIENT_ID)

        if cbio_client_kc_id is None:
            # Create the cBioportal client
            create_keycloak_client_or_exit(
                token,
                CBIOPORTAL_CLIENT_ID,
                standard_flow_enabled=True,
                service_accounts_enabled=False,
                public_client=False,
                redirect_uris=[f"{CBIOPORTAL_URL}{AUTH_LOGIN_REDIRECT_PATH}"],
                web_origins=[CBIOPORTAL_URL],
                access_token_lifespan=900,  # 15 minutes
                use_refresh_tokens=True,
            )
            cbio_client_kc_id = fetch_existing_client_id(token, CBIOPORTAL_CLIENT_ID)

        # Fetch and print secret

        client_secret_res = get_keycloak_client_secret(cbio_client_kc_id, token)

        client_secret_data = client_secret_res.json()
        if not client_secret_res.ok:
            err(f"    Failed to get client secret for {CBIOPORTAL_CLIENT_ID}; {client_secret_res.status_code} "
                f"{client_secret_data}")
            exit(1)

        client_secret = client_secret_data["value"]
        cprint(
            f"    Please set BENTO_CBIOPORTAL_CLIENT_SECRET to {client_secret} in local.env and restart the "
            f"gateway",
            attrs=["bold"],
        )

    def create_wes_client_if_needed(token: str) -> None:
        wes_client_kc_id: Optional[str] = fetch_existing_client_id(token, WES_CLIENT_ID)

        if wes_client_kc_id is None:
            # Create the Bento WES client
            create_keycloak_client_or_exit(
                token,
                WES_CLIENT_ID,
                standard_flow_enabled=False,
                service_accounts_enabled=True,
                public_client=False,  # Use client secret for this one
                redirect_uris=[],  # Not used with a standard/web flow - just client credentials
                web_origins=[],  # "
                access_token_lifespan=WES_WORKFLOW_TIMEOUT,  # WES workflow lifespan
                use_refresh_tokens=False,  # No refreshing these allowed!
            )
            wes_client_kc_id = fetch_existing_client_id(token, WES_CLIENT_ID)

        # Fetch and print secret

        client_secret_res = get_keycloak_client_secret(wes_client_kc_id, token)

        client_secret_data = client_secret_res.json()
        if not client_secret_res.ok:
            err(f"    Failed to get client secret for {WES_CLIENT_ID}; {client_secret_res.status_code} "
                f"{client_secret_data}")
            exit(1)

        client_secret = client_secret_data["value"]
        cprint(
            f"    Please set BENTO_WES_CLIENT_SECRET to {client_secret} in local.env and restart WES",
            attrs=["bold"],
        )

    def create_test_user_if_needed(token: str) -> None:
        p = f"admin/realms/{AUTH_REALM}/users"

        existing_users_res = keycloak_req(p, bearer_token=token)
        existing_users = existing_users_res.json()

        if not existing_users_res.ok:
            err(f"    Failed to fetch existing users: {existing_users}")
            exit(1)

        for u in existing_users:
            if u["username"] == AUTH_TEST_USER:
                warn(f"    Found existing user: {AUTH_TEST_USER} (ID={u['id']}); using that.")
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

        create_user_res_data = create_user_res.json()
        if create_user_res.ok:
            cprint(f"    Created user: {AUTH_TEST_USER} (ID={create_user_res_data['id']}).", "green")
        else:
            err(f"    Failed to create user: {AUTH_TEST_USER}; {create_user_res.status_code} {create_user_res_data}")
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

    # TODO: if cBioPortal ever needs auth implemented, re-enable this and set up Bento Gateway to handle cBioPortal
    #  client authorization.
    #   - David L, 2024-03-25
    # if c.BENTO_FEATURE_CBIOPORTAL.enabled:
    #     info(f"  Creating cBioPortal client: {CBIOPORTAL_CLIENT_ID}")
    #     create_cbioportal_client_if_needed(access_token)
    #     success()

    info(f"  Creating WES client: {WES_CLIENT_ID}")
    create_wes_client_if_needed(access_token)
    success()

    if c.BENTO_FEATURE_MONITORING.enabled:
        info(f"  Creating Grafana client: {GRAFANA_CLIENT_ID}")
        create_grafana_client_if_needed(access_token)
        create_grafana_roles_if_needed(access_token)
        create_grafana_groups_if_needed(access_token)
        # TODO: group client-role mappings
        #  /admin/realms/{realm}/groups/{group-id}/role-mappings/clients/{client}
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

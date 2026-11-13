# PCGL authorization delegation

By default, the Bento authorization service decides everything from Bento grants. With
`BENTO_AUTHZ_POLICY_ENGINE=pcgl`, it also asks the PCGL authorization service whether a user may download the file
manifest of a study. Every other decision still comes from Bento grants.


## How a decision is made

* Bento grants are evaluated first. PCGL can only add `download:metadata`; it never removes a permission.
* This applies to permission evaluations and to the endpoints that list the permissions of a user.
* Delegation to PCGL only happens when all of the following hold for a given permission check:
  * the request has a bearer token (anonymous requests are never sent to PCGL);
  * the resource is `{"project": ..., "dataset": ..., "data_type": "experiment"}`;
  * Bento grants do not already give `download:metadata` (`query:data` gives it).
* The dataset ID is sent as the PCGL study ID. All the studies of a request go in a single `/allowed` call, with the
  user's token as the bearer token and Bento's service ID and service token in the `X-Service-Id` and
  `X-Service-Token` headers.
* The service token comes from `POST <service URL>/service/<service ID>/verify`. It is cached for
  `BENTO_AUTHZ_PCGL_SERVICE_TOKEN_LIFESPAN` seconds, and requested again once if PCGL answers 401 or 403.
* Any PCGL error, timeout or unexpected response counts as "not allowed".


## Requirements

* Bento is registered as a service in the PCGL authorization service
* User access tokens are issued by the same IdP as the one the PCGL authorization service uses. The OAuth2 client
  can be different.
* Each dataset's `identifier` is its PCGL study ID. Set it when creating the dataset: Katsu generates a UUID if it
  is missing, and it cannot be changed afterwards.
* Dataset IDs only contain letters, digits, `_` and `-`, start with a letter or a digit, and are 128 characters long
  at most (`[A-Za-z0-9][A-Za-z0-9_-]{0,127}`). In particular, `.` and `:` are not accepted. Project IDs are still
  UUIDs.


## Configuration

```bash
# local.env

BENTO_AUTHZ_POLICY_ENGINE=pcgl
BENTO_AUTHZ_PCGL_SERVICE_URL="https://<pcgl-authz-host>"  # Base URL of the PCGL authorization service
BENTO_AUTHZ_PCGL_SERVICE_ID="<service ID>"                # Bento's service ID in the PCGL authorization service
BENTO_AUTHZ_PCGL_SERVICE_SECRET="<service secret>"        # Bento's service secret (UUID)
```

Then restart the authorization service:

```bash
./bentoctl.bash restart authz
```

With the `pcgl` policy engine, the service refuses to start if the service URL, service ID, service secret, action
endpoint or action method is empty, or if the token lifespan or the request timeout is not greater than 0.

All settings, with their defaults from `etc/default_config.env`:

| Variable                                  | Default         | Description                                            |
| ----------------------------------------- | --------------- | ------------------------------------------------------ |
| `BENTO_AUTHZ_POLICY_ENGINE`               | `bento`         | `bento` (Bento grants only) or `pcgl`.                 |
| `BENTO_AUTHZ_PCGL_SERVICE_URL`            |                 | Base URL of the PCGL authorization service.            |
| `BENTO_AUTHZ_PCGL_SERVICE_ID`             |                 | Bento's service ID in the PCGL authorization service.  |
| `BENTO_AUTHZ_PCGL_SERVICE_SECRET`         |                 | Bento's service secret (UUID).                         |
| `BENTO_AUTHZ_PCGL_ACTION_ENDPOINT`        | `/export/study` | Action endpoint sent to `/allowed`, as registered.     |
| `BENTO_AUTHZ_PCGL_ACTION_METHOD`          | `GET`           | Action method sent to `/allowed`, as registered.       |
| `BENTO_AUTHZ_PCGL_SERVICE_TOKEN_LIFESPAN` | `1500`          | Seconds the PCGL service token is cached for.          |
| `BENTO_AUTHZ_PCGL_REQUEST_TIMEOUT`        | `10`            | Timeout, in seconds, of each request to PCGL.          |
| `BENTO_AUTHZ_JWT_ACCESS_TOKENS`           | `true`          | Whether bearer tokens are JWTs. See [Limits](#limits). |

The TLS certificate of the PCGL authorization service is verified, except when `MODE=dev`
(`BENTO_VALIDATE_SSL=False` in `docker-compose.dev.yaml`).


## Bento Public

With `BENTO_PUBLIC_PCGL_MODE='true'`, a dataset page checks `download:metadata` on the dataset's `experiment` data
type:

* if the user has it, the "Get manifest" button is shown. It calls Katsu's `/api/batch/experimentresults` with
  `format=pcgl_manifest`, scoped to the dataset;
* otherwise, the "Apply for access" button is shown, if `BENTO_PUBLIC_APPLY_FOR_ACCESS_URL` is set.

The "Get manifest" button does not depend on the number of experiment results of the dataset: counts are censored
for users who only have access through PCGL.

The DAC ID shown on the dataset page is the dataset's `pcgl_dac_id` field.

Without PCGL mode, nothing changes: the "Apply for access" button depends on `download:data`, and there is no "Get
manifest" button.


## Limits

* Only the dataset-scoped manifest is delegated. Other formats of `/api/batch/experimentresults`, and the manifest
  export from search results (`/api/discovery_matches`), still need a Bento `query:data` grant.
* PCGL decides per study, not per data type (for now), so only the `experiment` data type is delegated.
* Keep `BENTO_AUTHZ_JWT_ACCESS_TOKENS=true`. With `false`, the authorization service does not decode bearer tokens,
  so Bento grants treat every request as anonymous. Only the PCGL check still receives the token. Support for
  non-JWT access tokens is not finished at time of writing.


## Future work

**Idea to explore: permissions hardening.**

A Bento `query:data` grant gives record-level access and the manifest, without delegating checks.
The authorization service could take a configurable list of denied permissions (e.g.
`query:data`), ignored at evaluation and refused when creating grants, with an exemption for service clients.

The purpose of this is to reduce the risk of misconfigurations in the authorization service's grants, by 
systematically denying permissions that pose risks.

Not settled, to be discussed.

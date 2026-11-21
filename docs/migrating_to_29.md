# Migrating to Bento v29

**BREAKING CHANGES:**

* WES (v0.17.0) now requires the user who starts a workflow run to have the `view:drop_box` permission on the whole
  instance if any of the run's file or directory inputs are set, since these are downloaded from the Drop-Box. Users
  with only project- or dataset-level grants (e.g. `ingest:data`) can no longer start these runs until they are given
  `view:drop_box` (see [step 5](#5-grant-drop-box-access-to-users-who-run-workflows)).
* WES only runs workflows from a workflow provider registered in the service registry (e.g. Katsu or Gohan), fetched
  over HTTP(S). `file://` workflow URLs are rejected, and so are parameters that the workflow does not declare.
  Workflow attachments are refused unless `BENTO_WES_WORKFLOW_ATTACHMENTS_ENABLED=true`. The Bento web portal does not
  use any of these, so only custom scripts or clients that submit runs are affected.

**Noteworthy changes:**

* PCGL instances can delegate file manifest access to the PCGL authorization service
  (see [step 3](#3-pcgl-instances-only-enable-pcgl-authorization-delegation)). Other instances have nothing to do:
  the default policy engine (`bento`) keeps the current behaviour, and all the new `BENTO_AUTHZ_*` variables have a
  default value.
* There is a new dataset-level permission, `download:metadata`, for downloading the metadata of a dataset as files.
  `query:data` gives it; `download:data` does not. It can be given by a Bento grant, like any other permission.
* In Katsu, the experiment result file manifest (`/api/batch/experimentresults` with `format=pcgl_manifest`) now
  requires `download:metadata` instead of `query:data`. Existing `query:data` grants keep working. The manifest
  export from search results (`/api/discovery_matches`) still requires `query:data`.
* Katsu accepts dataset IDs that are not UUIDs in scoped requests, such as PCGL study IDs. They only contain letters,
  digits, `_` and `-`, start with a letter or a digit, and are 128 characters long at most. Project IDs are still
  UUIDs.
* In PCGL mode (`BENTO_PUBLIC_PCGL_MODE='true'`), Bento Public:
  * shows "Get manifest" or "Apply for access" on a dataset page depending on `download:metadata` on the dataset's
    `experiment` data type, and no longer on `download:data`
  * reads the DAC ID of a dataset from its `pcgl_dac_id` field, and no longer from `extra_properties.dac_id`.
* The other services only have dependency and base image updates (security fixes).


## 1. Update the Bento environment

Source the Bento virtual environment and update `bentoctl` dependencies:

```bash
source env/bin/activate
pip install -U pip
pip install -r requirements.txt
```


## 2. Pull latest Docker containers and stop Bento

```bash
./bentoctl.bash stop
./bentoctl.bash pull
```


## 3. (PCGL instances only) Enable PCGL authorization delegation

Skip this step if the instance does not use the PCGL authorization service.

Bento must be registered as a service in the PCGL authorization service, which gives it a service ID and a service
secret. Add them to your `local.env`, along with the policy engine and the URL of the PCGL authorization service:

```bash
# local.env
BENTO_AUTHZ_POLICY_ENGINE=pcgl
BENTO_AUTHZ_PCGL_SERVICE_URL="https://<pcgl-authz-host>"  # Base URL of the PCGL authorization service
BENTO_AUTHZ_PCGL_SERVICE_ID="<service ID>"                # Bento's service ID in the PCGL authorization service
BENTO_AUTHZ_PCGL_SERVICE_SECRET="<service secret>"        # Bento's service secret (UUID)
```

By default, Bento asks PCGL about the `GET /export/study` action. If Bento delegates authz checks to another action, 
set `BENTO_AUTHZ_PCGL_ACTION_METHOD` and `BENTO_AUTHZ_PCGL_ACTION_ENDPOINT` to the appropriate values.

See [PCGL authorization delegation](./pcgl_authorization.md) for the requirements and all settings.


## 4. Create the ETL Docker network

The gateway joins the ETL network even if ETL is disabled, so this step is needed on every instance.

```bash
./bentoctl.bash init-docker
```

To enable ETL, follow [Setting up ETL](./etl.md#setting-up-etl).


## 5. Restart Bento

```bash
./bentoctl.bash start
```


## 5. Grant drop-box access to users who run workflows

WES now requires `view:drop_box` on the whole instance to start a workflow run with file or directory inputs.
Superusers (`bento_authz assign-all-to-user`) and the WES client grant created during installation already have it.

For each other user or group who ingests or analyzes Drop-Box files, add a `view:drop_box` grant on everything. Note
that this lets them see all the files in the Drop-Box. Use the **Access Management** page of the private portal
(`/data/manager/access`), or the authorization service container:

```bash
./bentoctl.bash shell authz
bento_authz create grant \
  '{"iss": "<ISSUER_HERE>", "sub": "<USER_ID_HERE>"}' \
  '{"everything": true}' \
  'view:drop_box'
```

Where `<ISSUER_HERE>` is the issuer (for example, `https://bentov2auth.local/realms/bentov2`) and `<USER_ID_HERE>`
is the user (subject) ID.

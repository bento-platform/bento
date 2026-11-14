# Migrating to Bento v29

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

TODO: other v29 changes.


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

Bento must first be registered as a service in the PCGL authorization service, meaning that the following values must 
be obtained in the registration process and configured as env vars:
- `BENTO_AUTHZ_PCGL_SERVICE_ID`
- `BENTO_AUTHZ_PCGL_SERVICE_SECRET`

The authorization check delegated to PCGL authz can be configured with env vars:
- `BENTO_AUTHZ_PCGL_ACTION_METHOD` (default `GET`)
- `BENTO_AUTHZ_PCGL_ACTION_ENDPOINT` (default `/export/study`)

Add the following to your `local.env`:

```bash
BENTO_AUTHZ_POLICY_ENGINE=pcgl
BENTO_AUTHZ_PCGL_SERVICE_URL="https://<pcgl-authz-host>"  # Base URL of the PCGL authorization service
BENTO_AUTHZ_PCGL_SERVICE_ID="<service ID>"                # Bento's service ID in the PCGL authorization service
BENTO_AUTHZ_PCGL_SERVICE_SECRET="<service secret>"        # Bento's service secret (UUID)
```

Then check the datasets:

* Each dataset's `identifier` must be its PCGL study ID. It is set when the dataset is created and cannot be changed
  afterwards, so datasets created with a generated UUID must be re-created.
* Study IDs must follow the dataset ID format: letters, digits, `_` and `-` only, starting with a letter or a digit,
  128 characters at most.
* If a dataset has its DAC ID in `extra_properties.dac_id`, set it in the `pcgl_dac_id` field instead.

See [PCGL authorization delegation](./pcgl_authorization.md) for the requirements, all settings and troubleshooting.


## 4. Restart Bento

```bash
./bentoctl.bash start
```

On PCGL instances, check that the delegation works:

* the authorization service has started (`./bentoctl.bash logs authz`): it refuses to start if a required PCGL
  setting is empty;
* a user approved for a study in PCGL sees the "Get manifest" button on the page of the dataset, and can download
  the manifest.

If not, see [Troubleshooting](./pcgl_authorization.md#troubleshooting).

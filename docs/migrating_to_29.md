# Migrating to Bento v29

**Noteworthy changes:**

* PCGL instances can delegate file manifest access to the PCGL authorization service
  (see [step 3](#3-pcgl-instances-only-enable-pcgl-authorization-delegation)). Other instances have nothing to do:
  the default policy engine (`bento`) keeps the current behaviour.
* Katsu's experiment result file manifest (`pcgl_manifest` format) now requires `download:metadata` instead of
  `query:data`. `query:data` gives `download:metadata`, so existing grants keep working.
* In PCGL mode, Bento Public reads the DAC ID of a dataset from its `pcgl_dac_id` field, and no longer from
  `extra_properties.dac_id`.

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
* If a dataset has its DAC ID in `extra_properties.dac_id`, set it in the `pcgl_dac_id` field instead.

See [PCGL authorization delegation](./pcgl_authorization.md) for the requirements, all settings and troubleshooting.


## 4. Restart Bento

```bash
./bentoctl.bash start
```

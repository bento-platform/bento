# Bento ETL (Extract, Transform, Load)

[Bento ETL](https://github.com/bento-platform/bento_etl) automates the ingestion of external data into Bento's data
services. A job extracts raw data from an S3 store, transforms it into Bento data types, and loads the result into
Katsu.

ETL is optional and disabled by default. The version in `etc/bento.env` is a pull request image.


## How it is connected

The gateway routes ETL at `https://<BENTOV2_DOMAIN>/api/etl`.

| ETL talks to              | Through                                            | For                                      |
|---------------------------|----------------------------------------------------|------------------------------------------|
| Katsu                     | the public URL (`/api/metadata/`), via the gateway | loading data                             |
| The identity provider     | the public URL, via the gateway                    | getting its own access token             |
| The authorization service | the public URL, via the gateway                    | checking the permissions of job requests |
| The S3 store              | the URL in `BENTO_ETL_S3_ENDPOINT_URL`             | reading inputs, writing outputs          |

ETL signs in as its own OIDC client (`etl`, client credentials flow), and Katsu accepts its requests based on the
grants this client has in the authorization service.

S3 credentials are passed as environment variables only; no host AWS configuration is mounted.


## Setting up ETL

### 1. Enable the feature

In `local.env`:

```bash
BENTO_ETL_ENABLED='true'
```

### 2. Initialize the network and the data directory

```bash
./bentoctl.bash init-docker  # Creates the Docker network for ETL
./bentoctl.bash init-dirs    # Creates the ETL data directory (job status database)
```

Recreate the gateway so that it joins the ETL network and routes `/api/etl`:

```bash
./bentoctl.bash restart gateway
```

### 3. Create the OIDC client

```bash
./bentoctl.bash init-auth
```

With ETL enabled, this creates the `etl` client if it does not exist, and prints its secret. Set it in `local.env`:

```bash
BENTO_ETL_CLIENT_SECRET=<the secret printed by init-auth>
```

### 4. Give the client its permissions

ETL needs three permissions to load data into Katsu:

| Permission       | Used for                                                   |
|------------------|------------------------------------------------------------|
| `ingest:data`    | Ingesting phenopackets, experiments and experiment results |
| `create:dataset` | Creating datasets (the `datasets` loader)                  |
| `delete:dataset` | Deleting existing datasets (the `datasets` loader)         |

The `datasets` loader deletes each dataset **with all the data it contains**, then creates it again, empty.
Datasets are never updated in place, so `edit:dataset` is not needed.

Submitting a job requires the same permissions (see [Authorization](#authorization)).

Create the grant in the authorization service container (`./bentoctl.bash shell authz`), replacing `<ISSUER_HERE>`
with the issuer URL, for example `https://bentov2auth.local/realms/bentov2`:

```bash
bento_authz create grant \
  '{"iss": "<ISSUER_HERE>", "client": "etl"}' \
  '{"everything": true}' \
  'ingest:data' 'create:dataset' 'delete:dataset'
```

Alternatively, add the same grant to `lib/authz/static_data.json` and restart the authorization service
(`./bentoctl.bash restart authz`):

```json
{
  "expiry": null,
  "notes": "Bento ETL: replace datasets (delete, then create) and ingest data into them",
  "permissions": ["create:dataset", "delete:dataset", "ingest:data"],
  "resource": {"everything": true},
  "subject": {"client": "etl", "iss": "<ISSUER_HERE>"}
}
```

The resource can be narrowed to a single project if ETL should only write there.

### 5. Configure the S3 store

ETL reads its inputs from one bucket, and the `s3:json` loader writes to the same bucket.

#### With Bento's Garage

See [Using Garage Object Storage in Bento](./garage.md) to set up Garage first. With ETL enabled, `init-garage`
also creates the `etl` bucket:

```bash
./bentoctl.bash init-garage
```

Then, in `local.env` (already set in `etc/bento_dev.env`):

```bash
BENTO_ETL_S3_ENDPOINT_URL="https://${BENTO_GARAGE_DOMAIN}"
BENTO_ETL_S3_BUCKET="etl"
BENTO_ETL_S3_REGION_NAME="garage"    # Must match garage.toml
BENTO_ETL_S3_ACCESS_KEY="${BENTO_GARAGE_ACCESS_KEY}"
BENTO_ETL_S3_SECRET_KEY="${BENTO_GARAGE_SECRET_KEY}"
BENTO_ETL_S3_VALIDATE_SSL=False      # Development only: self-signed certificate
```

#### With another S3 provider

Set the same variables to the endpoint URL (including the protocol), bucket, region and credentials given by the
provider, with `BENTO_ETL_S3_VALIDATE_SSL=True`.

### 6. Start ETL

```bash
./bentoctl.bash run etl
```


## Submitting jobs

A job is a JSON object with an `extractor`, a `transformer` and a `loader`. See the
[Bento ETL documentation](https://github.com/bento-platform/bento_etl#readme) for all the options.

The OpenAPI UI at `https://<BENTOV2_DOMAIN>/api/etl/docs` lists the endpoints and job schemas.

### Authorization

| Endpoints                                  | Required permissions, on everything               |
|--------------------------------------------|---------------------------------------------------|
| `POST /jobs`, `POST /jobs/pipeline/<name>` | `ingest:data`, `create:dataset`, `delete:dataset` |
| `DELETE /jobs/<job_id>`                    | `delete:data`                                     |
| `GET /jobs`, `GET /jobs/<job_id>`          | `view:runs`                                       |

Jobs run as the `etl` client, so submitting one requires that client's permissions; the `etl` client itself can
submit jobs, but not read their statuses or delete them.

In the OpenAPI UI, give an access token to the **Authorize** button. For the `etl` client, get one with the client
credentials grant from `https://<BENTOV2_AUTH_DOMAIN>/realms/<BENTOV2_AUTH_REALM>/protocol/openid-connect/token`
(see [Bento ETL authorization](https://github.com/bento-platform/bento_etl#authorization)).

### Pipelines and mapping files

The pre-built image has neither the `pipelines/` nor the `mappings/` directory; both are only available when
[working on ETL locally](#working-on-etl-locally). Otherwise:

* `POST /jobs/pipeline/<name>` has nothing to run: send the job definition in the request body instead.
* Upload the mapping files to the bucket, and give them as `s3://<bucket>/<key>` in the transformer's
  `mappings_path` and `ontology_mappings_path`.

### Uploading mapping files to Bento's Garage

The AWS CLI container can upload them over the Garage network, using only the Garage keys given in the command.
For example, the PCGL mappings:

```bash
docker run --rm --network bentov2-garage-net \
  -v /path/to/bento_etl/mappings/pcgl:/mappings:ro \
  -e AWS_ACCESS_KEY_ID="<BENTO_GARAGE_ACCESS_KEY>" \
  -e AWS_SECRET_ACCESS_KEY="<BENTO_GARAGE_SECRET_KEY>" \
  -e AWS_DEFAULT_REGION=garage \
  amazon/aws-cli --endpoint-url http://bentov2-garage:3900 \
  s3 cp --recursive /mappings s3://etl/mappings/
```

The jobs then use, for example, `"mappings_path": "s3://etl/mappings/phenopackets_mappings.json"`.

### Submitting jobs from an external workflow

A workflow outside Bento, such as the PCGL `submission-snapshot` workflow, can write its inputs to the bucket and
submit the jobs itself. It needs:

* **The ETL URL**: `https://<BENTOV2_DOMAIN>/api/etl`.
* **A token per request**, from the `etl` client or a dedicated client with the
  [step 4](#4-give-the-client-its-permissions) grant. Either needs `view:runs` to read job statuses.
* **The same bucket as ETL** (`BENTO_ETL_S3_BUCKET`): job object keys are relative to it.
* **Access to that bucket**: with Bento's Garage, `https://<BENTO_GARAGE_DOMAIN>` with the Garage keys and region
  `garage` (skipping certificate validation on a development instance).
* **Mapping files in the bucket**, as `s3://` URIs.


## Working on ETL locally

```bash
./bentoctl.bash work-on etl
```

This clones the repository into `repos/etl` if needed and runs the development image with it mounted at `/etl`.
The debugger listens on host port 6456.

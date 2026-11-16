# Bento ETL (Extract, Transform, Load)

[Bento ETL](https://github.com/bento-platform/bento_etl) automates the ingestion of external data into Bento's data
services. A job extracts raw data from an S3 store, transforms it into Bento data types, and loads the result into
Katsu.

ETL is an optional service, disabled by default. It is at an early stage:

* It is **not routed by the gateway**, so it cannot be reached from outside the instance. Jobs are submitted
  from the machine that runs Bento (see [Submitting jobs](#submitting-jobs)). Job submission is not authenticated
  yet, so do not publish its port.
* The version in `etc/bento.env` is a pull request image.


## How it is connected

| ETL talks to            | Through                                                           | For                              |
|-------------------------|-------------------------------------------------------------------|----------------------------------|
| Katsu                   | the public URL (`/api/metadata/`), via the gateway                | loading data                     |
| The identity provider   | the public URL, via the gateway                                   | getting its own access token     |
| The authorization service | the public URL, via the gateway                                 | checking who deletes job records |
| The S3 store            | the URL in `BENTO_ETL_S3_ENDPOINT_URL`                            | reading inputs, writing outputs  |

ETL signs in as its own OAuth2 client (`etl`, client credentials flow), and Katsu accepts its requests based on the
grants this client has in the authorization service.

S3 credentials are only given to the container as environment variables. No AWS configuration or credentials file
from the host is mounted.


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

On a development instance, the gateway joins the ETL network so that ETL can resolve the Bento domains. Recreate
the gateway once the network exists:

```bash
./bentoctl.bash restart gateway
```

### 3. Create the OAuth2 client

```bash
./bentoctl.bash init-auth
```

With ETL enabled, this creates the `etl` client if it does not exist, and prints its secret. Set it in `local.env`:

```bash
BENTO_ETL_CLIENT_ID=etl
BENTO_ETL_CLIENT_SECRET=<the secret printed by init-auth>
```

### 4. Give the client its permissions

ETL needs three permissions to load data into Katsu:

| Permission       | Used for                                                     |
|------------------|--------------------------------------------------------------|
| `ingest:data`    | Ingesting phenopackets, experiments and experiment results   |
| `create:dataset` | Creating datasets (the `datasets` loader)                    |
| `delete:dataset` | Deleting existing datasets (the `datasets` loader)           |

The `datasets` loader replaces each dataset: it deletes the dataset **and all the data it contains**, then creates
it again, empty, ready for the next ingestion jobs. Datasets are never updated in place, so `edit:dataset` is not
needed.

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

Then, in `local.env`, after the Garage variables:

```bash
BENTO_ETL_S3_ENDPOINT_URL="http://${BENTO_GARAGE_CONTAINER_NAME}:${BENTO_GARAGE_S3_API_PORT}"
BENTO_ETL_S3_BUCKET="etl"            # Created by init-garage when ETL is enabled
BENTO_ETL_S3_REGION_NAME="garage"    # Must match garage.toml
BENTO_ETL_S3_ACCESS_KEY="${BENTO_GARAGE_ACCESS_KEY}"
BENTO_ETL_S3_SECRET_KEY="${BENTO_GARAGE_SECRET_KEY}"
```

ETL talks to Garage directly inside the Docker network, over plain HTTP, instead of going through the gateway like
DRS and Drop-Box do. Its S3 client always validates TLS certificates, so it would reject the self-signed
certificate of a development gateway.

#### With another S3 provider

Set the same five variables to the endpoint URL (including the protocol), bucket, region and credentials given by
the provider. The endpoint must have a certificate that validates.

### 6. Start ETL

```bash
./bentoctl.bash run etl
```


## Submitting jobs

A job is a JSON object with an `extractor`, a `transformer` and a `loader`. See the
[Bento ETL documentation](https://github.com/bento-platform/bento_etl#readme) for all the options.

On a development instance (`MODE=dev`), the ETL API is published on the loopback interface of the host, port 6400:

```bash
curl -X POST http://localhost:6400/jobs \
  -H 'Content-Type: application/json' \
  -d '{
    "extractor": {"object_key": "path/in/the/bucket/data.jsonl"},
    "transformer": {"type": "none"},
    "loader": {"data_type": "print"}
  }'

curl http://localhost:6400/jobs            # All jobs
curl http://localhost:6400/jobs/<job_id>   # One job; the status ends at 'success' or 'error'
```

The interactive API documentation is at `http://localhost:6400/docs`.

In production mode no port is published. Run the same requests from inside the container, where the service
listens on port 5000:

```bash
docker exec bentov2-etl curl -X POST http://localhost:5000/jobs -H 'Content-Type: application/json' -d '...'
```

Two things to know about the pre-built image:

* It does not contain the `pipelines/` directory of the ETL repository, so `POST /jobs/pipeline/<name>` has
  nothing to run. Send the job definition in the request body instead.
* It does not contain the `mappings/` directory either. Upload the mapping files to the bucket and give them as
  `s3://<bucket>/<key>` in the transformer's `mappings_path` and `ontology_mappings_path`.

Both directories are available in local development mode, since the repository is mounted in the container.

### Uploading mapping files to Bento's Garage

The AWS CLI container can upload them over the Garage network. It only uses the Garage keys given in the
command, and no AWS configuration from the host. For example, the PCGL mappings of the ETL repository:

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

A workflow that runs outside Bento can write its inputs to the bucket and submit the jobs itself, for example the
PCGL research portal's `submission-snapshot` workflow. It needs:

* **The ETL URL.** On a development instance it is `http://localhost:6400`. ETL has no `/api/etl` route on
  the gateway until its job submission is authenticated, so a workflow that defaults to
  `https://<BENTOV2_DOMAIN>/api/etl` must be pointed at the local port instead.
* **The same bucket as ETL** (`BENTO_ETL_S3_BUCKET`). The object keys given in the jobs are relative to this
  bucket.
* **Access to that bucket.** With Bento's Garage, a workflow running on the host reaches it through the gateway
  at `https://<BENTO_GARAGE_DOMAIN>` with the Garage keys and region `garage`. On a development instance the
  certificate is self-signed, so the workflow's S3 client must skip certificate validation.
* **Mapping files in the bucket**, given as `s3://` URIs (see above).


## Working on ETL locally

```bash
./bentoctl.bash work-on etl
```

This clones the repository into `repos/etl` if needed and runs the development image with the repository mounted
at `/etl`. The code that runs is the branch checked out in `repos/etl`. The debugger listens on port 6456 of the
host (loopback interface).

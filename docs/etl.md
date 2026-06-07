# Bento ETL (Extract, Transform, Load)

Bento ETL is a service to automate the injestion of external health data into the Bento data services.
With customizable transformers, ETL can collect and convert a variety of data types from any data source.

## Configuration

Please follow the instructions below to deploy the ETL service in a Bento stack.

### Environment variables

Enable Bento ETL by setting the feature flag in `local.env`.

```bash
BENTO_ETL_ENABLED='true'
```

### Initialize networking and directories and generate client secret

```bash
./bentoctl.bash init-docker  # Creates the Docker network for Bento ETL
./bentoctl.bash init-dirs  # Creates Bento ETL's data directory

# Generates the client secret
./bentoctl.bash run auth
./bentoctl.bash run gateway
./bentoctl.bash init-auth
```
After running `init-auth`, update the following in your `local.env` file!

```bash
BENTO_ETL_CLIENT_ID=etl
BENTO_ETL_CLIENT_SECRET={your-newly-generated-secret-here!}
```

### Create additional grants

As Bento ETL is responsible for the upload of data to other Bento data services, it needs some additional grants to be able to do so.

First, run and shell into the authorization service:

```bash
./bentoctl.bash run authz
./bentoctl.bash shell authz
```

Then, substituting the `<ISSUER_HERE>` field with your issuer (`iss`), run the following:

```bash
bento_authz create grant \
  '{"iss": "<ISSUER_HERE>", "client": "etl"}' \
  '{"everything": true}' \
  'view:private_portal'

bento_authz create grant \
  '{"iss": "<ISSUER_HERE>", "client": "etl"}' \
  '{"everything": true}' \
  'query:data' 'ingest:data' 'ingest:reference_material' 'delete:reference_material'
```

## Run Bento ETL

Now that everything's set up, you can start the ETL service container using:

```bash
./bentoctl.bash run etl  # Runs just the etl container
# or
./bentoctl.bash run  # Runs everything, including etl
```

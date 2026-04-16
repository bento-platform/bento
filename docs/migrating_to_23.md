# Migrating to Bento v23

## 1. Updating the Bento environment 

Source the Bento virtual environment and update `bentoctl` dependencies:

```bash
source env/bin/activate
pip install -U pip
pip install -r requirements.txt
```

## 2. Update Bento services

Update and restart Bento services using the following commands:

```bash
./bentoctl.bash pull
./bentoctl.bash up
docker system prune -a
```

## 3. Update Phenopackets and experiments as needed

### a. Describing experiments with new vocabulary terms

TODO

### b. Adding storage location/server to experiment results

We've added two new fields to experiment results:

* `storage_uri`: A URI (file, S3, HTTP, etc.) of the *resting* storage location of the result (rather than a mirror or 
  aliased link or something.) This is useful for groups who need to find their own files using Bento as a search engine.
* `storage_server`: A full-qualified domain name of the server where the data is hosted.

Neither of these fields are required, but in the case that one is specified, it is recommended that both are specified 
as they complement each other nicely (e.g., using `storage_server` to resolve an S3 `storage_uri`.)

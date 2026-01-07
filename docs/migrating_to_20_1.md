# Migrating to Bento v20.1

> [!IMPORTANT]
> If using MinIO, **DO NOT** check out the `v20.1` tag or release branch until you've downloaded all data from MinIO for 
> the migration to Garage.

Bento v20.1 brings two different changes which may require data migration when moving from v20:

* Fixes for genomic interpretations in Katsu, require reingestion if any genomic interpretations are present.
* The replacement of MinIO with GarageHQ as a local S3 backend, which requires migration of all bucket data.


## Table of Contents

* [MinIO to Garage Migration](#minio-to-garage-migration)
* [Updating `bentoctl` Dependencies and Bento Images](#updating-bentoctl-dependencies-and-bento-images)
* [Re-Ingesting Genomic Interpretations](#re-ingesting-genomic-interpretations)


## MinIO to Garage Migration

### Prerequisites

Before starting the migration, ensure you have:

- Access to both MinIO instance
- [`s3cmd`](https://github.com/s3tools/s3cmd) installed and configured
- Sufficient local disk space for the backup

### Step 1: Back up data from MinIO

```bash
# Sync data from MinIO to local backup
s3cmd -c ~/.s3cfg-minio-local sync s3://drop-box/ ./drop-box-backup/
s3cmd -c ~/.s3cfg-minio-local sync s3://drs/ ./drs-backup/
```

If you do not have a `~/.s3cfg-minio-local` file, you should create one. It should look something like this:

```ini
[default]
host_base = minio.bentov2.local
host_bucket = minio.bentov2.local
use_https = True

# For dev self-signed certs only
check_ssl_certificate = False

# Credentials
# Re-use ones in your local.env, or create new ones in the minio UI at minio.bentov2.local
access_key = <REDACTED>
secret_key = <REDACTED>
```

For verfication later, you can store the output of the following to check after migration:

```bash
# Save output text somewhere
s3cmd -c ~/.s3cfg-minio-local ls s3://drop-box/ --recursive | wc -l
s3cmd -c ~/.s3cfg-minio-local ls s3://drs/ --recursive | wc -l
```

#### Notes

- Use `--dry-run` flag to preview sync operations before executing
- Add `--delete-removed` if you want to mirror deletions
- Consider using `--skip-existing` for incremental syncs


### Step 2: Update to Bento v20.1

Now you can switch to the Bento `v20.1` tag, update `bentoctl` dependencies, and update images:

```bash
# make sure your `bentoctl` environment dependencies are up-to-date:
pip install -r requirements.txt

# update images
./bentoctl.bash pull

# don't start the new versions of services yet, as we need to set up Garage first!
```


### Step 3. Set up Garage

Follow the steps listed [here](./garage.md) to set up Garage.

> [!IMPORTANT] 
> Don't forget to set the Garage related variables in `local.env`, especially when real domains are used.
>
> If you forget to set `BENTO_GARAGE_DOMAIN` or `BENTO_GARAGE_ADMIN_DOMAIN` and are using real domains, the gateway will
> not be able to route your garage requests properly.

### Step 4. Restart other Bento services

Start new versions of any services that haven't already been restarted by the Garage setup process:

```bash
./bentoctl.bash up
```


### Step 5: Upload data to Garage

```bash
# Sync local backup to Garage
s3cmd -c ~/.s3cfg-garage-local sync ./drop-box-backup/ s3://drop-box/
s3cmd -c ~/.s3cfg-garage-local sync ./drs-backup/ s3://drs/
```

`s3cfg` template for Garage: 

```ini
# ~/.s3cfg-garage-local
[default]
host_base = garage.bentov2.local
host_bucket = garage.bentov2.local
use_https = True

# Provided from init-garage output
access_key = <GARAGE_ACCESS_KEY>
secret_key = <GARAGE_SECRET_KEY>

# For dev self-signed certs only; True if in production
check_ssl_certificate = False
```

### Step 6: Verify migration

Compare the object counts against the output from Step 1.
```bash
s3cmd -c ~/.s3cfg-garage-local ls s3://drop-box/ --recursive | wc -l
s3cmd -c ~/.s3cfg-garage-local ls s3://drs/ --recursive | wc -l
```

### Step 7: Cleanup

(**Note**: Consider keeping the backup for a grace period after removal):

#### Stopping MinIO
```bash
# stop the container (if it's running)
docker stop bentov2-minio
# below: only if you're completely done with MinIO!
docker rm bentov2-minio
```

#### Removing backups

After verifying the migration is successful, clean up the backup files 
```bash
# Remove local backup directories
rm -rf ./drop-box-backup/
rm -rf ./drs-backup/
```

#### Clearing MinIO environment variables from `local.env`

Remove the following lines from your `local.env`, if present:

```bash
# local.env

BENTO_MINIO_ENABLED='true'
---
# Unused if MinIO is disabled
BENTO_MINIO_DOMAIN=minio.${BENTOV2_DOMAIN}
---
# MinIO
BENTO_MINIO_ROOT_PASSWORD=devpassword789
```

#### Removing old MinIO files
```bash
rm ~/.s3cfg-minio-local
rm ./certs/gateway/minio_privkey1.key
rm ./certs/gateway/minio_fullchain1.crt
rm <path-to-your-minio-data-dir> # Default was ${BENTO_SLOW_DATA_DIR}/minio/data
```


## Updating `bentoctl` Dependencies and Bento Images

If you have not already done so, make sure your `bentoctl` environment dependencies are up-to-date:

```bash
pip install -r requirements.txt
```

Then, update Bento images (if you migrated to Garage from MinIO above, you should have already done this!)

```bash
./bentoctl.bash pull
./bentoctl.bash up

# if you want, free some space:
docker system prune -a
```


## Re-Ingesting Genomic Interpretations

Version 20.1 fixes a bug with ingesting genomic interpretations, which resulted in some genomic interpretations 
referencing the wrong biosample/subject. Since this bug was in the ingestion process, any datasets with these incorrect
genomic interpretations must have their phenopackets re-ingested in v20.1.

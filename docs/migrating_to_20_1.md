# Migrating to Bento v20.1

## Minio to Garage Migration

### Prerequisites
Before starting the migration, ensure you have:

> [!IMPORTANT]
> If using MinIO, **DO NOT** check out the `v20.1` tag or release branch until you've downloaded all data from MinIO for migration to Garage.

- Access to both Minio instance
- [`s3cmd`](https://github.com/s3tools/s3cmd) installed and configured
- Sufficient local disk space for the backup

### Step 1: Back up data from Minio

```bash
# Sync data from Minio to local backup
s3cmd -c ~/.s3cfg-minio-local sync s3://drop-box/ ./drop-box-backup/
s3cmd -c ~/.s3cfg-minio-local sync s3://drs/ ./drs-backup/
```

For example, your `.s3cfg-minio-local` might look something like this:
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

**Notes**
- Use `--dry-run` flag to preview sync operations before executing
- Add `--delete-removed` if you want to mirror deletions
- Consider using `--skip-existing` for incremental syncs

### Step 2: Setting up Garage

Now you can switch to Bento - v20.1; Follow the steps listed [here](./garage.md) to setup Garage.

### Step 3: Upload data to Garage

```bash
# Sync local backup to Garage
s3cmd -c ~/.s3cfg-garage-local sync ./drop-box-backup/ s3://drop-box/
s3cmd -c ~/.s3cfg-garage-local sync ./drs-backup/ s3://drs/
```

S3cfg template for Garage: 

```ini
# ~/.s3cfg-garage-local
[default]
host_base = garage.bentov2.local
host_bucket = garage.bentov2.local
use_https = True

# Provided from init-garage output
access_key = <GARAGE_ACCESS_KEY>
secret_key = <GARAGE_SECRET_KEY>

# For dev self-signed certs only  
check_ssl_certificate = False
```

### Step 3: Verify migration

Compare the object counts against the output from Step 1.
```bash
s3cmd -c ~/.s3cfg-garage-local ls s3://drop-box/ --recursive | wc -l
s3cmd -c ~/.s3cfg-garage-local ls s3://drs/ --recursive | wc -l
```

### Step 4: Cleanup

(**Note**: Consider keeping the backup for a grace period after removal):

#### Stopping Minio
```bash
docker stop bentov2-minio
```

#### Backup removal
After verifying the migration is successful, clean up the backup files 
```bash
# Remove local backup directories
rm -rf ./drop-box-backup/
rm -rf ./drs-backup/
```

#### Clearing Minio vars from local.env
Remove the following lines from your local.env
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

#### Old Minio files
```bash
rm ~/.s3cfg-minio-local
rm ./certs/gateway/minio_privkey1.key
rm ./certs/gateway/minio_fullchain1.crt
rm <path-to-your-minio-data-dir> # Default was ${BENTO_SLOW_DATA_DIR}/minio/data
```

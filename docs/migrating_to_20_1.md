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

#### Option A: If you have `~/.s3cfg-minio-local`
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

#### Option B: Without existing config file
```bash
# Backup drop-box bucket
s3cmd --access_key=ACCESS_KEY --secret_key=SECRET_KEY \
      --host=minio.bentov2.local --no-check-certificate \
      --host-bucket="minio.bentov2.local/%(bucket)s" \
      sync s3://drop-box/ ./drop-box-backup/

# Backup drs bucket
s3cmd --access_key=ACCESS_KEY --secret_key=SECRET_KEY \
      --host=minio.bentov2.local --no-check-certificate \
      --host-bucket="minio.bentov2.local/%(bucket)s" \
      sync s3://drs/ ./drs-backup/
```

**Notes**
- Use `--dry-run` flag to preview sync operations before executing
- Add `--delete-removed` if you want to mirror deletions
- Consider using `--skip-existing` for incremental syncs
- The `--no-check-certificate` flag is used for local development environments

### Step 2: Setting up Garage

Now you can switch to Bento - v20.1; Follow the steps listed [here](./garage.md) to setup Garage.

### Step 3: Upload data to Garage

#### Option A: If you have `~/.s3cfg-garage-local` or you can create one with the template below

```bash
# Sync local backup to Garage
s3cmd -c ~/.s3cfg-garage-local sync ./drop-box-backup/ s3://drop-box/
s3cmd -c ~/.s3cfg-garage-local sync ./drs-backup/ s3://drs/
```

S3cfg template for Garage: 

```ini
# ~/.s3cfg-garage-local
[default]
access_key = <GARAGE_ACCESS_KEY>
secret_key = <GARAGE_SECRET_KEY>
host_base = garage.bentov2.local
host_bucket = garage.bentov2.local/%(bucket)s
use_https = True
check_ssl_certificate = False
check_ssl_hostname = False
signature_v2 = False
region = garage
```

#### Option B: Without existing config file
```bash
# Upload drop-box bucket
s3cmd --access_key=<GARAGE_ACCESS_KEY> --secret_key=<GARAGE_SECRET_KEY> \
      --host=garage.bentov2.local --no-check-certificate \
      --host-bucket="garage.bentov2.local/%(bucket)s" \
      --region=garage \
      sync ./drop-box-backup/ s3://drop-box/

# Upload drs bucket
s3cmd --access_key=<GARAGE_ACCESS_KEY> --secret_key=<GARAGE_SECRET_KEY> \
      --host=garage.bentov2.local --no-check-certificate \
      --host-bucket="garage.bentov2.local/%(bucket)s" \
      --region=garage \
      sync ./drs-backup/ s3://drs/
```

### Step 3: Verify migration
```bash
# Compare object counts for drop-box
s3cmd -c ~/.s3cfg-minio-local ls s3://drop-box/ --recursive | wc -l
s3cmd -c ~/.s3cfg-garage-local ls s3://drop-box/ --recursive | wc -l

# Compare object counts for drs
s3cmd -c ~/.s3cfg-minio-local ls s3://drs/ --recursive | wc -l
s3cmd -c ~/.s3cfg-garage-local ls s3://drs/ --recursive | wc -l
```

### Step 4: Cleanup

After verifying the migration is successful, clean up the backup files (**Note**: Consider keeping the backup for a grace period after removal):
```bash
# Remove local backup directories
rm -rf ./drop-box-backup/
rm -rf ./drs-backup/
```



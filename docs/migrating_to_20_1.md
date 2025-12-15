# Migrating to Bento v20.1

## Minio to Garage Migration

### Prerequisites
Before starting the migration, ensure you have:
- Be on Bento - v20 in the start
- Access to both Minio instance
- `s3cmd` installed and configured
- Sufficient local disk space for the backup

### Step 1: Back up data from Minio

#### Option A: If you have `~/.s3cfg-minio-local`
```bash
# Sync data from Minio to local backup
s3cmd -c ~/.s3cfg-minio-local sync s3://drop-box/ ./drop-box-backup/
s3cmd -c ~/.s3cfg-minio-local sync s3://drs/ ./drs-backup/
```

#### Option B: Without existing config file
```bash
# Backup drop-box bucket
s3cmd --access_key=AKIA_MINIO --secret_key=MINIOSECRET \
      --host=minio.bentov2.local --no-check-certificate \
      --host-bucket="minio.bentov2.local/%(bucket)s" \
      sync s3://drop-box/ ./drop-box-backup/

# Backup drs bucket
s3cmd --access_key=AKIA_MINIO --secret_key=MINIOSECRET \
      --host=minio.bentov2.local --no-check-certificate \
      --host-bucket="minio.bentov2.local/%(bucket)s" \
      sync s3://drs/ ./drs-backup/
```

### Step 2: Setting up Garage

Now you can switch to Bento - v20.1; Follow the steps listed [here](./garage.md) to setup Garage.

### Step 3: Upload data to Garage

#### Option A: If you have `~/.s3cfg-garage-local` or you can create one with the template below

```bash
# Sync local backup to Garage
s3cmd -c ~/.s3cfg-garage-local sync ./drop-box-backup/ s3://drop-box/
s3cmd -c ~/.s3cfg-garage-local sync ./drs-backup/ s3://drs/
```

S3cfg template for garage: 

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

### Notes
- Use `--dry-run` flag to preview sync operations before executing
- Add `--delete-removed` if you want to mirror deletions
- Consider using `--skip-existing` for incremental syncs
- The `--no-check-certificate` flag is used for local development environments

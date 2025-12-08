# Object Storage in Bento

This document section covers how to configure Bento services to use S3 object storage.

When we refer to S3 here, we mean any S3 compatible implementation (Minio, Ceph, GCP, ...), which is not limited
to AWS.

## Why object storage?

Smaller datasets can easily be stored on disk storage on Bento instances.

On the other hand, larger datasets in the multi TB range can be more difficult to store on traditional 
block storage, if not impossible. This is where object-storage becomes necessary.

Object storage solutions like S3 can be used to store any file with an API. S3 clusters aim at providing scalability, 
high availability, low latency and durability.

This paradigm allows applications to read and write files over the network, thus allowing applications to 
handle more data than they otherwise could with block storage (disk).

On top of providing scalable storage, using object-storage makes it easier to deploy applications in general and 
especially on Kubernetes, since it eliminates the need to manage Persistent Volume Claims in clusters.

## S3 compatible services

This section details how to configure Bento services for S3 storage.

To enable S3 on Bento services, you first need to configure the following in your S3 provider:
1. Create S3 credentials for the service (access and secret key)
2. Create an S3 bucket for the service

The steps for this depend on which S3 provider you are using. For local development, we recommend
using the Garage deployment that comes with Bento. See [garage.md](garage.md) for setup instructions.

### Drop Box

The drop box service in Bento acts as a deposit location for Bento.
Files accessible to drop box can be ingested in Bento's various data services (Phenopackets, experiments, VCFs).

Edit your `local.env` file to include the drop box S3 environment variables:

```bash
# local.env

BENTO_DROP_BOX_S3_ENDPOINT="garage.bentov2.local"       # Local Garage S3 endpoint (no protocol)
BENTO_DROP_BOX_S3_USE_HTTPS=true                        # Use HTTPS or HTTP on the endpoint
BENTO_DROP_BOX_S3_BUCKET="drop-box"                     # Bucket name (created by init-garage)
BENTO_DROP_BOX_S3_REGION_NAME=""                        # Region (required for Garage)
BENTO_DROP_BOX_S3_ACCESS_KEY="<get from init-garage>"   # S3 access key (from init-garage output)
BENTO_DROP_BOX_S3_SECRET_KEY="<get from init-garage>"   # S3 secret key (from init-garage output)
BENTO_DROP_BOX_VALIDATE_SSL=false                       # Needs to be 'false' with self signed certs and HTTPS
```

Restart the drop box service for the changes to take effect:

```bash
./bentoctl.bash restart drop-box
```

### DRS

The DRS service is the Bento implementation of the DRS GA4GH standard.

Edit your `local.env` file to include the DRS environment variables for S3 storage.

```bash
# local.env

BENTO_DRS_S3_ENDPOINT="garage.bentov2.local"        # Local Garage S3 endpoint (no protocol)
BENTO_DRS_S3_USE_HTTPS=true                         # Use HTTPS or HTTP on the endpoint
BENTO_DRS_S3_BUCKET="drs"                           # Bucket name (created by init-garage)
BENTO_DRS_S3_REGION_NAME=""                         # Region (required for Garage)
BENTO_DRS_S3_ACCESS_KEY="<get from init-garage>"    # S3 access key (from init-garage output)
BENTO_DRS_S3_SECRET_KEY="<get from init-garage>"    # S3 secret key (from init-garage output)
BENTO_DRS_VALIDATE_SSL=false                        # Needs to be 'false' with self signed certs and HTTPS
```

Restart the DRS service for the changes to take effect:

```bash
./bentoctl.bash restart drs
```


## Verify that services are using the S3 backend

You can verify that DRS and Dop-Box are using the S3 backend by checking their logs:

Look for S3 logs in DRS:
```bash
./bentoctl.bash logs drs | grep -i s3
```

Look for S3 logs in Drop-Box:
```bash
./bentoctl.bash logs drop-box | grep -i s3
```

## Migrating from block storage to S3

This section goes over some useful tips to preserve your data when migrating a Bento instance from block storage
to S3 compatible object storage.

When turning S3 on in Bento, we recommend that you upload the data that was previously on disk to the appropriate 
bucket for a seamless transition.

### Prepare for S3 uploads

To upload old files to S3 you will need the following:
- An S3 store (use Bento's Minio if you don't have one)
  - Save the hostname for later
  - Determine if HTTPS or HTTP should be used
    - HTTPS is strongly recommended for security reasons, but some S3 stores are configured to be HTTP only
  - Determine if SSL validation should be performed if using HTTPS
- S3 credentials (created in the S3 store)
  - Save the `Access Key` string for later
  - Save the `Secret Key` string for later
- An S3 CLI tool installed on the machine hosting Bento
  - We detail usage with S3CMD here, but any S3 compatible CLI tool will work (aws, Minio CLI)

Before performing the uploads, configure your S3 CLI tool (S3CMD here):

```bash
# Create S3CMD config file
touch ~/.s3cfg

# Edit the file (details bellow)
vim ~/.s3cfg

# Test the connection to the S3 store by listing the buckets
s3cmd ls
```

The `~/.s3cfg` config file should be populated with the following fields at least:
```bash
host_base = <S3 STORE ENDPOINT>     # don't include the protocol
host_bucket = <S3 STORE ENDPOINT>   # don't include the protocol
use_https = True                    # False if HTTP
check_ssl_certificate = True        # False if using HTTPS with self-signed certs
access_key = <FILL FROM S3 STORE>
secret_key = <FILL FROM S3 STORE>
```

You can now proceed to uploading your data to the appropriate buckets in S3!

### Drop-Box

The following instructions apply to Drop-Box.

```bash
# Go to the drop-box directory
cd /path/to/drop-box/data-x/

# Make sure you have a destination bucket ready
# Here we expect s3://drop-box to be present
s3cmd ls

# Upload the content of the directory to S3 recursively
s3cmd put --recursive -v ./* s3://drop-box
```

### DRS

DRS includes a database that tracks file information, such as paths, timestamps etc.

If you are migrating from a DRS service with block-storage, any previously ingested file will include a path prefix.


Since DRS blobs were created on block storage, their path includes the mountpoint for the container volume that included
the files: `/drs/bento_drs/data/obj/<files>`

Instead of changing each DB row for DRS blobs that were uploaded from block-storage, we can simply upload the old data 
to the bucket using the same path prefix! New DRS blobs created with DRS in S3 mode will be placed at the root of the 
bucket.

```bash
# Go to the DRS data directory
cd /path/to/drs/data/obj

# Make sure you have a destination bucket ready
# Here we expect s3://drs to be present
s3cmd ls

# Upload the content of the directory to S3 recursively
# Here we re-use the block-storage path prefix in S3 to maintain valid paths:
#   s3://<BUCKET NAME>/<BLOCK STORAGE PREFIX> ==> s3://drs/drs/bento_drs/data/obj/
s3cmd put -v ./* s3://drs/drs/bento_drs/data/obj/
```

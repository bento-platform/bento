# Object Storage in Bento

This document section covers how to configure Bento services to use S3 object storage.

When we refer to S3 here, we mean any S3 compatible implementation (Minio, Ceph, GCP, ...), which is not limited
to AWS.

## Why object storage?

Smaller datasets can be stored on disk storage on Bento instances.

On the other hand, larger datasets in the multi TB range can be more difficult to store on traditional 
block storage, if not impossible.

Object storage solutions like S3 can be used to store any file with an API. S3 clusters aim at providing scalability, 
high availability, low latency and durability.

This paradigm allows applications to read and write files over the network, thus allowing applications to 
handle more data than they otherwise could with block storage (disk).

## S3 compatible services

This section details how to configure Bento services for S3 storage.

To enable S3 on Bento services, you first need to configure the following in your S3 provider:
1. Create S3 credentials for the service (access and secret key)
2. Create an S3 bucket for the service

The steps for this depend on which S3 provider you are using. For local development, we recommend 
using the Minio deployment that comes with Bento.

### Drop-box

The drop-box service in Bento acts as a deposit location for Bento.
Files accessible to drop-box can be ingested in Bento's various data services (Phenopackets, experiments, VCFs).

Edit your `local.env` file to include the drop-box S3 environment variables:

```bash
# local.env

BENTO_DROP_BOX_S3_ENDPOINT="https://minio.bentov2.local"    # Local Minio S3 endpoint
BENTO_DROP_BOX_S3_BUCKET="drop-box"                         # Bucket name
BENTO_DROP_BOX_S3_REGION_NAME=""                            # Region (optional)
BENTO_DROP_BOX_S3_ACCESS_KEY="<get from S3 provider>"
BENTO_DROP_BOX_S3_SECRET_KEY="<get from S3 provider>"
```

Restart the drop-box service for the changes to take effect.

### DRS (WIP)

The DRS service is the Bento implementation of the DRS GA4GH standard.

Edit your `local.env` file to include the DRS environment variables for S3 storage.

```bash
# local.env

BENTO_DRS_S3_ENDPOINT="https://minio.bentov2.local"     # Local Minio S3 endpoint
BENTO_DRS_S3_BUCKET="drs"                               # Bucket name
BENTO_DRS_S3_REGION_NAME=""                             # Region (optional)
BENTO_DRS_S3_ACCESS_KEY="<get from S3 provider>"
BENTO_DRS_S3_SECRET_KEY="<get from S3 provider>"
```

Restart the DRS service for the changes to take effect.

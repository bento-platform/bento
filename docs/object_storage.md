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
using the Minio deployment that comes with Bento.

### Drop Box

The drop box service in Bento acts as a deposit location for Bento.
Files accessible to drop box can be ingested in Bento's various data services (Phenopackets, experiments, VCFs).

Edit your `local.env` file to include the drop box S3 environment variables:

```bash
# local.env

BENTO_DROP_BOX_S3_ENDPOINT="minio.bentov2.local"        # Local Minio S3 endpoint (no protocol)
BENTO_DROP_BOX_S3_USE_HTTPS=true                        # Use HTTPS or HTTP on the endpoint
BENTO_DROP_BOX_S3_BUCKET="drop-box"                     # Bucket name (must already exist)
BENTO_DROP_BOX_S3_REGION_NAME=""                        # Region (not required for Minio or SD4H)
BENTO_DROP_BOX_S3_ACCESS_KEY="<get from S3 provider>"   # S3 access key (get from Minio console)
BENTO_DROP_BOX_S3_SECRET_KEY="<get from S3 provider>"   # S3 secret key (get from Minio console)
BENTO_DROP_BOX_VALIDATE_SSL=false                       # Needs to be 'false' with self signed certs and HTTPS
```

Restart the drop box service for the changes to take effect:

```bash
./bentoctl.bash restart drop-box
```

### DRS (WIP)

The DRS service is the Bento implementation of the DRS GA4GH standard.

Edit your `local.env` file to include the DRS environment variables for S3 storage.

```bash
# local.env

BENTO_DRS_S3_ENDPOINT="minio.bentov2.local"         # Local Minio S3 endpoint (no protocol)
BENTO_DRS_S3_USE_HTTPS=true                         # Use HTTPS or HTTP on the endpoint
BENTO_DRS_S3_BUCKET="drs"                           # Bucket name (must already exist)
BENTO_DRS_S3_REGION_NAME=""                         # Region (not required for Minio or SD4H)
BENTO_DRS_S3_ACCESS_KEY="<get from S3 provider>"    # S3 access key (get from Minio console)
BENTO_DRS_S3_SECRET_KEY="<get from S3 provider>"    # S3 secret key (get from Minio console)
BENTO_DRS_VALIDATE_SSL=false                        # Needs to be 'false' with self signed certs and HTTPS
```

Restart the DRS service for the changes to take effect:

```bash
./bentoctl.bash restart drs
```

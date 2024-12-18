# Migrating to Bento v18

## Before enabling minio

Create new docker network, init dirs and init certs for Minio instance

```bash
./bentoctl.bash init-certs -f
./bentoctl.bash init-dirs
./bentoctl.bash init-docker  # new networks for minio
```

### The following parameters must be configure in `local.env`

Enable minio by setting the feature flag in local.env

```bash
BENTO_MINIO_ENABLED='true'
```

Also set root user and password in local.env:
BENTO_MINIO_ROOT_USER=root (default value, could be change)
BENTO_MINIO_ROOT_PASSWORD=secure-password

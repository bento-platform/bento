# Bento object store

![MinIO service logs querying](./img/minio_object_store.png)

## Configuration

Enable MinIO by setting the feature flag in local.env

```bash
BENTO_MINIO_ENABLED='true'
```

After enabling the MinIO feature flag for the first time, 
you must initialize the Docker networks, mounted directories and certs.
```bash
./bentoctl.bash init-certs -f
./bentoctl.bash init-docker # new network for MinIO
./bentoctl.bash init-dirs 
```

Also set root user and password in local.env:
```bash
BENTO_MINIO_ROOT_USER=root # (default value, could be change)
BENTO_MINIO_ROOT_PASSWORD=secure-password
```
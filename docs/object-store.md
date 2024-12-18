# Bento object store

![Minio service logs querying](./img/minio_object_store.png)

## Configuration

Enable minio by setting the feature flag in local.env

```bash
BENTO_MINIO_ENABLED='true'
```

Also set root user and password in local.env:
BENTO_MINIO_ROOT_USER=root (default value, could be change)
BENTO_MINIO_ROOT_PASSWORD=secure-password
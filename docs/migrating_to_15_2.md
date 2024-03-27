# Migrating to Bento v15.2

Migrating to version 15.2 from version 15.1 should be straightforward.


## 1. Update Gohan JVM configuration, if necessary

See the [relevant section in the installation guide](installation.md#gohan-configuration) for more information.


## 2. Update services and restart

Run the following commands to pull the latest service images and restart services as needed:

```bash
./bentoctl.bash pull
./bentoctl.bash restart
```

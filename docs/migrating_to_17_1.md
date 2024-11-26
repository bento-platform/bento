# Migrating to Bento v17.1

Migrating to version 17.1 from version 17 should be straightforward.
Check out our new documentation on [using a reverse proxy in front of Bento](./reverse-proxy.md)!


## 1. Update services and restart

Run the following commands to pull the latest service images and restart services as needed:

```bash
./bentoctl.bash pull
./bentoctl.bash start
```

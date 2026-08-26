# Migrating to Bento v25.1

This patch release only includes changes to the Keycloak version for security fixes.

## 1. Update Bento services

Update and restart Bento services using the following commands:

```bash
./bentoctl.bash pull
./bentoctl.bash up
docker system prune -a
```

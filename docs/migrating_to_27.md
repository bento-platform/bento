# Migrating to Bento v27

## 1. Update the Bento environment 

Source the Bento virtual environment and update `bentoctl` dependencies:

```bash
source env/bin/activate
pip install -U pip
pip install -r requirements.txt
```

## 2. (If using Garage) Configure new environment variables

Garage has been bumped from v2.2.0 to v2.3.0, and `init-garage` now bootstraps the single-node cluster
layout and S3 access key directly via Garage's own `--single-node`/`--default-access-key` server flags,
instead of configuring them after the fact over the admin API.

If `BENTO_GARAGE_ENABLED=true`, add the following to `local.env`, alongside `BENTO_GARAGE_RPC_SECRET` and
`BENTO_GARAGE_ADMIN_TOKEN`:

```bash
# local.env
BENTO_GARAGE_ACCESS_KEY='<your-access-key>'
BENTO_GARAGE_SECRET_KEY='<your-secret-key>'
```

- **New Garage instance:** choose new values here, then run `./bentoctl.bash init-garage` as usual - see
  [docs/garage.md](garage.md).
- **Existing Garage instance:** set these to the *same* values as your current
  `BENTO_DRS_S3_ACCESS_KEY`/`BENTO_DRS_S3_SECRET_KEY` (or `BENTO_DROP_BOX_S3_ACCESS_KEY`/`SECRET_KEY`) so the
  new bootstrap flags line up with the access key already in use. Your existing single-node layout and
  buckets are unaffected by the version bump; there's no need to re-run `init-garage`.

## 3. Update Bento services

Update and restart Bento services using the following commands:

```bash
./bentoctl.bash pull
./bentoctl.bash up
docker system prune -a
```

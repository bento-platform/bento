# Migrating to Bento v20

TODO

## 1. Dump all Postgres databases

To upgrade to the latest version of Postgres, we need to exfiltrate and then re-load all data, since major upgrades are
not well-supported by the Postgres Docker image (although Postgres v17+ seems to be making headway here.)

To create a database dump, Bento v20 adds a `bentoctl` helper sub-command, which will create SQL files of (up to) four
databases in a folder of your choosing and will create the folder if needed. To do this, run the following command:

```bash
./bentoctl.bash pg-dump db_dumps/v19_to_v20
```

This will make `*.pgdump` files in a directory called `v19_to_v20` inside the `db_dumps` folder.


## 2. Shut down Bento and pull new images

```bash
./bentoctl.bash stop
./bentoctl.bash pull
```


## 3. Remove old database volumes

As described in [step 1](#1-dump-all-postgres-databases), we need to delete and re-create the database volumes in order
to upgrade the major Postgres version of the database containers. Here, we delete the contents of the old database 
volumes in order to prepare for fresh ones.

Before wiping them, if you want to be safe, make a copy/backup of the database folders:

```bash
cd path/to/data
# ---
mv auth/data auth/data_old
mv authz/db authz/db_old
mv katsu/data katsu/data_old
mv reference/data reference/data_old
# ---
cd path/to/bento
```

If anything goes wrong, you can manually roll back Postgres versions and try to keep using these volumes to perform the 
migration by hand. 

To wipe the volumes and re-create them as blank folders, run the following command:

```bash
./bentoctl.bash pg-wipe
```

All database volume directories will now be empty.


## TODO


## TODO. Restart Bento

```bash
./bentoctl.bash start
```


## TODO. Restore database contents

To restore the contents of Postgres databases, run the following:

```bash
./bentoctl.bash pg-load db_dumps/v19_to_v20
```

**If everything succeeds**, run the following to delete the database dump, which contains sensitive information:

```bash
# ONLY IF EVERYTHING SUCCEEDS!
rm -rf db_dumps/v19_to_v20
```

If the load fails for some reason, you will either need to re-ingest data by hand or rollback Postgres to another 
version and try to load the database dump files.

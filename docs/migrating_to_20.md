# Migrating to Bento v20

Bento version 20 includes enhancements to the Bento Public researcher portal user interface, full-text clin./phen. 
metadata search, and more. 

It also migrates to Postgres v18 from a mix of v13 and v16. Most of the steps below describe how to migrate the 
database containers, and it is **very important** that they are followed closely!

> [!IMPORTANT]
> Before beginning these steps, make sure you have **checked out** `releases/v20` on Git, but **NOT** pulled any new 
> Docker images yet!


## 1. Dump all Postgres databases

To upgrade to the latest version of Postgres, we need to exfiltrate and then re-load all data, since major upgrades are
not well-supported by the Postgres Docker image (although Postgres v17+ seems to be making headway here.)

To create a database dump, Bento v20 adds a `bentoctl` helper sub-command, which will create SQL files of (up to) four
databases in a folder of your choosing and will create the folder if needed. To do this, run the following command:

```bash
./bentoctl.bash pg-dump db_dumps/v19_to_v20
```

This will make `*.pgdump` files in a directory called `v19_to_v20` inside the `db_dumps` folder.

> [!NOTE]
> You may get collation version mismatch warnings during the dump process. This should not affect anything.

> [!IMPORTANT]
> Make sure to check the contents of the database dump files to make sure they have **your actual data** in them!


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
mv reference/data reference/data_old
# The katsu DB directory to move depends on whether you're running in development or production mode. The following is 
# for MODE=prod in local.env:
mv katsu/data katsu/data_old
# If you're running with MODE=dev in your local.env, run this instead:
mv katsu/dev/data katsu/dev/data_old
# ---
cd path/to/bento
```

If anything goes wrong, you can manually roll back Postgres versions and try to keep using these volumes to perform the 
migration by hand. 

To re-create blank volume folders, run the following command:

```bash
./bentoctl.bash init-dirs
```

All database volume directories should now exist, but be empty.


## 4. Restart Bento

```bash
./bentoctl.bash start
```


## 5. Restore database contents

To restore the contents of Postgres databases, run the following:

```bash
./bentoctl.bash pg-load db_dumps/v19_to_v20
```

**If everything succeeds**, run the following to delete the database dump, which contains sensitive information, as well
as your backup copies of the database volumes:

```bash
# ONLY IF EVERYTHING SUCCEEDS!
rm -rf db_dumps/v19_to_v20
# ---
cd path/to/data
rm -rf auth/data_old
rm -rf authz/db_old
rm -rf reference/data_old
# The katsu DB directory to move depends on whether you're running in development or production mode. The following is 
# for MODE=prod in local.env:
rm -rf katsu/data_old
# If you're running with MODE=dev in your local.env, run this instead:
rm -rf katsu/dev/data_old
# ---
cd path/to/bento
```

If the load fails for some reason, you will either need to re-ingest data by hand or rollback Postgres to another 
version and try to load the database dump files.


## 6. Populate Katsu's full-text search fields

For Katsu's new faster full-text search to work properly, a command needs to be run to populate some fields in the 
database when Katsu is migrated from a previous version (for some technical reasons, this could not be automatically 
done with a Django migration.)

To populate these fields, you will need to enter the Katsu shell and run a command:

```bash
./bentoctl.bash shell katsu
./manage.py populate_fts
```

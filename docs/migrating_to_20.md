# Migrating to Bento v20

TODO

## 1. Dump all Postgres databases

TODO

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

TODO

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

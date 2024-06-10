# Migrating to Bento v16

Key points:

* Bento v16 may now use 2 data directories for better resource usage in production. 
   * The environment variable `BENTOV2_ROOT_DATA_DIR` was replaced with:
      * `BENTO_FAST_DATA_DIR` for SSD mounts
      * `BENTO_SLOW_DATA_DIR` for HDD mounts
   * By default, `Drop-Box` and `DRS` are now configured to use `BENTO_SLOW_DATA_DIR` as their data directory.
     All other services use `BENTO_FAST_DATA_DIR`. 
   * If needed, the default service specific volume directories defined in [bento.env](../etc/bento.env) can be overriden in your 
     `local.env`.
* The WES schema has been updated, so the run database must be cleared.
* The reference service has been updated, so an SQL migration must be run.


## 1. Run reference service pre-migration step

```bash
./bentoctl.bash shell reference-db
PGPASSWORD="${POSTGRES_PASSWORD}"
psql --user "${POSTGRES_USER}" reference
```

Then, begin a transaction:

```sql
BEGIN TRANSACTION;
```

Then, paste the contents of
[migrate_v0_2.sql](https://github.com/bento-platform/bento_reference_service/blob/main/bento_reference_service/sql/migrate_v0_2.sql)
from the reference service repository into the SQL command line.

Next, commit the results of the transaction:

```sql
COMMIT;
```

Finally, exit the shell (via successive `^D`).


## 2. Stop Bento

```bash
./bentoctl.bash stop
```


## 3. Pre-update data config

Before updating, perform the following steps:

* Shut down Bento with `./bentoctl.bash stop`
* In `local.env`, replace `BENTOV2_ROOT_DATA_DIR` with `BENTO_FAST_DATA_DIR` and `BENTO_SLOW_DATA_DIR`

To minimize side effects in local environments, we recommend that you use the same directory as before for both new 
variables.

```bash
# local.env

# Old
BENTOV2_ROOT_DATA_DIR=some_dir

# Recommended new variables
BENTO_FAST_DATA_DIR=some_dir
BENTO_SLOW_DATA_DIR=some_dir
```

*IMPORTANT:* If you decide to split the data in distinct directories, **make sure to migrate the data accordingly**.


## 4. Update images

```bash
./bentoctl.bash pull
```


## 5. Create new Docker volume directories

```bash
./bentoctl.bash init-dirs  # new volume directory for DRS and Reference temporary files
```


## 6. Migrate data from old `BENTOV2_ROOT_DATA_DIR` location to `BENTO_FAST_DATA_DIR`/`BENTO_SLOW_DATA_DIR`

This is only needed if the data was split into distinct directories in part 1. All service data should be copied into 
the corresponding locations as specified in `etc/bento.env`.


## 7. Restart Bento

```bash
./bentoctl.bash start
```

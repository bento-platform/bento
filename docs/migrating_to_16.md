# Migrating to Bento v16

Bento v16 may now use 2 data directories for better resource usage in production.


The environment variable `BENTOV2_ROOT_DATA_DIR` was replaced with:
* `BENTO_FAST_DATA_DIR` for SSD mounts
* `BENTO_SLOW_DATA_DIR` for HDD mounts


By default, `Drop-Box` and `DRS` are now configured to use `BENTO_SLOW_DATA_DIR` as their data directory.

All other services use `BENTO_FAST_DATA_DIR`. 

If needed, the default service specific volume directories defined in [bento.env](../etc/bento.env) can be overriden 
in your `local.env`.

## 1. Pre-update data config

Before updating, perform the following steps:

* Shut down Bento with `./bentoctl.bash stop`
* In `local.env`, replace `BENTOV2_ROOT_DATA_DIR` with `BENTO_FAST_DATA_DIR` and `BENTO_SLOW_DATA_DIR`

To minimize side effects in local environments, we recommend that you use the same directory as before for both new variables.

```bash
# local.env

# Old
BENTOV2_ROOT_DATA_DIR=some_dir

# Recommended new variables
BENTO_FAST_DATA_DIR=some_dir
BENTO_SLOW_DATA_DIR=some_dir
```

*IMPORTANT:* If you decide to split the data in distinct directories, make sure to migrate the data accordingly.


## 2. Update images

```bash
./bentoctl.bash pull
```


## 3. Create new Docker volume directories

This step is optional if you DIDN'T split the data directories in step 1.

```bash
./bentoctl.bash init-dirs  # new volume directory for DRS temporary files

# migrate the old data
```


## 4. Restart Bento

```bash
./bentoctl.bash start
```

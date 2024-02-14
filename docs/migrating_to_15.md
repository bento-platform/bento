# Migrating to Bento v15

Bento v15 migrates to Phenopackets v2, and as such requires that Phenopackets are updated and re-ingested.

This version also adds the reference service, so permissions must be updated in order to give reference service
permissions to administrators and the WES client.


## 1. Pre-update data removal

Before updating, perform the following steps:

* Shut down Bento with `./bentoctl.bash stop`
* Remove the Katsu data volume
* Remove the WES data volume


## 2. Update images

```bash
./bentoctl.bash pull
```


## 3. Create new Docker volume directories and networks

```bash
./bentoctl.bash init-docker  # new networks for reference and reference-db
./bentoctl.bash init-dirs  # new volume directory for DRS temporary files
```


## 4. Set new environment variables

In `local.env`, set a secure value for `BENTO_REFERENCE_DB_PASSWORD`.


## 5. Restart Bento

```bash
./bentoctl.bash start
```


## 6. Add permissions

Add permissions as needed for reference service content management:

```bash
./bentoctl.bash shell authz  # start a shell session in the authz service container to access the authz CLI
bento_authz list grants
# In this list, find the grant IDs for the existing superuser/permissions managers and WES 
bento_authz add-grant-permissions <superuser-grant-id> ingest:reference_material delete:reference_material
bento_authz add-grant-permissions <wes-grant-id> ingest:reference_material delete:reference_material
```

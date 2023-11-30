# Migrating to Bento v15

Bento v15 migrates to Phenopackets v2, and as such requires that Phenopackets are updated and re-ingested.

Before updating, perform the following steps:

* Shut down Bento with `./bentoctl.bash stop`
* Remove the Katsu data volume
* Remove the WES data volume

Then, update your instance:

```bash
./bentoctl.bash pull
```

Finally, restart Bento:

```bash
./bentoctl.bash start
```

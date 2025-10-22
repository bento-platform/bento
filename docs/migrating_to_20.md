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

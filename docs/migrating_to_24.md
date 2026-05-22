# Migrating to Bento v24

## Katsu

> **NOTE:** Known issue — katsu auto-migrations may fail. If so, run manually:
> ```sh
> # Inside the katsu container
> python manage.py migrate
> ```

After switching to katsu, run the dataset migration command:

```sh
python manage.py migrate_to_datasets_v2
```

This migrates datasets from the old format to the new provenance format. Placeholder values will be created for missing fields.

Review the new provenance data via the web interface. To update a specific dataset, upload its JSON in the dataset edit view.

If you have a French translation for a dataset — **[TO COME]**
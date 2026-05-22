# Migrating to Bento v24

## 1. Updating the Bento environment 

Source the Bento virtual environment and update `bentoctl` dependencies:

```bash
source env/bin/activate
pip install -U pip
pip install -r requirements.txt
```

## 2. Update Bento services

Update and restart Bento services using the following commands:

```bash
./bentoctl.bash pull
./bentoctl.bash up
docker system prune -a
```

## 3. Migrate dataset metadata in Katsu

After restarting Bento, open a shell in Katsu:

```bash
./bentoctl.bash shell katsu
```

> **NOTE:** Known issue — katsu auto-migrations may fail. If so, run manually:
> ```sh
> # Inside the katsu container
> python manage.py migrate
> ```

Then, run the dataset migration command:

```sh
python manage.py migrate_to_datasets_v2
```

This migrates datasets from the old format to the new provenance format. Placeholder values will be created for missing 
fields.

Review the new provenance data via the web interface. To update a specific dataset, upload its JSON in the dataset edit 
view.

If you have a French translation for a dataset — **[TO COME]**

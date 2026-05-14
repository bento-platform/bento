# Migrating to Bento v21

## 1. (RECOMMENDED) Regenerate experiments with the new data model

The Bento experiment model has been changed, switching the `experiment_ontology` and `molecule_ontology` fields to be 
single ontology terms. Katsu will migrate these fields seamlessly, but going forwards ingestion will fail due to schema
errors with the old format.

New fields have also been added to the experiments model:

* `description`
* `protocol_url`
* `library_id`
* `library_description`
* `library_extract_id`
* `insert_size`

Make sure to update your experiments-generating scripts!


## 2. Update `bentoctl` requirements

Update `bentoctl` dependencies with the following commands: 

```bash
source env/bin/activate
pip install -U pip
pip install -r requirements.txt
```


## 3. Update Bento images, start Bento, and clean up old resources

Update and restart Bento services using the following commands:

```bash
./bentoctl.bash pull
./bentoctl.bash up
docker system prune -a
```


## 4. (RECOMMENDED) Re-ingest regenerated experiments

If you regenerated experiments in step 1, make sure you can successfully re-ingest them using the Bento portal 
administration interface.

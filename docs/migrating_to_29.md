# Migrating to Bento v29

TODO: summary of breaking changes / noteworthy changes.


## 1. Update the Bento environment

Source the Bento virtual environment and update `bentoctl` dependencies:

```bash
source env/bin/activate
pip install -U pip
pip install -r requirements.txt
```


## 2. Pull latest Docker containers and stop Bento

```bash
./bentoctl.bash stop
./bentoctl.bash pull
```


## 3. TODO: release-specific steps


## 4. Restart Bento

```bash
./bentoctl.bash start
```

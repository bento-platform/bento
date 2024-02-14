# Migrating to Bento v15.1

Migrating to version 15.1 from version 15 should be straightforward.


## 1. Update `bentoctl` Python requirements

Make sure you've entered into the `bentoctl` Python virtual environment, if you've set one up:

```bash
source env/bin/activate
```

Then, install the latest requirements / module versions:

```bash
pip install -r requirements.txt
```


## 2. Update services and restart

Run the following commands to pull the latest service images and restart services as needed:

```bash
./bentoctl.bash pull
./bentoctl.bash start
```

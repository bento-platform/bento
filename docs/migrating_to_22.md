# Migrating to Bento v22

First, source the Bento virtual environment and update `bentoctl` dependencies:

```bash
source env/bin/activate
pip install -U pip
pip install -r requirements.txt
```

Then, update and restart Bento services using the following commands:

```bash
./bentoctl.bash pull
./bentoctl.bash up
docker system prune -a
```

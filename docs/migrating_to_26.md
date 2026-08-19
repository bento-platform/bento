# Migrating to Bento v26

## 1. Update the Bento environment 

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

# Migrating to Bento v25

## 1. Update the Bento environment 

Source the Bento virtual environment and update `bentoctl` dependencies:

```bash
source env/bin/activate
pip install -U pip
pip install -r requirements.txt
```

## 2. Set up new Bento Public files

Run the following command to generate French logo placeholder files and the new instance CSS stylesheet for 
Bento Public:

```bash
./bentoctl.bash init-web public
```

## 3. TODO

TODO

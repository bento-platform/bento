# Migrating to Bento v29

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

## 3. (Optional) Configure the Bento Public announcement banner

Bento Public can now show an announcement banner, loaded from the GitHub issues of a repository you choose.
Two new variables control it:

- `BENTO_PUBLIC_BANNER_REPO` (default `''`): the GitHub API URL of the repository's issues. When empty, no
  banner is shown. The banner shows the newest open issue with the `announcement` label.
- `BENTO_PUBLIC_BANNER_CACHE_LIFE` (default `3600`): how many seconds the announcement is cached before Bento
  Public checks GitHub again. It must be a whole number of seconds. If it is unset or invalid, the default is used.

To turn on the banner, add the following to `local.env`:

```bash
# local.env
BENTO_PUBLIC_BANNER_REPO='https://api.github.com/repos/<owner>/<repo>/issues'
BENTO_PUBLIC_BANNER_CACHE_LIFE=3600


## 4. Restart Bento

```bash
./bentoctl.bash start
```


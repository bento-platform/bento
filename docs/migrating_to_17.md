# Migrating to Bento v17

Key points:

* Bento now has observability tools to help monitor the services (Grafana). Some setup is required for this feature to 
  work.
* Katsu discovery endpoints now have an authorization layer. Data that used to be completely public by default (i.e., 
  censored counts) now requires a permission (`query:project_level_counts` and/or `query:dataset_level_counts`), and 
  thus a grant in the authorization service. 
* ...


## 1. Stop Bento

```bash
./bentoctl.bash stop
```


## 2. Update images

```bash
./bentoctl.bash pull
```


## 3. *(Optional)* Set up Grafana

TODO: environment

```bash
./bentoctl.bash start auth
./bentoctl.bash init-auth
```


## 4. Set up public data access grants

Starting from Bento v17, anonymous visitors do not have access to see censored counts data by default, even if a 
discovery configuration has been set up. For anonymous visitors to access data, a level (`bool`, `counts`, `full`)
must be chosen and passed to the `bento_authz` CLI command below.

```bash
./bentoctl.bash shell authz
# Configure public data access
# ----------------------------
# The level below ("counts") preserves previous functionality. Other possible options are:
#  - none - will do nothing.
#  - bool - for censored true/false discovery, but in effect right now forbids access.
#  - counts - for censored count discovery.
#  - full - allows full data access (record-level, including sensitive data such as IDs), uncensored counts, etc.
bento_authz public-data-access counts
```


## 5. Start Bento

```bash
./bentoctl.bash start
```

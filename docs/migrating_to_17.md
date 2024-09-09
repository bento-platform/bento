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

TODO


## 5. Start Bento

```bash
./bentoctl.bash start
```

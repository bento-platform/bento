# Migrating to Bento v18

TODO


## 1. Stop and update services

```bash
./bentoctl.bash stop
./bentoctl.bash pull
```


## 2. Set up light and dark-background branding for Bento Public

* Make sure `lib/public/branding.png` and `lib/web/branding.png` are images which work on dark backgrounds.
* **If you have a light-background logo to add:** put this file at `lib/public/branding.lightbg.png`.
* **If you do not have a light-background logo:** run `./bentoctl.bash init-web public` to copy the Bento logo to the 
  above location, or copy `branding.png` to `branding.lightbg.png`


## 3. Enabling minio

Enable minio by setting the feature flag in local.env
```bash
BENTO_MINIO_ENABLED='true'
```

After enabling the Minio feature flag for the first time, 
you must initialize the Docker networks, mounted directories and certs.
```bash
./bentoctl.bash init-certs -f
./bentoctl.bash init-docker # new network for minio
./bentoctl.bash init-dirs 
```

Also set root user and password in local.env:
BENTO_MINIO_ROOT_USER=root (default value, could be change)
BENTO_MINIO_ROOT_PASSWORD=secure-password


TODO


## TODO. Restart services

```bash
./bentoctl.bash start
```

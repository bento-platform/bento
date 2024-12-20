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


## 3. Enabling MinIO

To enable the deployment of a MinIO server for S3 storage, refer to the documentation on [configuring MinIO for Bento](/docs/minio.md/).


## TODO. Restart services

```bash
./bentoctl.bash start
```

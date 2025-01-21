# Migrating to Bento v18

* Bento v18 requires implements some new features for branding, which may require changes as described below.
* It also adds MinIO as a backend for future S3-compatible object storage. 
  * This can be enabled now, but will not be used until a future version. 
  * For instances hosted on the Secure Data for Health (SD4H) infrastructure, the SD4H object store should be used for 
    production instances when S3-compatible services become ready in a future version.


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


## 3. If desired, disable Bento Public sign in / portal links

Version 18 includes two new Bento Public environment variables for customizing an instance:

* `BENTO_PUBLIC_SHOW_PORTAL_LINK`: Whether to show a link to the private data portal in the header
* `BENTO_PUBLIC_SHOW_SIGN_IN`: Whether to show a "Sign In" button in the header

Both of these are set to `true` by default. If desired, they can be toggled to `false` by setting them in `local.env`,
for example:

```bash
# ...
BENTO_PUBLIC_SHOW_PORTAL_LINK='false'
BENTO_PUBLIC_SHOW_SIGN_IN='false'
# ...
```


## 4. Enabling MinIO

To enable the deployment of a MinIO server for S3 storage, refer to the documentation on 
[configuring MinIO for Bento](/docs/minio.md).


## 5. Restart services

```bash
./bentoctl.bash start
```

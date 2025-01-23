# Adding services to Bento

There are two types of services in Bento:

* Bento services, which have been developed by the Bento team specifically for the platform, and
* other services, which support the Bento services or provide additional platform features.


## Aspects to consider when adding any service to Bento

### Environment variables

* Service environment variables, used for configuring the image and some aspects of the service itself, should be added 
  to `etc/bento.env`. These variables typically include:
  * Image
  * Image version (tag)
  * Container name template
  * Service Docker network (**Note:** we typically give each service its own network, and add services to multiple 
    networks only as needed)
  * Debugger ports
* Configuration environment variables, for setting up feature flags and passwords, should be added to 
  `etc/default_config.env` and the example files `etc/bento_deploy.env` and `etc/bento_dev.env`.
  * `etc/default_config.env` contains feature flags and "empty definitions" for passwords/secrets. 
  * `etc/bento_deploy.env` is an example / template setup (to be copied to `local.env`) for a production deployment.
  * `etc/bento_dev.env` is an example / template setup (to be copied to `local.env`) for a development setup.

### Container setup

The service's Docker container must be set up via a Compose file in `lib/<service>/docker-compose.<service>.yaml`.
This must then be included in the main `docker-compose.yaml` file, in the `include` block.

The service's network (and potentially feature flag, if applicable), as well as container name and port environment 
variables must be added to the gateway compose file (`lib/gateway/docker-compose.gateway.yaml`) if the service is to be 
externally accessible.

### Gateway configuration

*As needed,* a gateway NGINX config must be placed into `lib/gateway/<public_services|services>`.

### Required `bentoctl` changes

Inside the `py_bentoctl` Python module:

* If the service is locked behind a feature flag, add the feature (as an `BentoOptionalFeature` instance) to 
  `config.py`, modeling it after other definitions.
* Add the service image environment variables to the `service_image_vars` variable in `services.py`. 
* If the service is not a Bento service (or does not have the `bento` user in the Docker image), add the service to the
  `BENTO_USER_EXCLUDED_SERVICES` variable.
* In `other_helpers.py`:
  * If the service has a data directory that needs to be initialized, add an entry to the `data_dir_vars` variable 
    in the `init_dirs(...)` function containing the name of the environment variable which points to the data volume 
    directory.
  * Add any entry with the name of the environment variable storing the name of the Docker network to the `networks` 
    variable in the `init_docker(...)` function.
  * If new certificates are needed, add new entries to the `init_self_signed_certs` function (for development purposes).

### Documentation changes

* Make sure to add a note about how to set up the service for the first time to the 
  [Installation guide](./installation.md), as well as the migration guide for the version the service is introduced in.
* If additional deployment steps are needed (i.e., new certificates), add a note to the 
  [Deployment guide](./deployment.md).

### Additional notes

Non-Bento services **MUST NOT** be put into `etc/bento_services.json`; this file is for Bento services only (see below).


## Additional considerations when adding new Bento services

### User and base image

It is expected that Bento services will use one of the 
[Bento base images](https://github.com/bento-platform/bento_base_images).

These images provide a `bento` user, whose UID is set to the host user's UID.

### `/service-info` and service record in `bento_services.json`

Bento services **MUST** implement the GA4GH [Service Info](https://www.ga4gh.org/product/service-info/) API.
They must also be registered in the `etc/bento_services.json` file, which allows them to be loaded into the 
[Bento Service Registry](https://github.com/bento-platform/bento_service_registry).

Each entry of this file follows the format:

```js
{
  // ...
   "<compose ID>": {
     "service_kind": "<service kind>",
     "url_template": "{BENTO_PUBLIC_URL}/api/{service_kind}",
     "repository": "git@github.com:bento-platform/<...>"
   },
  // ...
}
```

In this format:
* `<compose ID>` is the key of the service in its `docker-compose.<...>.yaml` file
* `<service kind>` is a special Bento-unique identifier for the service, allowing front ends to look up services.
* The `url_template` key is a template for the base URL used to access the service's API.
* The `repository` key is an SSH Git repository URL for the service code, so it can be cloned into the `repos` folder
  for development.


### Making service-to-service requests go through the gateway (dev)

Bento relies on three mechanisms to resolve hostnames to IP adresses:
- DNS records in production
  - `/etc/hosts` entries when in local dev
- Container names
  - When two containers are on the same Docker network and need to talk to each other directly
  - Docker resolve a container's name to its IP on a Docker network
  - e.g. Katsu can talk directly to DRS with `http://${BENTOV2_DRS_CONTAINER_NAME}:${BENTOV2_DRS_INTERNAL_PORT}`
- Docker network aliases (dev only)
  - When two services need to communicate with each other via the gateway.

When developing locally, some services may need to be interacted with strictly through the gateway.
This is the case for Keycloak (auth) and Minio, as both services require a subdomain and HTTPS.

As such, drop-box cannot use the Docker resolver in order to connect to Minio.

Since we are in local, there is no DNS record to resolve Minio's domain, 
and the host's `/etc/hosts` entries will not be of help from the container's perspective.

For these situations, we rely on [Docker network aliases.](https://docs.docker.com/reference/compose-file/services/#aliases)

Taking the Minio example, we need:
  - Drop-Box to interact with Minio via the gateway
  - DRS to interact with Minio via the gateway

Enabling this is done by adding `${BENTO_MINIO_DOMAIN}` to the respective service networks aliases.

This snippet comes from [docker-compose.dev.yaml](../docker-compose.dev.yaml):
```
services:
  gateway:
    networks:
    drop-box-net:
      aliases:
        - ${BENTOV2_DOMAIN}
        - ${BENTOV2_PORTAL_DOMAIN}
        - ${BENTOV2_AUTH_DOMAIN}
        - ${BENTO_MINIO_DOMAIN}
    drs-net:
      aliases:
        - ${BENTOV2_DOMAIN}
        - ${BENTOV2_PORTAL_DOMAIN}
        - ${BENTOV2_AUTH_DOMAIN}
        - ${BENTO_MINIO_DOMAIN}
```

Doing so, we make sure that ${BENTO_MINIO_DOMAIN} is resolved to the gateway for drop-box and DRS.

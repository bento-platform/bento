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
* Configuration environment variables TODO

### Container setup

The service's Docker container must be set up via a Compose file in `lib/<service>/docker-compose.<service>.yaml`.
This must then be included in the main `docker-compose.yaml` file, in the `include` block.

The service's network (and potentially feature flag, if applicable), as well as container name and port environment 
variables must be added to the gateway compose file (`lib/gateway/docker-compose.gateway.yaml`) if the service is to be 
externally accessible.

### Gateway configuration

*As needed,* a gateway NGINX config must be placed into `lib/gateway/<public_services|services>`.

### Required `bentoctl` changes

TODO

* If new certificates are needed, add new entries to the `init_self_signed_certs` function (for development purposes)
  in `py_bentoctl/other_helpers.py`.

### Documentation changes

* Make sure to add a note about how to set up the service for the first time to the 
  [Installation guide](./installation.md), as well as the migration guide for the version the service is introduced in.
* If additional deployment steps are needed (i.e., new certificates), add a note to the 
  [Deployment guide](./deployment.md).

### Additional notes

Non-Bento services **MUST NOT** be put into `etc/bento_services.json`; this file is for Bento services only (see below).


## Additional considerations when adding new Bento services

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

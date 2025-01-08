# Adding services to Bento

There are two types of services in Bento:

* Bento services, which have been developed by the Bento team specifically for the platform, and
* other services, which support the Bento services or provide additional platform features.


## Aspects to consider when adding any service to Bento

* Service environment variables, used for configuring the image and some aspects of the service itself, should be added 
  to `etc/bento.env`. These variables typically include:
  * Image
  * Image version (tag)
  * Container name template
  * Service Docker network (**Note:** we typically give each service its own network, and add services to multiple 
    networks only as needed)
  * Debugger ports
* Configuration environment variables TODO
* Docker container configuration via a Compose file in `lib/<service>/docker-compose.<service>.yaml`
* *As needed:* a gateway NGINX config in `lib/gateway/<public_services|services>`

* TODO

Non-Bento services **MUST NOT** be put into `etc/bento_services.json`; this file is for Bento services only (see below).

### Required `bentoctl` changes

TODO


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

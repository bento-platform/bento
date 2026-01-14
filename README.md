# <img src="./docs/img/bento_logo.png" alt="Bento" width="297" height="73" />

Bento is a collection of free and open source microservices used to construct data-focused platforms, developed by the
[Canadian Centre for Computational Genomics](https://computationalgenomics.ca/) in Montréal.

By adhering to existing and anticipated standardized APIs, it facilitates interactions between 
various -omic science global communities. Its reusable and interoperable components reduce the 
complexity and overhead of constructing data distribution portals.


## Docker-based development and deployment tooling

This repository contains configuration and a command-line utility for deploying
the Bento platform using `docker compose`, and for developing the various services
that make up the Bento platform.



<!--
For now, comment out this diagram since it's outdated and confusing.
<div style="text-align:center">
  <img src="https://github.com/bento-platform/bentoV2/blob/main/diagram.png?raw=true" alt="diagram" style="align:middle;"/>
</div>
-->


## Requirements
- Docker >= 27.3
- Docker Compose >= 2.40.2 (plugin form: you should have the `docker compose` command available, without a dash)
  - Version 2.40.2 addressed a
    [major security vulnerability](https://www.cyber.gc.ca/en/alerts-advisories/docker-security-advisory-av25-708)
    in Compose, and is the minimum required version.
- Python >= 3.10 (for `bentoctl`); the services require Python 3.12 but this is included in their Docker images.


## Documentation

### Set up, installation, and development

* [`bentoctl`: the Bento deployment command line management tool](./docs/bentoctl.md)
* [Installation](./docs/installation.md)
* [Development](./docs/development.md)
  * [Adding services to Bento](./docs/adding-services.md)
* [Troubleshooting guide](./docs/troubleshooting.md)
* [Deployment](./docs/deployment.md)
* [Monitoring](./docs/monitoring.md)
* [Public discovery configuration](./docs/public_discovery.md)
* [Using a reverse proxy in front of Bento](./docs/reverse-proxy.md)
* [Batteries-included S3 object storage with Garage](./docs/garage.md)
* [Configuring services for object storage](./docs/object_storage.md)

### Data ingestion and usage

* [Guide to genomic reference material in Bento](./docs/reference_material.md)
* [Converting Phenopackets from V1 to V2 using `bentoctl`](./docs/phenopackets_v1_to_v2.md)
* [JSON Schemas for data types and discovery configuration](./docs/json-schemas.md)

### Migration documents

* [v20.1 to v21](./docs/migrating_to_21.md)
* [v20 to v20.1](./docs/migrating_to_20_1.md)
* [v19 to v20](./docs/migrating_to_20.md)
* [v18 to v19](./docs/migrating_to_19.md)
* [v17.1 to v18](./docs/migrating_to_18.md)
* [v17 to v17.1](./docs/migrating_to_17_1.md)
* [v16 to v17](./docs/migrating_to_17.md)
* [v15.2 to v16](./docs/migrating_to_16.md)
* [v15.1 to v15.2](./docs/migrating_to_15_2.md)
* [v15 to v15.1](./docs/migrating_to_15_1.md)
* [v14 to v15](./docs/migrating_to_15.md)
  * [Converting Phenopackets from V1 to V2 using `bentoctl`](./docs/phenopackets_v1_to_v2.md) 
* [v13 to v14](./docs/migrating_to_14.md)
* [v12 to v13](./docs/migrating_to_13.md)
* [v2.11 to v12](./docs/migrating_to_12.md)
* [v2.10 to v2.11](./docs/migrating_to_2_11.md)

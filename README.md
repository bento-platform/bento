# Bento

Bento is a collection of free and open source microservices used to construct data-focused platforms. 
By adhering to existing and anticipated standardized APIs, it facilitates interactions between 
various -omic science global communities. Its reusable and interoperable components reduce the 
complexity and overhead of constructing data distribution portals.


## Docker-based development and deployment tooling

This repository contains configuration and a command-line utility for deploying
the Bento platform using `docker compose`, and for developing the various services
that make up the Bento platform.



<div style="text-align:center">
  <img src="https://github.com/bento-platform/bentoV2/blob/main/diagram.png?raw=true" alt="diagram" style="align:middle;"/>
</div>


## Requirements
- Docker >= 19.03.8
- Docker Compose >= 2.14.0 (plugin form: you should have the `docker compose` command available, without a dash)


## Documentation

### Set up, installation, and development

* [`bentoctl`: the Bento deployment command line management tool](./docs/bentoctl.md)
* [Installation](./docs/installation.md)
* [Development]()
* [Troubleshooting guide](./docs/troubleshooting.md)

### Data ingestion and usage

* [Guide to genomic reference material in Bento](./docs/reference_material.md)
* [Converting Phenopackets from V1 to V2 using `bentoctl`](./docs/phenopackets_v1_to_v2.md) 

### Migration documents

* [v14 to v15](./docs/migrating_to_15.md)
  * [Converting Phenopackets from V1 to V2 using `bentoctl`](./docs/phenopackets_v1_to_v2.md) 
* [v13 to v14](./docs/migrating_to_14.md)
* [v12 to v13](./docs/migrating_to_13.md)
* [v2.11 to v12](./docs/migrating_to_12.md)
* [v2.10 to v2.11](./docs/migrating_to_2_11.md)

# Migrating to BentoV2 2.11

BentoV2 2.11 introduces a new pre-built gateway image, a new Keycloak image version, and a new management tool
called `bentoctl` which replaces the Makefile.


## Shut down the old cluster

The Makefile will likely no longer work, so stop the containers using the `docker` command or GUI.


## Move certificates

Certificates have been relocated from `lib/gateway/certs` to `./certs`, since Keycloak now
terminates SSL at the Keycloak server itself instead of the gateway.

To move certs, run:

```bash
mv ./lib/gateway/certs/* ./certs/
```


## Move development repos (optional; can just let `bentoctl` re-clone instead)

Development repositories are now located in `./repos`.

Repositories should be relocated and renamed after the `docker compose` service name.
For example, for web:

```bash
mv lib/web/bento_web repos/web
```


## Updating local environment variables

A new configuration variable has been added in BentoV2 2.11. 
Here is what you will need to set in your `local.env` file:

```bash
# Set this to a random secret value
BENTOV2_SESSION_SECRET=some-long-random-string
```

Remove any lines which look like the following:

```bash
BENTOV2_FEDERATION_PROD_DEBUG=true
BENTOV2_FEDERATION_DEV_DEBUG=true
```


## Create a Python 3.8+ (preferably 3.10+) virtual environment and install `bentoctl` requirements

`bentoctl` is a Python script, and requires some external dependencies, which we can put
in a virtual environment.

```bash
virtualenv -p python3 ./env  # create env folder with virtual environment inside
source ./env/bin/activate  # activate the virtual environment
pip install -r requirements.txt  # install bentoctl requirements
./bentoctl.bash --help  # Make sure bentoctl works and look at the available commands
```


## Make `bentoctl` alias (optional; Linux/macOS)

To make interacting with the CLI quicker, consider adding an alias for calling `bentoctl.bash`, putting the following
in your `.bash_aliases`, `.bash_profile` or `.zshrc` file:

### Bash/ZSH:
```bash
alias bentoctl="./bentoctl.bash"
```

From here, you can use `bentoctl` instead of `./bentoctl.bash` to manage BentoV2.


## Pull new images

v2.11 needs a bunch of new service images, as specified by `etc/bento.env`. To update the images using the new
`bentoctl` tool, run:

```bash
./bentoctl.bash pull
```


## Start the new cluster

```bash
./bentoctl.bash run
```


## Migrating to `bentoctl`

Key changes versus the Makefile include:

### Running all services

**Makefile:** `make run-all`

**`bentoctl`:** `./bentoctl.bash run`


### Restarting a specific service, while pulling a new image

#### Makefile

```bash
make stop-drs
docker pull ghcr.io/bento-platform/...
make run-drs
```

#### `bentoctl`

```bash
./bentoctl.bash restart --pull drs
```


### Switching a service (e.g., `web`) to development mode

#### Makefile

```bash
make clean-web
make run-web-dev
```

#### `bentoctl`

> **Note:** that the first time `work-on` is called, it will clone the service in question in the `repos/` directory 
> and run the version of the service that code specifies.
> This is a change from the old approach, where the repos were located in `lib/`.

```bash
./bentoctl.bash work-on web
```

This will automatically restart the service in development mode, using code in `./repos/web`.

### Switching a service (e.g., `web`) to production mode

#### Makefile

```bash
make clean-web-dev
make run-web
```

#### `bentoctl`

```bash
./bentoctl.bash prod web
```
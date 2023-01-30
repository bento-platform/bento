# BentoV2 - Docker-based Bento development and deployment tooling

This repo is intended to be the next generation of Bento deployments.
Originating from the blueprints in the repo `chord_singularity`, `bentoV2` aims to be much more modular than its 
counterpart, built with Docker instead of Singularity.



<div style="text-align:center">
  <img src="https://github.com/bento-platform/bentoV2/blob/qa/v2.4/diagram.png?raw=true" alt="diagram" style="align:middle;"/>
</div>

## `bentoctl`
This command line tool offers a series of commands and parameters that are helpful to setup the Docker environment for BentoV2 services. Consider using it instead of the Makefile for better cross-compatibility on Windows.


## Requirements
- Docker >= 19.03.8
- Docker Compose >= 2.14.0



### Prerequisites
Bentoctl depends on python packages, we recommend installing them in a venv (virtual environment).

```
# Create venv under ./env
python3 -m venv env

# Acivate venv in terminal
source env/bin/activate

# Install python requirements
pip3 install -r requirements.txt
```
Once the requirements are installed, you are ready to use bentoctl!

This command line tool offers a series of commands and parameters that are helpful to set up the Docker environment for 
Bento services. It is designed to facilitate fast development and have better cross-platform compatibility versus the 
Makefile.

### Prerequisites

This CLI is specifyed by a Python module, `py_bentoctl`, lauched by a Bash script, 
`./bentoctl.bash`. The Bash wrapper loads various `.env` files to set up the Bento environment.

The `bentoctl` script depends on python packages, we recommend using a virtual environment for this.

```
# Create a venv under ./env
python3 -m venv env

# Activate the python env
source env/bin/activate

# Install dependencies
pip3 install -r requirements.txt
```
To make interacting with the CLI quicker, consider adding an alias for calling `bentoctl.bash`, putting the following
in your `.bash_aliases`, `.bash_profile` or `.zshrc` file:

**Bash/ZSH:** `alias bentoctl="./bentoctl.bash"`

For a quick setup, use the following to append the alias to the file of your choice.
```
# Optional: create an alias for bentoctl (run from project's root)
echo "alias bentoctl=${PWD}/bentoctl.bash" > ~/.bash_aliases

# Simply use your alias!
bentoctl --help
```
### Usage
For an overview of `bentoctl`'s features, type the following from the root of the project:

```
./bentoctl.bash
```

> **Note:** the flags `--debug, -d` are intended for interactive remote Python debugging of the `bentoctl` module 
> itself. See [VSCode instructions](https://code.visualstudio.com/docs/python/debugging#_local-script-debugging) or 
> [PyCharm instructions](https://www.jetbrains.com/help/pycharm/remote-debugging-with-product.html) for IDE setup.

### Migrating to `bentoctl`

Key changes versus the Makefile include:

#### Running all services

**Makefile:** `make run-all`

**`bentoctl`:** `./bentoctl.bash run`


#### Switching a service (e.g., `web`) to development mode

##### Makefile

```bash
make clean-web
make run-web-dev
```

##### `bentoctl`

> **Note:** that the first time `work-on` is called, it will clone the service in question in the `repos/` directory 
> and run the version of the service that code specifies.
> This is a change from the old approach, where the repos were located in `lib/`.

```bash
./bentoctl.bash work-on web
```

#### Switching a service (e.g., `web`) to production mode

##### Makefile

```bash
make clean-web-dev
make run-web
```

##### `bentoctl`

```bash
./bentoctl.bash prod web
```



## Makefile
The Makefile contains a set of tools to faciliate testing, development, and deployments. Ranging from `build`, `run`, 
and `clean` commands, operators may have an easier time using these rather than fiddling with raw `docker` and 
`docker-compose` commands.



## Installation

### Provision configuration files

Depending on your use either development or deployment you will need to cp the right template file
```
# Dev
cp ./etc/bento_dev.env local.env

# Deployment
cp ./etc/bento_deploy.env local.env
```

Then, run --
```
# public service configuration file. Required if BENTOV2_USE_BENTO_PUBLIC flag is set to `1`
# See Katsu documentation for more information about the specifications
cp ./etc/katsu.config.example.json ./lib/katsu/config.json
```

-then modify the values as seen applicable..
For example;

```
local.env

BENTOV2_DOMAIN=bentov2.local
BENTOV2_PORTAL_DOMAIN=portal.${BENTOV2_DOMAIN}
BENTOV2_AUTH_DOMAIN=bentov2auth.local

MODE=dev

BENTOV2_USE_EXTERNAL_IDP=0
BENTOV2_USE_BENTO_PUBLIC=1
BENTOV2_PRIVATE_MODE=false

BENTOV2_ROOT_DATA_DIR=~/bentov2/data
```
If the internal IdP is being used (by default, Keycloak), credential variables should also be provided. The *admin* credentials are used to connect to the Keycloak UI
for authentication management (adding users, getting client credentials,...).
The *test* credentials will be used to authenticate on the Bento Portal.

```
BENTOV2_AUTH_ADMIN_USER=testadmin
BENTOV2_AUTH_ADMIN_PASSWORD=testpassword123

BENTOV2_AUTH_TEST_USER=testuser
BENTOV2_AUTH_TEST_PASSWORD=testpassword123
```
Otherwise, adjust the following AUTH variables according to the extenal IdP's specifications;
```
BENTOV2_AUTH_CLIENT_ID=local_bentov2
BENTOV2_AUTH_REALM=bentov2

BENTOV2_AUTH_WELLKNOWN_PATH=/auth/realms/${BENTOV2_AUTH_REALM}/.well-known/openid-configuration
```

<br />

### Create self-signed TLS certificates (`bentoctl`)

Setting up the certificates with `bentoctl` can be done in a single command.
From the project root, run

```bash
./bentoctl.bash init-certs
```

> This command will skip all certificate generation if it detects previously created files. 
> To force an override, simply add the option `--force, -f`.

### Create self-signed TLS certificates (With Makefile)

First, set up your local bentoV2 and authorization hostnames (something like `bentov2.local`, and `bentov2auth.local`) 
in the `.env` file. You can then create the corresponding TLS certificates for local development with the following 
steps:

From the project root, run
```
mkdir -p ./certs
```

> NOTE: In the steps below, ensure the domain names in `.env` and the cert Common Names match up

Then run
```
openssl req -newkey rsa:2048 -nodes \
    -keyout ./certs/privkey1.key -x509 \
    -days 365 -out ./certs/fullchain1.crt

openssl req -newkey rsa:2048 -nodes \
    -keyout ./certs/portal_privkey1.key -x509 \
    -days 365 -out ./certs/portal_fullchain1.crt
```
to create the bentov2 cert for `bentov2.local` (or whatever other domain you use)

Next, if you're running an OIDC provider container locally (default is Keycloak), run
```
openssl req -newkey rsa:2048 -nodes \
    -keyout ./certs/auth_privkey1.key -x509 \
    -days 365 \
    -out ./certs/auth_fullchain1.crt
```
to create the bentov2 cert for `bentov2auth.local` (or whatever other domain you use)

Finally, ensure that the local domain name is set in the machines `hosts` file (for Linux users, this is likely `/etc/hosts`, and in Windows, `C:\Windows\System32\drivers\etc\hosts`) pointing to either `localhost`, `127.0.0.1`, or `0.0.0.0`, depending on whichever gets the job done on your system.


### Boot the gateway controller (NGINX by default)

> NOTE: `make` commands seen here aren't the only tools for operating this cluster. See the `Makefile` for further documentation.


```sh
# Once the certificates are ready, initialize the cluster configs secrets
make init-chord-services
make init-dirs
make init-docker
make docker-secrets

# Build base images
make build-common-base

# Prepare web-service
make init-web

# If you are running the bentoV2 with the use of an internal identity provider (defaults to Keycloak), i.e setting BENTOV2_USE_EXTERNAL_IDP=0, run both
make run-gateway
# and
make auth-setup

# Otherwise, only open & configure the cluster's gateway with
make auth-setup
```

This last step boots and configures the local OIDC provider (**Keycloak**) container and reconfigure the gateway to 
utilize new variables generated during the OIDC configuration.

> NOTE: by default, the `gateway` service *does* need to be running for this to work as the configuration will pass via 
> the URL set in the `.env` file which points to the gateway.
>
> If you do not plan to use the built-in OIDC provider, you will have to handle the `auth_config` and `instance_config` 
> manually (see `./etc/auth/..` and `./etc/scripts/..` for further details)

The `CLIENT_SECRET` environment variable must be set using the value provided
by Keycloak. Using a browser, connect to the `auth` endpoint (by default `https://bentov2auth.local`) and use the admin credentials from the env file. Once within
Keycloak interface, navigate to the *Configure/Clients* menu. Select `local_bentov2`
in the list of clients and switch to the *Credentials* tab. Copy the secret from
there and paste it in your .env file.

![Keycloak UI: get client secret](docs/img/keycloak_client_secret.png)

### Setup Bento-Public

Run
```
make init-public
```

Adjust the default translation set as necessary

```
lib/public/translations/<en|fr>.json

{
  "Age": "Age",
  "Sex": "Sex",
  "Verbal consent date": "Verbal Consent Date",
  "Functional status": "Functional Status",
  "Lab Test Result": "Lab Test Results",
  "Experiment Types": "Experiment Types",
  "Demographics": "Demographics",
  "MALE": "MALE",
  "FEMALE": "FEMALE",
  "I have no problems in walking about": "I have no problems in walking about",
  "Results": "Results"
}


{
  "MALE": "HOMME",
  "FEMALE": "FEMME",
  "Age": "Âge",
  "Sex": "Sexe",
  "Demographics": "Démographie",
  "Verbal consent date": "Date de consentement verbal",
  "Functional status": "Statut fonctionnel",
  "Lab Test Result": "Résultats des tests de laboratoire",
  "Experiment Types": "Types d'expériences",
  "I have no problems in walking about": "Je n’ai aucun problème à marcher",
  "Results": "Résultats"
}
```


### Setup Gohan service

Run

```
make run-gohan-api
make run-gohan-elasticsearch
```

to start `bentov2-gohan-api` and `bentov2-gohan-elasticsearch` containers.



### Start the cluster

```
make run-all
```

to trigger the series of initial build events (using `docker-compose`) for the rest of bento's supporting microservices, and then run them.

### Stop the cluster

Run
```
make stop-all
```
to shut down the whole cluster,

```
make clean-all
```
to remove the docker containers and images from disk,

> NOTE: application data does persist (see `./lib/[auth, drs, katsu]/data` directories, for example)

### Gohan Genes 'Catalogue' Setup Tips:
Upon initial startup of a fresh instance, it may of use, depending on the use-case, to perform the following:

```
# navigate to:
https://portal.bentov2.local/api/gohan/genes/ingestion/run
# to trigger Gohan to download the default GenCode .gtk files from the internet and process them

# - followed up by
https://portal.bentov2.local/api/gohan/genes/ingestion/requests
# to keep up with the process

# the end results can be found at
https://portal.bentov2.local/api/gohan/genes/overview
```

<br />



## Development
To build upon the `bento_web` service while using bentoV2 *(Note; this can be done with a number of other services in the stack with slight modifications : see the 'Makefile' and '.env' for details)*, a few accomodations need to be made to your workspace.
First, move your local bento_web project to the `./lib/web` directory, or clone the web project there with

```
cd lib/web
git clone https://github.com/bento-platform/bento_web.git
```

You will then have `lib/web/bento_web` available.

Once this is set, you can run
```
make run-web-dev
```
which will spin up the `web` container tethered to your local directory with a docker `volume`. Internally, `npm run watch` is executed (see `./lib/web/dev_startup.sh`) so changes made locally will be reflected in the container - the service will then recompile and render.

> Note: if you get stuck on an NGINX `500 Internal Service Error`, give it another minute to spin up. If it persists, run `docker exec -it bentov2-web sh` to access the container, and then run `npm run watch` manually.


<br />

## Testing

First, head on over to https://github.com/mozilla/geckodriver/releases and download the latest geckodriver.

Decompress the .tar.gz or .zip and move the `geckodriver` over to the `./etc/tests/integration` directory. After that, simply run
```
make run-tests
```

This will run a set of both unit `(TODO)` and integration tests. See the `Makefile` for more details

## Troubleshooting

- The logs for each individual service can be accessed by running

```
docker logs bentov2-<service>
```
for example:
```
docker logs bentov2-katsu
```

- To restart all services

```
make stop-all
make run-all
make auth-setup
```

- If a service container doesn't start with `make run-all` start it individually, e.g.

```
make run-drs
```

- Running development instance locally: If federation service throws 500 ERROR, e.g.:

```
ssl.SSLError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed (_ssl.c:852)
ERROR:tornado.access:500 POST /private/dataset-search/...
```
In lib/federation/docker-compose.federation.yaml, set
```
CHORD_DEBUG=true
```

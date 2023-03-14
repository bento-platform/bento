# BentoV2 - Docker-based Bento development and deployment tooling

This repo is intended to be the next generation of Bento deployments.
Originating from the blueprints in the repo `chord_singularity`, `bentoV2` aims to be much more modular than its 
counterpart, built with Docker instead of Singularity.



<div style="text-align:center">
  <img src="https://github.com/bento-platform/bentoV2/blob/qa/v2.4/diagram.png?raw=true" alt="diagram" style="align:middle;"/>
</div>



<br />

## Requirements
- Docker >= 19.03.8
- Docker Compose >= 2.14.0 (plugin form: you should have the `docker compose` command available, without a dash)



<br />

## Migration documents

* [v2.10 to v2.11](./docs/migrating_to_2_11.md)



<br />

## `bentoctl`: the BentoV2 command line management tool

This command line tool offers a series of commands and parameters that are helpful to set up the Docker environment for 
Bento services. It is designed to facilitate fast development and have better cross-platform compatibility versus the 
Makefile.

### Prerequisites

This CLI is specified by a Python module, `py_bentoctl`, launched by a Bash script, 
`./bentoctl.bash`. The Bash wrapper loads various `.env` files to set up the Bento environment.

The `bentoctl` script depends on Python packages, we recommend using a virtual environment for this.

```bash
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

```bash
# Optional: create an alias for bentoctl (run from project's root)
echo "alias bentoctl=${PWD}/bentoctl.bash" > ~/.bash_aliases

# Now RESTART your terminal and re-source the virtualenv, OR run:
source ~/.bash_aliases

# Then, use your alias!
bentoctl --help
```

### Usage

For an overview of `bentoctl`'s features, type the following from the root of the project:

```bash
./bentoctl.bash
```

> **Note:** the flags `--debug, -d` are intended for interactive remote Python debugging of the `bentoctl` module 
> itself. See [VSCode instructions](https://code.visualstudio.com/docs/python/debugging#_local-script-debugging) or 
> [PyCharm instructions](https://www.jetbrains.com/help/pycharm/remote-debugging-with-product.html) for IDE setup.



<br />

## Installation

### 1. Provision configuration files

#### Instance-specific environment variable file: `local.env`

Depending on your use, development or deployment, you will need to copy the right template file
to `local.env` in the root of the `bentoV2` folder:

```bash
# Dev
cp ./etc/bento_dev.env local.env

# Deployment
cp ./etc/bento_deploy.env local.env
```

Then, modify the values as seen; depending on if you're using the instance for development or deployment.


##### Development example

The below is an example of a completed development configuration:

```bash
# in local.env:

MODE=dev

# Gateway/domains -----------------------------------------------------
BENTOV2_DOMAIN=bentov2.local
BENTOV2_PORTAL_DOMAIN=portal.${BENTOV2_DOMAIN}
BENTOV2_AUTH_DOMAIN=bentov2auth.local
# ---------------------------------------------------------------------

# Feature switches ----------------------------------------------------
BENTOV2_USE_EXTERNAL_IDP=0
BENTOV2_USE_BENTO_PUBLIC=1
BENTOV2_PRIVATE_MODE=false
# ---------------------------------------------------------------------

# set this to a data storage location, optionally within the repo itself, like: /path-to-my-bentov2-repo/data
BENTOV2_ROOT_DATA_DIR=~/bentov2/data

# Auth ----------------------------------------------------------------
#  - Session secret should be set to a unique secure value.
#    this adds security and allows sessions to exist across gateway restarts.
#  - Empty by default, to be filled by local.env
#  - IMPORTANT: set before starting gateway
BENTOV2_SESSION_SECRET=my-very-secret-session-secret  # !!! ADD SOMETHING MORE SECURE !!!

BENTOV2_AUTH_ADMIN_USER=admin
BENTOV2_AUTH_ADMIN_PASSWORD=admin  # !!! obviously for dev only !!!

BENTOV2_AUTH_TEST_USER=user
BENTOV2_AUTH_TEST_PASSWORD=user  # !!! obviously for dev only !!!

# Set CLIENT_SECRET *after* Keycloak is up and running; then, restart it.
CLIENT_SECRET=from-running-init-auth...
# --------------------------------------------------------------------

BENTOV2_KATSU_APP_SECRET=some-random-phrase-here   # !!! ADD SOMETHING MORE SECURE !!!

# Development settings ------------------------------------------------

# - Git configuration
BENTO_GIT_NAME=David  # Change this to your name
BENTO_GIT_EMAIL=do-not-reply@example.org  # Change this to your GitHub account email
```

If the internal OIDC identity provider (IdP) is being used (by default, Keycloak), variables specifying default 
credentials should also be provided. The *admin* credentials are used to connect to the Keycloak UI for authentication 
management (adding users, getting client credentials, ...). The *test* credentials will be used to authenticate on the 
Bento Portal.

```bash
BENTOV2_AUTH_ADMIN_USER=testadmin
BENTOV2_AUTH_ADMIN_PASSWORD=testpassword123

BENTOV2_AUTH_TEST_USER=testuser
BENTOV2_AUTH_TEST_PASSWORD=testpassword123
```

If using an *external* identity provider, adjust the following auth variables according to the external IdP's 
specifications:

```bash
BENTOV2_AUTH_CLIENT_ID=local_bentov2
BENTOV2_AUTH_REALM=bentov2

BENTOV2_AUTH_WELLKNOWN_PATH=/auth/realms/${BENTOV2_AUTH_REALM}/.well-known/openid-configuration
```

#### `bento_public` configuration

Then, copy the `bento_public` configuration file to its correct location for use by Katsu, 
Bento's clinical/phenotypic metadata service:

```bash
# public service configuration file. Required if BENTOV2_USE_BENTO_PUBLIC flag is set to `1`
# See Katsu documentation for more information about the specifications
cp ./etc/katsu.config.example.json ./lib/katsu/config.json
```



### 2. *Development only:* create self-signed TLS certificates 

First, set up your local Bento and Keycloak hostnames (something like `bentov2.local`, `portal.bentov2.local`, and 
`bentov2auth.local`) in the `.env` file. You can then create the corresponding TLS certificates for local development.

Setting up the certificates with `bentoctl` can be done in a single command.
From the project root, run

```bash
./bentoctl.bash init-certs
```

> **NOTE:** This command will skip all certificate generation if it detects previously created files. 
> To force an override, simply add the option `--force` / `-f`.


### 3. *Development only:* Hosts file configuration

Ensure that the local domain names are set in the machines `hosts` file (for Linux users, this is likely 
`/etc/hosts`, and in Windows, `C:\Windows\System32\drivers\etc\hosts`) pointing to either `localhost`, `127.0.0.1`, 
or `0.0.0.0`, depending on whichever gets the job done on your system.

With the default development configuration, this might look something like:

```
# ... system stuff above
127.0.0.1	bentov2.local
127.0.0.1	portal.bentov2.local
127.0.0.1	bentov2auth.local
# ... other stuff below
```

If you are working with cBioPortal, you will need another line:
```
# ...
127.0.0.1   cbioportal.bentov2.local
# ...
```

Editing `/etc/hosts` is **not needed** in production, since the domains should have DNS records.

Make sure these values match the values in the `.env` file and what was issued in the self-signed certificates, as 
specified in the step above.


### 4. Initialize and boot the gateway


> NOTE: `./bentoctl.bash` commands seen here aren't the only tools for operating this cluster. 
> Run `./bentoctl.bash --help` for further documentation.


```bash
# Once the certificates are ready, initialize various aspects of the cluster:
./bentoctl.bash init-all
# Which is equivalent to:

#   # Once the certificates are ready, initialize the cluster configs secrets
#   ./bentoctl.bash init-dirs
#   ./bentoctl.bash init-docker
#   ./bentoctl.bash init-secrets
#   
#   # Initialize bento_web and bento_public
#   ./bentoctl.bash init-web private
#   ./bentoctl.bash init-web public

# If you are running the bentoV2 with the use of an internal identity provider (defaults to Keycloak), 
# i.e setting BENTOV2_USE_EXTERNAL_IDP=0, run both
./bentoctl.bash run auth
./bentoctl.bash run gateway
# and
./bentoctl.bash init-auth

# then EDIT YOUR ENVIRONMENT TO INCLUDE THE RESULTING CLIENT SECRET VIA CLIENT_SECRET=... ! after this,
# restart the gateway:
./bentoctl.bash restart gateway
```

**If using an external identity provider**, only start the cluster's gateway
after setting `CLIENT_SECRET` in your local environment file:

```bash
./bentoctl.bash run gateway
```


#### Note on Keycloak

This last step boots and configures the local OIDC provider (**Keycloak**) container and reconfigures the gateway to 
utilize new variables generated during the OIDC configuration.

> NOTE: by default, the `gateway` service *does* need to be running for this to work as the configuration will pass via 
> the URL set in the `.env` file which points to the gateway.
>
> If you do not plan to use the built-in OIDC provider, you will have to handle auth configuration manually.

The `CLIENT_SECRET` environment variable must be set using the value provided by Keycloak. If `bentoctl` was used, 
this should have been printed to the console when `init-auth` was run.

##### If you need to retrieve `CLIENT_SECRET` manually:

Using a browser, connect to the `auth` endpoint (by default `https://bentov2auth.local`) and use the admin 
credentials from the env file. Once within Keycloak interface, navigate to the *Configure/Clients* menu. Select 
`local_bentov2` in the list of clients and switch to the *Credentials* tab. Copy the secret from
there and paste it in your .env file.

![Keycloak UI: get client secret](docs/img/keycloak_client_secret.png)


### 5. *Production only:* set up translations for Bento-Public

Now that Bento Public has been initialized by either `./bentoctl.bash init-all` or `./bentoctl.bash init-web public`,
adjust the default translation set as necessary:

```js
// lib/public/translations/<en|fr>.json

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


### 6. Start the cluster

```bash
./bentoctl.bash run all
# or
./bentoctl.bash run
# (these are synonymous)
```

to run all Bento services.


#### Stopping and cleaning the cluster

Run

```bash
./bentoctl.bash stop all
```

to shut down the whole cluster.

To remove the Docker containers, run the following:

```bash
./bentoctl.bash clean all
```

> NOTE: application data does persist after cleaning 
> (depending on data path, e.g., `./data/[auth, drs, katsu]/...` directories)


### 7. Set up Gohan's gene catalogue (*optional*; required for gene querying support)

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

### Accessing containers with `bentoctl`

To start a shell session within a particular container, use the following command (here, `web` is used as an example):

```bash
./bentoctl.bash shell web
```

Optionally, the shell to run can be specified via `--shell /bin/bash` or `--shell /bin/sh`.


### Working on `web` (as an example)

To work on the `bento_web` repository within a BentoV2 environment, run the following command:

```bash
./bentoctl.bash work-on web
```

This will clone the `bento_web` repository into `./repos/web` if necessary, and start it in development mode,
which means on-the-fly Webpack building will be available.

⚠️ **Warning for local development** ⚠️

In local mode, be sure to navigate to the cloned repository `./repos/web/` (or any other service repo you want to work 
on locally), and checkout on the PR branch from which the dev Docker image was built. 

You can find the default image tag variables in `./etc/bento.env` and overwrite them in `local.env`, look for the 
pattern `BENTOV2_(service name)_VERSION`. 

The version tags correspond to the PR **number** (not its name), e.g. `BENTOV2_WEB_VERSION=pr-216` indicates that the 
image was built from PR #216 in bento_web.

#### Migrating the repository from v2.10 and prior

Move your local `bento_web` project to the `./repos` directory (named `web`):

```bash
mv ./path/to/my/bentoweb ./repos/web
```

You will then have `repos/web` available for the `./bentoctl.bash work-on web` command, which will spin up the 
`web` container tethered to your local directory with a Docker volume. Internally, 
`npm run watch` is executed so changes made locally will be reflected in the container.

> Note: if you get stuck on an NGINX `500 Internal Service Error`, give it another minute to spin up. If it persists, 
> run `./bentoctl.bash shell web` to access the container, and then run `npm run watch` manually.



<br />

## Testing

First, head on over to https://github.com/mozilla/geckodriver/releases and download the latest geckodriver.

Decompress the .tar.gz or .zip and move the `geckodriver` over to the `./etc/tests/integration` directory. After that, 
simply run
```
make run-tests
```

This will run a set of both unit `(TODO)` and integration tests. See the `Makefile` for more details



<br />

## Troubleshooting

### Accessing service logs

The logs for each individual service can be accessed by running

```
./bentoctl.bash logs <service>
```

for example:

```
./bentoctl.bash logs katsu
```

If you want to follow the logs live, append the `-f` option. If no service is specified, logs
from all running Docker containers will be shown.

### Restarting all services

To restart all services

```
./bentoctl.bash stop all
./bentoctl.bash run all
```

One can also start services individually, e.g.:

```
./bentoctl.bash run drs
```

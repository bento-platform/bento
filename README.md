# bentoV2
This repo is intended to be the next generation of Bento deployments.
Originating from the blueprints in the repo `chord_singularity`, `bentoV2` aims to be much more modular than it's counterpart, built with docker instead of Singularity.

## Makefile
The Makefile contains a set of tools to faciliate testing, development, and deployments. Ranging from `build`, `run`, and `clean` commands, operators may have an easier time using these rather than fiddling with raw `docker` and `docker-compose` commands.

## Requirements
- Docker >= 19.03.8
- Docker Compose >=1.29.0

<br/>

# Installation
## Create self-signed TLS certificates
First, setup your local bentoV2 and authorization hostnames (something like `bentov2.local`, and `bentov2auth.local`) in the `.env` file. You can then create the corresponding TLS certificates for local development with the following steps;

From the project root, run 
```
mkdir -p ./lib/gateway/certs/dev/auth
```

Then run 
```
openssl req -newkey rsa:2048 -nodes \
    -keyout ./lib/gateway/certs/dev/privkey1.key -x509 \
    -days 365 -out ./lib/gateway/certs/dev/fullchain1.crt
```
to create the bentov2 cert for `bentov2.local` (or whatever other domain you use)

Next, if you're running an OIDC provider container locally <b>(default is currently Keycloak)</b>, run 
```
openssl req -newkey rsa:2048 -nodes \
    -keyout ./lib/gateway/certs/dev/auth/auth_privkey1.key -x509 \
    -days 365 \
    -out ./lib/gateway/certs/dev/auth/auth_fullchain1.crt
```
to create the bentov2 cert for `bentov2auth.local` (or whatever other domain you use)
> Note:
> 
> **(ensure the domain names in `.env` and the cert Common Names match up)**
>
> TODO: parameterize these directories in `.env`

Finally, ensure that the local domain name is set in the machines `hosts` file (for Linux users, this is likely `/etc/hosts`, and in Windows, `C:\Windows\System32\drivers\etc\hosts`) pointing to either `localhost`, `127.0.0.1`, or `0.0.0.0`, depending on whichever gets the job done on your system.

<br/>

## Boot the gateway controller (<b>NGINX</b> by default)

> Note: `make` commands seen here aren't the only tools for operating this cluster. See the `Makefile` for further documentation.

<br/>

Once the certificates are ready, 

<br/>

Initialize the cluster configs secrets

```
make init-chord-services
make init-dirs
make init-docker
make docker-secrets
```
and open up the cluster's gateway with
```
make run-gateway
```

Next, run

```
make auth-setup
```

to boot and configure the local OIDC provider (<b>Keycloak</b>) container and reconfigure the gateway to utilize new variables generated during the OIDC configuration.

> Note: by <b>default</b>, the `gateway` service *does* need to be running for this to work as the configuration will pass via the URL set in the `.env` file which points to the gateway. 
>
> If you do not plan to use the built-in OIDC provider, you will have to handle the `auth_config` and `instance_config` manually (see `./etc/auth/..` and `./etc/scripts/..` for further details)

<br />

## Start the cluster
Next, run

```
make build-common-base
make run-all
```

to trigger the series of initial build events (using `docker-compose`) for the rest of bento's supporting microservices, and then run them.

<br />

## Stop the cluster
Run

```
make stop-all
```

to shut down the whole cluster,

```
make clean-all
```
to remove the docker containers and images from disk,

> \* Note: application data does persist (see `./lib/[auth, drs, katsu]/data` directories, for example)


# bentoV2
This repo is intended to be the next generation of Bento deployments.
Originating from the blueprints in the repo `chord_singularity`, `bentoV2` aims to be much more modular than it's counterpart, built with docker instead of Singularity.

## Makefile
The Makefile contains a set of tools to faciliate testing, development, and deployments. Ranging from `build`, `run`, and `clean` commands, operators may have an easier time using these rather than fiddling with raw `docker` and `docker-compose` commands.

## Requirements
- Docker >= 19.03.8
- Docker Compose >=1.25.0

<br/>

# Installation
## Create self-signed TLS certificates
After setting both the bentoV2 and its authorization URLs in the project `.env` file, you can create the corresponding TLS certificates for local development with the following steps;

From the project root, run 
```
mkdir -p ./lib/gateway/certs/dev/auth
```

Then run 
```
openssl req -newkey rsa:2048 -nodes -keyout ./lib/gateway/certs/dev/privkey1.key -x509 -days 365 -out ./lib/gateway/certs/dev/fullchain1.crt
```
to create the bentov2 certs **(ensure the domain names in `.env` and the certs match up)**

Next, if you're running an OIDC provider container locally <b>(default is currently Keycloak)</b>, run 
```
openssl req -newkey rsa:2048 -nodes \
    -keyout ./lib/gateway/certs/dev/auth/auth_privkey1.key -x509 \
    -days 365 \
    -out ./lib/gateway/certs/dev/auth/auth_fullchain1.crt
```

> TODO: parameterize these directories in `.env`

<br/>


## Boot the gateway controller <b>(NGINX by default)</b>

Once the certificates are ready, run 

```
make run-gateway
```

to kickstart the cluster. Next, if necessary, run

```
make auth-setup
```

to boot and configure the local OIDC provider <b>(Keycloak)</b> container.

> Note: by <b>default</b>, the `gateway` service needs to be running for this to work as the configuration will pass via the URL set in the `.env` file.

<br/>

Initialize the cluster configs secrets

```
make init-chord-services
make init-dirs
make docker-secrets
```

## Start the cluster
Next, run 

```
make run
```

to trigger the series of build events using `docker-compose`.
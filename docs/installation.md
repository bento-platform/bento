# Installation

## 1. Set up `bentoctl`

See the following guide: [`bentoctl`: the Bento deployment command line management tool](./bentoctl.md)

Before running any installation steps, make sure you've set up `bentoctl` and have activated its 
virtual environment.


## 2. Provision configuration files

### Instance-specific environment variable file: `local.env`

Depending on your use, development or deployment, you will need to copy the right template file
to `local.env` in the root of the `bentoV2` folder:

```bash
# Dev
cp ./etc/bento_dev.env local.env

# Deployment
cp ./etc/bento_deploy.env local.env
```

Then, modify the values as seen; depending on if you're using the instance for development or deployment.


#### Development example

The below is an example of a completed development configuration:

```bash
# in local.env:

MODE=dev

# Gateway/domains -----------------------------------------------------
BENTOV2_DOMAIN=bentov2.local
BENTOV2_PORTAL_DOMAIN=portal.${BENTOV2_DOMAIN}
BENTOV2_AUTH_DOMAIN=bentov2auth.local
# Unused if cBioPortal is disabled:
BENTOV2_CBIOPORTAL_DOMAIN=cbioportal.${BENTOV2_DOMAIN}
# ---------------------------------------------------------------------

# Feature switches ----------------------------------------------------
BENTOV2_USE_EXTERNAL_IDP=0
BENTOV2_USE_BENTO_PUBLIC=1
BENTOV2_PRIVATE_MODE=false

BENTO_CBIOPORTAL_ENABLED=false
# ---------------------------------------------------------------------

# set this to a data storage location, optionally within the repo itself, like: /path-to-my-bentov2-repo/data
BENTOV2_ROOT_DATA_DIR=./data

# Auth ----------------------------------------------------------------
#  - Session secret should be set to a unique secure value.
#    this adds security and allows sessions to exist across gateway restarts.
#     - Empty by default, to be filled by local.env
#  - IMPORTANT: set before starting gateway
BENTOV2_SESSION_SECRET=my-very-secret-session-secret  # !!! ADD SOMETHING MORE SECURE !!!

#  - Set auth DB password if using a local IDP
BENTO_AUTH_DB_PASSWORD=some-secure-password

BENTOV2_AUTH_ADMIN_USER=admin
BENTOV2_AUTH_ADMIN_PASSWORD=admin  # !!! obviously for dev only !!!

BENTOV2_AUTH_TEST_USER=user
BENTOV2_AUTH_TEST_PASSWORD=user  # !!! obviously for dev only !!!

#  - WES Client ID/secret; client within BENTOV2_AUTH_REALM
BENTO_WES_CLIENT_ID=wes
BENTO_WES_CLIENT_SECRET=
# --------------------------------------------------------------------

# Gohan
BENTOV2_GOHAN_ES_PASSWORD=devpassword567

# Katsu
BENTOV2_KATSU_DB_PASSWORD=devpassword123
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

### `bento_public` configuration

Then, copy the `bento_public` configuration file to its correct location for use by Katsu, 
Bento's clinical/phenotypic metadata service:

```bash
# public service configuration file. Required if BENTOV2_USE_BENTO_PUBLIC flag is set to `1`
# See Katsu documentation for more information about the specifications
cp ./etc/katsu.config.example.json ./lib/katsu/config.json
```


## 3. *Development only:* create self-signed TLS certificates 

First, set up your local Bento and Keycloak hostnames (something like `bentov2.local`, `portal.bentov2.local`, and 
`bentov2auth.local`) in the `.env` file. You can then create the corresponding TLS certificates for local development.

Setting up the certificates with `bentoctl` can be done in a single command.
From the project root, run

```bash
./bentoctl.bash init-certs
```

> **NOTE:** This command will skip all certificate generation if it detects previously created files. 
> To force an override, simply add the option `--force` / `-f`.

After creating the three certificates, it is worth ensuring your browser has security exceptions for these
certificates and domains. Navigate to each of the three domains mentioned above and add security exceptions
to ensure cross-origin requests will occur correctly.


## 4. *Development only:* Hosts file configuration

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


## 5. Initialize and boot the gateway


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
```

**If using an external identity provider**, only start the cluster's gateway
after setting `CLIENT_SECRET` in your local environment file:

```bash
./bentoctl.bash run gateway
```


### Note on Keycloak

This last step boots and configures the local OIDC provider (**Keycloak**) container and reconfigures the gateway to 
utilize new variables generated during the OIDC configuration.

> NOTE: by default, the `gateway` service *does* need to be running for this to work as the configuration will pass via 
> the URL set in the `.env` file which points to the gateway.
>
> If you do not plan to use the built-in OIDC provider, you will have to handle auth configuration manually.


## 6. Configure permissions

### a. Create superuser permissions in the new Bento authorization service

First, run the authorization service and then open a shell into the container:

```bash
./bentoctl.bash run authz
./bentoctl.bash shell authz
```

Then, run the following command for each user ID you wish to assign superuser permissions to:

```bash
bento_authz assign-all-to-user iss sub
```

Where `iss` is the issuer (for example, `https://bentov2auth.local/realms/bentov2`) and `sub` is the user (subject) ID,
which in Keycloak should be a UUID.

### b. Create grants for the Workflow Execution Service (WES) OAuth2 client

Run the following commands to set up authorization for the WES client:

```bash
# This grant is a temporary hack to get permissions working for v12/v13. In the future, it should be removed.
bento_authz create grant \
  '{"iss": "ISSUER_HERE", "client": "wes"}' \
  '{"everything": true}' \
  'view:private_portal'

# This grant gives permission to access and ingest data into all projects
bento_authz create grant \
  '{"iss": "ISSUER_HERE", "client": "wes"}' \
  '{"everything": true}' \
  'query:data' 'ingest:data'
```

### c. *Optional step:* Assign portal access to all users in the instance realm

We added a special permission, `view:private_portal`, to Bento v12/v13 in order to carry forward the current
'legacy' authorization behaviour for one more major version. This permission currently behaves as a super-permission,
allowing all actions within the private portal. **However,** in the future, this permission will do almost *nothing.*

To carry forward legacy behaviour of all users in the instance realm being able to do everything, run the following
command in the authorization service container:

```bash
# Create the grant
bento_authz create grant \
  '{"iss": "ISSUER_HERE", "client": "WEB_CLIENT_ID_HERE"}' \
  '{"everything": true}' \
  'view:private_portal'
```

Where `WEB_CLIENT_ID_HERE` is the OAuth2 client the web portal uses, i.e., the 
value in the `BENTOV2_AUTH_CLIENT_ID` environment variable. On local instances, 
this is set to `local_bentov2` by default.


## 7. *Production only:* set up translations for Bento-Public

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


## 8. Start the cluster

```bash
./bentoctl.bash run all
# or
./bentoctl.bash run
# (these are synonymous)
```

to run all Bento services.


### Stopping and cleaning the cluster

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


## 9. Set up Gohan's gene catalogue (*optional*; required for gene querying support)

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

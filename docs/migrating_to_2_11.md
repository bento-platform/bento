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

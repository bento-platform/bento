# Bento Release Checklist

## Individual Services

* Make sure `bento_lib` accepts the latest (or at least a secure version) of all web frameworks (FastAPI, Flask, and 
  Django), and release a new semver-compliant version of `bento_lib`. 
* Update `bento_lib` in all services unless there is a good reason not to (which happens!)
* Make sure all services have up-to-date dependency security patches and base images (to ensure the underlying container
  operating systems are patched.)
* If no other changes are present, release these changes as a PATCH release. 


## Bento Repository (*this one!*)

### Updating Services

* Make sure all services in [`etc/bento.env`](../etc/bento.env) are updated.

### Updating Configuration

* If you've added any new environment variable configuration, remember to add it to the following file(s) as needed: 
  * `etc/default_config.env` - base config/secrets/etc. overrided by the `local.env` file
  * `etc/bento.env` - variables that are not changed by instance/by user
  * `etc/bento_deploy.env` - example `local.env` file for production deployments
  * `etc/bento_dev.env` - example `local.env` file for development instances
  * any Docker Compose `.yaml` files in `lib/`

### Writing a Migration Guide

* Create a new migration guide in [`docs/`](.), detailing all steps needed to update instances for the release, and any
  other noteworthy changes node administrators should know about.
* Link to the migration guide from [`README.md`](../README.md).


## Deploying to Staging

* Before finalizing the release, deploy the "release candidate" / "working copy" version of the release branch on the
  Bento Staging node and test that all tickets pass their acceptance criteria.


## Tagging the Version

* When all tickets are ready to release, merge the release branch into the default branch of this repository.


## Deployment

* First, make sure any given deployment is on the latest version of Bento before this one before continuing.
* If the instance has a staging version, make sure everything works well there before rolling it out to the main 
  instance.
* Follow the migration guide (mentioned above) when deploying.

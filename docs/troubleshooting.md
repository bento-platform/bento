# Troubleshooting Bento

Common issues can arise when developing on Bento, or when deploying it to a server. 
This document lists known pitfalls that can be encountered and their solutions.


## Basics

Useful commands used to diagnose and fix issues.

### Accessing service logs

When a service is not behaving as expected, checking the service's logs for errors and warnings is always a good reflex.

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

In some situations you may want to stop all services, perform environment changes or maintenance operations, then start all services again.
To restart all services quickly

```shell
# Stop all services
./bentoctl.bash stop all

# Perform maintenance operations on host (optional)
git pull
./bentoctl.bash pull

# Start all services
./bentoctl.bash run all
```

One can also start and stop services individually, e.g.:

```shell
./bentoctl.bash run drs
./bentoctl.bash stop katsu
```


## Docker

Issues related to Docker.

### Mounted files

***How to notice:*** A service is experiencing issues and logs reveal it is trying to load a directory as a file.

Confirguration files for some services are provided to the container as file mounts, 
such as Katsu's `config.json` file.

If the docker-compose of a service has a file mount that does not exsit on the host (e.g. `lib/katsu/config.json`), 
Docker's default behaviour is to create a directory with said path.

This can lead the service to experience errors when trying to load the directory as a file.
To fix this:
1.  Stop the service with: `bentoctl stop <service name>`
2.  Make sure the expected file exists in the host's path.
3.  Start the service with: `bentoctl run <service name>`
4.  Check the logs for errors: `bentoctl logs <service name>`

### Permission issues in volumes
How to notice: Services are experiencing errors because they are unable to read the contents of their volumes.

This is often a permission being denied because the host paths of volumes are owned by `root`, verify with: 

```shell
ls -la ${BENTO_SLOW_DATA_DIR} # For "slow" data volumes
ls -la ${BENTO_FAST_DATA_DIR} # For "fast" data volumes
ls -la lib/ # For configuration volumes
```

Find the faulty path(s) and the services they are associated with.
Stop any service that is using said path(s), then change the ownership with:

```shell
sudo chown -R <username>:<username> <path>
```

Where `username` is your username.

Finally, start the stopped services: `bentoctl run <service>`


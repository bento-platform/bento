# Migrating to Bento v13

The following is a migration guide for going from Bento v12.x to Bento v13.

Some notes on **breaking** changes in this version:

* WES now requires its own OAuth2 client ID/secret for making authorized requests
* The concept of 'tables' has been removed from Bento; some data re-ingestion will be required


## 1. Delete variant data

Since the concept of 'tables' has been removed from Bento v13; 
data re-ingestion will be required for all variant data via the UI.

It would be wise to first remove the Gohan Elasticsearch volume to
clean up old variant data on the VM.


## 2. Pull latest Docker containers and stop Bento

The following commands:

* Stop the cluster
* Pull the latest images


```bash
./bentoctl.bash stop
./bentoctl.bash pull
```


## 3. Create a WES client with secret

WES now requires its own OAuth2 client ID/secret for making authorized requests
to various services within WDL workflows. 

To create this client, with secret, re-run the `init-auth` subcommand of `bentoctl`:

```bash
./bentoctl.bash init-auth
```

This will print the new client secret to the console; set it in your `local.env` file
similar to the following:

```
# ...
BENTO_WES_CLIENT_SECRET=my-wes-client-secret-here
# ...
```

The default client ID here is `wes`, as set in `./etc/default_config.env`.


## 4. Restart Bento

Now that we have the environment configured correctly, we can restart the 
Bento instance:

```bash
./bentoctl.bash run
```


## 5. Create a grant for the WES OAuth2 client

The next step is to create a grant in `authz` which gives WES the ability
to ingest data into all projects/endpoints/etc. in the node:

```bash
./bentoctl.bash shell authz  # enter into an authz container session to create the grant

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


## 6. Delete and re-ingest Gohan variant data

Since you should have deleted all variant data in step 1, now is the time to
re-ingest VCFs into Goahn.
